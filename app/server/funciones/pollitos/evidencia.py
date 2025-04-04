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
def procesar_historico(mensaje, user_evento, id_objeto, tipo_objeto):
    """
    Crea un registro histórico para una acción realizada sobre un objeto.
    
    Args:
        mensaje: Descripción de la acción realizada
        user_evento: ID del usuario que realizó la acción
        id_objeto: ID del objeto afectado
        tipo_objeto: Tipo de objeto (ej: "evidencia")
    
    Returns:
        dict: Datos del registro histórico
    """
    historico = {
        "mensaje": mensaje,
        "user_evento": user_evento,
        "id_objeto": id_objeto,
        "tipo_objeto": tipo_objeto,
        "fecha_evento": datetime.now()
    }
    return historico

def procesar_log(evento, usuario, campo):
    """
    Crea un registro de log para una acción.
    
    Args:
        evento: Tipo de evento
        usuario: ID del usuario que realizó la acción
        campo: Campo o identificador relacionado con la acción
    
    Returns:
        dict: Datos del registro de log
    """
    mensaje2 = str(evento) + " : " + str(campo) + " , hecho por : " + str(usuario)
    agrupado = {"evento": mensaje2, "fecha": datetime.now()}
    return agrupado

def filtrar_no_none(data: dict) -> dict:
    """
    Filtra un diccionario eliminando las claves con valores None.
    
    Args:
        data: Diccionario a filtrar
    
    Returns:
        dict: Diccionario filtrado
    """
    return {k: v for k, v in data.items() if v is not None}

def convertir_fecha_inicio(fecha_str):
    """
    Convierte una cadena de fecha al formato de fecha de inicio.
    
    Args:
        fecha_str: Cadena de fecha en formato "dd-mm-yyyy_HH-MM-SS"
    
    Returns:
        datetime: Fecha convertida o fecha por defecto (30 días atrás)
    """
    try:
        return datetime.strptime(fecha_str, "%d-%m-%Y_%H-%M-%S")
    except ValueError:
        return datetime.now() - timedelta(days=30)

def convertir_fecha_fin(fecha_str):
    """
    Convierte una cadena de fecha al formato de fecha de fin.
    
    Args:
        fecha_str: Cadena de fecha en formato "dd-mm-yyyy_HH-MM-SS"
    
    Returns:
        datetime: Fecha convertida o fecha actual
    """
    try:
        return datetime.strptime(fecha_str, "%d-%m-%Y_%H-%M-%S")
    except ValueError:
        return datetime.now()

async def guardar_evidencia(evidencia_data: dict) -> dict:
    """
    Guarda una evidencia en la base de datos.
    
    Args:
        evidencia_data: Datos de la evidencia a guardar
    
    Returns:
        dict: Datos de la evidencia guardada o mensaje de error
    """
    # Verificar si ya existe una evidencia con el mismo título para la misma entidad
    coincidencia_dato = await evidencia_collection.find_one({
        "titulo_evidencia": evidencia_data['titulo_evidencia'],
        "tipo_entidad": evidencia_data['tipo_entidad'],
        "entidad_id": evidencia_data['entidad_id'],
        "estado_evidencia": 1
    }, {"_id": 0})
    
    proyecto_ok = "FAIL"
    id_value = evidencia_data.get('id_evidencia', 0)
    
    # Asegurar que estado_evidencia esté presente
    if 'estado_evidencia' not in evidencia_data:
        evidencia_data['estado_evidencia'] = 1
    
    if id_value == 0:
        # Crear nueva evidencia
        if coincidencia_dato:
            return "DUPLICADO"
        
        # Establecer fecha si no se proporciona
        if not evidencia_data.get('fecha_evidencia'):
            evidencia_data['fecha_evidencia'] = datetime.now()
        
        # Validar que haya al menos un tipo de evidencia (foto o archivo)
        if not evidencia_data.get('link_evidencia') and not evidencia_data.get('archivo_evidencia'):
            return "ERROR: Se requiere al menos una foto o un archivo"
        
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
            evidencia_data['id_evidencia'],
            "evidencia"
        )
        await h_evidencia_collection.insert_one(evidencia_historico)
        
        return proyecto_ok
    else:
        # Actualizar evidencia existente
        evidencia_data['updated_at'] = datetime.now()
        
        # Verificar si existe la evidencia a actualizar
        evidencia_existente = await evidencia_collection.find_one({
            "id_evidencia": id_value,
            "estado_evidencia": 1
        })
        
        if not evidencia_existente:
            return "NO EXISTE"
        
        # Validar que haya al menos un tipo de evidencia (foto o archivo)
        # Si ya existe un link o archivo en la BD, no requerimos uno nuevo
        if (not evidencia_data.get('link_evidencia') and not evidencia_data.get('archivo_evidencia') and
            not evidencia_existente.get('link_evidencia') and not evidencia_existente.get('archivo_evidencia')):
            return "ERROR: Se requiere al menos una foto o un archivo"
        
        # Filtrar campos None para no sobrescribir datos existentes
        datos_actualizacion = filtrar_no_none(evidencia_data)
        
        # Actualizar en la base de datos
        await evidencia_collection.update_one(
            {"id_evidencia": id_value},
            {"$set": datos_actualizacion}
        )
        
        # Obtener evidencia actualizada
        proyecto_ok = await evidencia_collection.find_one(
            {"id_evidencia": id_value},
            {"_id": 0, "id_evidencia": 1, "titulo_evidencia": 1}
        )
        
        # Guardar en histórico
        evidencia_historico = procesar_historico(
            f"EVIDENCIA ACTUALIZADA PARA {evidencia_data['tipo_entidad'].upper()}",
            evidencia_data['user_m'],
            evidencia_data['id_evidencia'],
            "evidencia"
        )
        await h_evidencia_collection.insert_one(evidencia_historico)
        
        return proyecto_ok

async def listar_evidencias(evidencia_data: dict) -> dict:
    """
    Lista las evidencias según los criterios proporcionados.
    
    Args:
        evidencia_data: Criterios de búsqueda
    
    Returns:
        dict: Resultados de la búsqueda
    """
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
    ).sort("created_at", -1):
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
    """
    Ver una evidencia específica.
    
    Args:
        evidencia_data: Datos para identificar la evidencia
    
    Returns:
        dict: Datos de la evidencia o mensaje de error
    """
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
    """
    Marca una evidencia como eliminada (estado_evidencia = 0).
    
    Args:
        evidencia_data: Datos para identificar la evidencia
    
    Returns:
        str: Resultado de la operación
    """
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
            
            # Guardar en histórico
            evidencia_historico = procesar_historico(
                "EVIDENCIA ELIMINADA",
                evidencia_data['id_usuario'],
                evidencia_data['especifico'],
                "evidencia"
            )
            await h_evidencia_collection.insert_one(evidencia_historico)
            
            return "OK"
        else:
            return "FAIL"
    else:
        return "SIN_ESPECIFICO"

async def reestablecer_evidencia(evidencia_data: dict) -> str:
    """
    Reestablece una evidencia (estado_evidencia = 1).
    
    Args:
        evidencia_data: Datos para identificar la evidencia
    
    Returns:
        str: Resultado de la operación
    """
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
            
            # Guardar en histórico
            evidencia_historico = procesar_historico(
                "EVIDENCIA REESTABLECIDA",
                evidencia_data['id_usuario'],
                evidencia_data['especifico'],
                "evidencia"
            )
            await h_evidencia_collection.insert_one(evidencia_historico)
            
            return "OK"
        else:
            return "FAIL"
    else:
        return "SIN_ESPECIFICO"








