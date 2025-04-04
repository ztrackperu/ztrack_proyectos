import hashlib
import os
from datetime import datetime, timedelta
from server.database import collection
from bson.objectid import ObjectId

# Colecciones
evidencia_collection = collection("evidencia")
h_evidencia_collection = collection("h_evidencia")
log_general_collection = collection("log_general")
ids_collection = collection("ids_proyectos")
fecha_actual = datetime.now()

# Funciones auxiliares
def procesar_historico(mensaje, user_c, objeto):
    filter_proyecto = {k: v for k, v in objeto.items() if k not in ['user_c', 'user_m', 'updated_at', 'created_at']}
    filter_proyecto['mensaje'] = mensaje
    filter_proyecto['user_evento'] = user_c
    filter_proyecto['fecha_evento'] = datetime.now()
    return filter_proyecto

def procesar_log(evento, usuario, campo):
    mensaje2 = str(evento) + " : " + str(campo) + " , hecho por : " + str(usuario)
    agrupado = {"evento": mensaje2, "fecha": datetime.now()}
    return agrupado

def filtrar_no_none(data: dict) -> dict:
    return {k: v for k, v in data.items() if v is not None}

def convertir_fecha_inicio(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d-%m-%Y_%H-%M-%S")
    except ValueError:
        return datetime.now() - timedelta(days=30)

def convertir_fecha_fin(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d-%m-%Y_%H-%M-%S")
    except ValueError:
        return datetime.now()

async def guardar_evidencia(evidencia_data: dict) -> dict:
    """Guarda una evidencia en la base de datos"""
    # Verificar si ya existe una evidencia con el mismo título para la misma entidad
    coincidencia_dato = await evidencia_collection.find_one({
        "titulo_evidencia": evidencia_data['titulo_evidencia'],
        "tipo_entidad": evidencia_data['tipo_entidad'],
        "entidad_id": evidencia_data['entidad_id'],
        "estado_evidencia": 1
    }, {"_id": 0})
    
    proyecto_ok = "FAIL"
    id_value = evidencia_data.get('id_evidencia', 0)
    
    if id_value == 0:
        # Crear nueva evidencia
        if coincidencia_dato:
            return "DUPLICADO"
        
        # Establecer fecha si no se proporciona
        if not evidencia_data.get('fecha_evidencia'):
            evidencia_data['fecha_evidencia'] = datetime.now()
        
        # Obtener nuevo ID
        ids_proyectos = await ids_collection.find_one({"id_evidencia": {"$exists": True}})
        evidencia_data['created_at'] = datetime.now()
        evidencia_data['id_evidencia'] = ids_proyectos['id_evidencia'] + 1 if ids_proyectos else 1
        
        # Guardar en la base de datos
        guardar_evidencia = await evidencia_collection.insert_one(evidencia_data)
        
        # Actualizar contador de IDs
        s_ids = {"id_evidencia": evidencia_data['id_evidencia'], "fecha": datetime.now()}
        if ids_proyectos:
            await ids_collection.update_one({"_id": ids_proyectos['_id']}, {"$set": s_ids})
        else:
            await ids_collection.insert_one(s_ids)
        
        # Obtener evidencia guardada
        proyecto_ok = await evidencia_collection.find_one(
            {"_id": guardar_evidencia.inserted_id},
            {"_id": 0, "id_evidencia": 1, "titulo_evidencia": 1}
        )
        
        # Guardar en histórico
        evidencia_historico = procesar_historico(
            f"EVIDENCIA GUARDADA PARA {evidencia_data['tipo_entidad'].upper()}",
            evidencia_data['user_c'],
            evidencia_data
        )
        await h_evidencia_collection.insert_one(evidencia_historico)
        
        # Guardar en log
        log = procesar_log(
            f"EVIDENCIA GUARDADA PARA {evidencia_data['tipo_entidad'].upper()}",
            evidencia_data['user_c'],
            evidencia_data['titulo_evidencia']
        )
        await log_general_collection.insert_one(log)
    else:
        # Actualizar evidencia existente
        if coincidencia_dato is None or coincidencia_dato['id_evidencia'] == id_value:
            evidencia_data['updated_at'] = datetime.now()
            evidencia_data['user_m'] = evidencia_data['user_c']
            
            # Filtrar campos para actualización
            filter_evidencia = {k: v for k, v in evidencia_data.items() if k not in ['id_evidencia', 'user_c', 'created_at']}
            filter_evidencia2 = filtrar_no_none(filter_evidencia)
            
            # Actualizar en la base de datos
            await evidencia_collection.update_one(
                {"id_evidencia": evidencia_data['id_evidencia'], "estado_evidencia": 1},
                {"$set": filter_evidencia2}
            )
            
            # Guardar en histórico
            evidencia_historico = procesar_historico(
                f"EVIDENCIA EDITADA PARA {evidencia_data['tipo_entidad'].upper()}",
                evidencia_data['user_m'],
                evidencia_data
            )
            await h_evidencia_collection.insert_one(evidencia_historico)
            
            # Guardar en log
            log = procesar_log(
                f"EVIDENCIA EDITADA PARA {evidencia_data['tipo_entidad'].upper()}",
                evidencia_data['user_m'],
                id_value
            )
            await log_general_collection.insert_one(log)
            
            proyecto_ok = {"id_evidencia": evidencia_data['id_evidencia'], "titulo_evidencia": evidencia_data['titulo_evidencia']}
        else:
            proyecto_ok = "DUPLICADO"
    
    return proyecto_ok

async def listar_evidencias(evidencia_data: dict) -> dict:
    """Lista las evidencias según los criterios proporcionados"""
    notificacions = []
    
    fecha_inicio = convertir_fecha_inicio(evidencia_data['fecha_inicio']) if evidencia_data.get('fecha_inicio') else datetime.now() - timedelta(days=30)
    fecha_fin = convertir_fecha_fin(evidencia_data['fecha_fin']) if evidencia_data.get('fecha_fin') else datetime.now()
    
    # Construir la consulta según los parámetros
    if evidencia_data['id_usuario'] == 1:
        query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin}}
    else:
        query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin}, "estado_evidencia": 1, "user_c": evidencia_data['id_usuario']}
    
    # Filtrar por tipo_entidad si se proporciona
    if evidencia_data.get('tipo_entidad'):
        query["tipo_entidad"] = evidencia_data['tipo_entidad']
    
    # Filtrar por entidad_id si se proporciona
    if evidencia_data.get('entidad_id'):
        query["entidad_id"] = evidencia_data['entidad_id']
    
    # Ejecutar la consulta
    async for notificacion in evidencia_collection.find(
        query,
        {"_id": 0}
    ).sort({"created_at": -1}):
        notificacions.append(notificacion)
    
    res = {"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin, "resultado": notificacions}
    
    # Guardar en log
    log = procesar_log(
        f"LISTADO DE EVIDENCIAS",
        evidencia_data['id_usuario'],
        evidencia_data.get('tipo_entidad', 'TODAS')
    )
    await log_general_collection.insert_one(log)
    
    return res

async def ver_evidencia(evidencia_data: dict) -> dict:
    """Ver una evidencia específica"""
    if evidencia_data['especifico']:
        # Realizar secuencia para ver información específica
        especifico = await evidencia_collection.find_one(
            {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 1},
            {"_id": 0}
        )
        
        # Guardar en Log
        log = procesar_log(
            "Se solicitó info de Evidencia: ",
            evidencia_data['id_usuario'],
            evidencia_data['especifico']
        )
        await log_general_collection.insert_one(log)
        
        return especifico
    else:
        return "SIN_ESPECIFICO"

async def eliminar_evidencia(evidencia_data: dict) -> str:
    """Marca una evidencia como eliminada (estado_evidencia = 0)"""
    if evidencia_data.get('especifico'):
        # Cambiar estado a 0
        objeto = {
            "estado_evidencia": 0,
            "user_m": evidencia_data['id_usuario'],
            "updated_at": datetime.now()
        }
        
        # Verificar que la evidencia exista
        evidencia = await evidencia_collection.find_one(
            {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 1},
            {"_id": 0, "titulo_evidencia": 1}
        )
        
        if evidencia:
            # Actualizar estado
            await evidencia_collection.update_one(
                {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 1},
                {"$set": objeto}
            )
            
            # Guardar en log
            log = procesar_log(
                "EVIDENCIA ELIMINADA: ",
                evidencia_data['id_usuario'],
                evidencia_data['especifico']
            )
            await log_general_collection.insert_one(log)
            
            return "OK"
        else:
            return "FAIL"
    else:
        return "SIN_ESPECIFICO"

async def reestablecer_evidencia(evidencia_data: dict) -> str:
    """Reestablece una evidencia (estado_evidencia = 1)"""
    if evidencia_data.get('especifico'):
        # Cambiar estado a 1
        objeto = {
            "estado_evidencia": 1,
            "user_m": evidencia_data['id_usuario'],
            "updated_at": datetime.now()
        }
        
        # Verificar que la evidencia exista
        evidencia = await evidencia_collection.find_one(
            {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 0},
            {"_id": 0, "titulo_evidencia": 1}
        )
        
        if evidencia:
            # Actualizar estado
            await evidencia_collection.update_one(
                {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 0},
                {"$set": objeto}
            )
            
            # Guardar en log
            log = procesar_log(
                "EVIDENCIA REESTABLECIDA: ",
                                evidencia_data['id_usuario'],
                evidencia_data['especifico']
            )
            await log_general_collection.insert_one(log)
            
            return "OK"
        else:
            return "FAIL"
    else:
        return "SIN_ESPECIFICO"

