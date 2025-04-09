import hashlib
import json
import os
import base64
from server.database import database_mongo, client, collection
from datetime import datetime, timedelta

# Colecciones
evidencia_collection = collection("evidencia")
log_general_collection = collection("log_general")
ids_collection = collection("ids_proyectos")
h_evidencia_collection = collection("h_evidencia")

fecha_actual = datetime.now()

# Directorio para almacenar archivos
UPLOAD_DIR = "app/server/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

async def guardar_evidencia(evidencia_data: dict) -> dict:
    """
    Guarda o actualiza una evidencia con soporte para múltiples archivos.
    
    Si id_evidencia es 0, crea una nueva evidencia.
    Si id_evidencia existe, actualiza la evidencia existente.
    
    Verifica duplicados por título y entidad relacionada.
    """
    # Extraer los archivos de evidencia_data si existen
    archivos = evidencia_data.pop('archivos', []) if 'archivos' in evidencia_data else []
    
    # Verificar si ya existe una evidencia con el mismo título para la misma entidad
    coincidencia_dato = await evidencia_collection.find_one({
        "titulo_evidencia": evidencia_data['titulo_evidencia'],
        "tipo_entidad": evidencia_data['tipo_entidad'],
        "entidad_id": evidencia_data['entidad_id'],
        "estado_evidencia": 1
    }, {"_id": 0})
    
    id_value = evidencia_data['id_evidencia'] if 'id_evidencia' in evidencia_data else 0
    
    # Procesar los archivos
    archivos_guardados = []
    if archivos:
        for archivo in archivos:
            # Generar un nombre único para el archivo
            nombre_original = archivo.get('nombre', 'archivo')
            extension = nombre_original.split('.')[-1] if '.' in nombre_original else ''
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            nombre_archivo = f"{timestamp}_{hashlib.md5(nombre_original.encode()).hexdigest()[:10]}.{extension}"
            
            # Guardar el archivo en el sistema de archivos
            ruta_completa = os.path.join(UPLOAD_DIR, nombre_archivo)
            
            # Decodificar el contenido base64 y guardarlo
            contenido = base64.b64decode(archivo.get('contenido', ''))
            with open(ruta_completa, 'wb') as f:
                f.write(contenido)
            
            # Agregar información del archivo guardado
            archivos_guardados.append({
                "nombre_original": nombre_original,
                "nombre_archivo": nombre_archivo,
                "tipo_archivo": archivo.get('tipo', ''),
                "tamano": len(contenido)
            })
    
    # Agregar la lista de archivos a evidencia_data
    if archivos_guardados:
        evidencia_data['archivos'] = archivos_guardados
    
    if id_value == 0:
        # Crear nueva evidencia
        if coincidencia_dato:
            return "DUPLICADO"
        else:
            # Obtener el siguiente ID
            ids_proyectos = await ids_collection.find_one({"id_evidencia": {"$exists": True}})
            evidencia_data['created_at'] = datetime.now()
            evidencia_data['id_evidencia'] = ids_proyectos['id_evidencia'] + 1 if ids_proyectos else 1
            
            # Asegurar que el estado sea activo (1)
            evidencia_data['estado_evidencia'] = 1
            
            # Insertar la evidencia
            guardar_evidencia = await evidencia_collection.insert_one(evidencia_data)
            
            # Actualizar el contador de IDs
            s_ids = {"id_evidencia": evidencia_data['id_evidencia'], "fecha": datetime.now()}
            procesar_ids = await ids_collection.update_one(
                {"_id": ids_proyectos['_id']},
                {"$set": s_ids}
            ) if ids_proyectos else await ids_collection.insert_one(s_ids)
            
            # Obtener la evidencia guardada
            evidencia_ok = await evidencia_collection.find_one(
                {"_id": guardar_evidencia.inserted_id},
                {"_id": 0, "id_evidencia": 1, "titulo_evidencia": 1, "estado_evidencia": 1}
            )
            
            # Guardar en histórico
            evidencia_historico = procesar_historico("EVIDENCIA GUARDADA", evidencia_data['user_c'], evidencia_data)
            guardar_evidencia_historico = await h_evidencia_collection.insert_one(evidencia_historico)
            
            # Guardar en Log
            log = procesar_log("EVIDENCIA GUARDADA", evidencia_data['user_c'], evidencia_data['titulo_evidencia'])
            guardar_log = await log_general_collection.insert_one(log)
            
            return evidencia_ok
    else:
        # Actualizar evidencia existente
        # Verificar si existe la evidencia a actualizar
        evidencia_existente = await evidencia_collection.find_one({
            "id_evidencia": id_value,
            "estado_evidencia": 1
        }, {"_id": 0})
        
        if not evidencia_existente:
            return "NO EXISTE"
        
        # Verificar si hay duplicados (excepto si es la misma evidencia)
        if coincidencia_dato and coincidencia_dato['id_evidencia'] != id_value:
            return "DUPLICADO"
        
        # Actualizar la evidencia
        evidencia_data['updated_at'] = datetime.now()
        evidencia_data['user_m'] = evidencia_data['user_c']
        
        # Si hay archivos nuevos, agregar a los existentes
        if archivos_guardados:
            archivos_existentes = evidencia_existente.get('archivos', [])
            evidencia_data['archivos'] = archivos_existentes + archivos_guardados
        
        # Filtrar campos a actualizar
        filter_evidencia = {k: v for k, v in evidencia_data.items() if k not in ['id_evidencia', 'user_c', 'created_at']}
        filter_evidencia2 = filtrar_no_none(filter_evidencia)
        
        actualizar_evidencia = await evidencia_collection.update_one(
            {"id_evidencia": evidencia_data['id_evidencia'], "estado_evidencia": 1},
            {"$set": filter_evidencia2}
        )
        
        # Guardar en el histórico
        evidencia_historico = procesar_historico("EVIDENCIA EDITADA", evidencia_data['user_m'], evidencia_data)
        guardar_evidencia_historico = await h_evidencia_collection.insert_one(evidencia_historico)
        
        # Guardar en Log
        log = procesar_log("EVIDENCIA EDITADA por ", evidencia_data['user_m'], id_value)
        guardar_log = await log_general_collection.insert_one(log)
        
        evidencia_ok = {
            "id_evidencia": evidencia_data['id_evidencia'],
            "titulo_evidencia": evidencia_data['titulo_evidencia'],
            "estado_evidencia": 1
        }
        
        return evidencia_ok

async def ver_evidencia(evidencia_data: dict) -> dict:
    """
    Obtiene los detalles de una evidencia específica.
    """
    if evidencia_data['especifico']:
        # Buscar la evidencia específica
        especifico = await evidencia_collection.find_one(
            {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 1},
            {"_id": 0}
        )
        
        if especifico:
            # Guardar en Log
            log = procesar_log(
                "Se solicitó info de Evidencia: ", 
                evidencia_data['id_usuario'], 
                evidencia_data['especifico']
            )
            guardar_log = await log_general_collection.insert_one(log)
            
            return especifico
        else:
            return None
    else:
        return None


async def listar_evidencias(evidencia_data: dict) -> dict:
    """
    Lista evidencias según los criterios de filtrado.
    Puede filtrar por tipo de entidad, entidad específica y rango de fechas.
    Incluye información sobre los archivos adjuntos.
    """
    evidencias = []
    
    # Convertir fechas
    fecha_inicio = convertir_fecha_inicio(evidencia_data['fecha_inicio']) if evidencia_data['fecha_inicio'] else datetime.now() - timedelta(days=30)
    fecha_fin = convertir_fecha_fin(evidencia_data['fecha_fin']) if evidencia_data['fecha_fin'] else datetime.now()
    
    # Construir la consulta
    query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin}}
    
    # Filtrar por estado (excepto para admin)
    if evidencia_data['id_usuario'] != 1:
        query["estado_evidencia"] = 1
    
    # Filtrar por tipo de entidad si se especifica
    if evidencia_data.get('tipo_entidad'):
        query["tipo_entidad"] = evidencia_data['tipo_entidad']
    
    # Filtrar por ID de entidad si se especifica
    if evidencia_data.get('entidad_id'):
        query["entidad_id"] = evidencia_data['entidad_id']
    
    # Ejecutar la consulta
    async for evidencia in evidencia_collection.find(
        query,
        {"_id": 0, "id_evidencia": 1, "tipo_entidad": 1, "entidad_id": 1, 
         "titulo_evidencia": 1, "link_evidencia": 1, "archivo_evidencia": 1, 
         "archivos": 1, "estado_evidencia": 1, "created_at": 1}
    ).sort({"created_at": -1}):
        evidencias.append(evidencia)
    
    res = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "resultado": evidencias
    }
    
    # Guardar en log
    log = procesar_log("LISTADO DE EVIDENCIAS POR ", evidencia_data['id_usuario'], "TODOS")
    guardar_log = await log_general_collection.insert_one(log)
    
    return res



# async def eliminar_archivo_evidencia(datos: dict) -> dict:
#     """
#     Elimina un archivo específico de una evidencia.
    
#     Args:
#         datos: Diccionario con id_evidencia, nombre_archivo e id_usuario
        
#     Returns:
#         Mensaje de éxito o error
#     """
#     if not datos.get('id_evidencia') or not datos.get('nombre_archivo'):
#         return "DATOS_INCOMPLETOS"
    
#     # Buscar la evidencia
#     evidencia = await evidencia_collection.find_one(
#         {"id_evidencia": datos['id_evidencia'], "estado_evidencia": 1},
#         {"_id": 0, "archivos": 1}
#     )
    
#     if not evidencia:
#         return "EVIDENCIA_NO_ENCONTRADA"
    
#     # Buscar el archivo en la lista de archivos
#     archivos = evidencia.get('archivos', [])
#     archivo_encontrado = False
#     nuevos_archivos = []
    
#     for archivo in archivos:
#         if archivo.get('nombre_archivo') == datos['nombre_archivo']:
#             archivo_encontrado = True
#             # Intentar eliminar el archivo físico
#             try:
#                 ruta_completa = os.path.join(UPLOAD_DIR, datos['nombre_archivo'])
#                 if os.path.exists(ruta_completa):
#                     os.remove(ruta_completa)
#             except Exception as e:
#                 print(f"Error al eliminar archivo físico: {e}")
#         else:
#             nuevos_archivos.append(archivo)
    
#     if not archivo_encontrado:
#         return "ARCHIVO_NO_ENCONTRADO"
    
#     # Actualizar la evidencia con la nueva lista de archivos
#     actualizar = await evidencia_collection.update_one(
#         {"id_evidencia": datos['id_evidencia'], "estado_evidencia": 1},
#         {"$set": {
#             "archivos": nuevos_archivos,
#             "updated_at": datetime.now(),
#             "user_m": datos['id_usuario']
#         }}
#     )
    
#     # Guardar en Log
#     log = procesar_log(
#         "ARCHIVO ELIMINADO DE EVIDENCIA",
#         datos['id_usuario'],
#         f"Evidencia: {datos['id_evidencia']}, Archivo: {datos['nombre_archivo']}"
#     )
#     guardar_log = await log_general_collection.insert_one(log)
    
#     return "ARCHIVO_ELIMINADO"

async def eliminar_evidencia(evidencia_data: dict) -> str:
    """
    Elimina lógicamente una evidencia (cambia estado_evidencia a 0).
    """
    if evidencia_data['especifico']:
        # Cambiar estado a 0 (inactivo)
        objeto = {
            "estado_evidencia": 0,
            "user_m": evidencia_data['id_usuario'],
            "updated_at": datetime.now()
        }
        
        # Verificar que la evidencia existe y está activa
        especifico = await evidencia_collection.find_one(
            {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 1},
            {"_id": 0, "titulo_evidencia": 1}
        )
        
        if especifico:
            # Actualizar estado
            especifico_ok = await evidencia_collection.update_one(
                {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 1},
                {"$set": objeto}
            )
            res = "OK"
        else:
            res = "FAIL"
        
        # Guardar en Log
        log = procesar_log(
            "Se eliminó la Evidencia: ",
            evidencia_data['id_usuario'],
            evidencia_data['especifico']
        )
        guardar_log = await log_general_collection.insert_one(log)
        
        # Guardar en histórico
        evidencia_historico = procesar_historico(
            "EVIDENCIA ELIMINADA", 
            evidencia_data['id_usuario'], 
            {"id_evidencia": evidencia_data['especifico'], "titulo_evidencia": especifico.get('titulo_evidencia', '')}
        )
        guardar_evidencia_historico = await h_evidencia_collection.insert_one(evidencia_historico)
        
        return res
    else:
        return "SIN_ESPECIFICO"

async def reestablecer_evidencia(evidencia_data: dict) -> dict:
    """
    Reestablece una evidencia previamente eliminada (cambia estado_evidencia a 1).
    """
    if evidencia_data['especifico']:
        # Cambiar estado a 1 (activo)
        objeto = {
            "estado_evidencia": 1,
            "user_m": evidencia_data['id_usuario'],
            "updated_at": datetime.now()
        }
        
        # Verificar que la evidencia existe y está eliminada
        especifico = await evidencia_collection.find_one(
            {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 0},
            {"_id": 0, "titulo_evidencia": 1}
        )
        
        if especifico:
            # Actualizar estado
            especifico_ok = await evidencia_collection.update_one(
                {"id_evidencia": evidencia_data['especifico'], "estado_evidencia": 0},
                {"$set": objeto}
            )
            res = "OK"
        else:
            res = "FAIL"
        
        # Guardar en Log
        log = procesar_log(
            "Se reestableció la Evidencia: ",
            evidencia_data['id_usuario'],
            evidencia_data['especifico']
        )
        guardar_log = await log_general_collection.insert_one(log)
        
        return res
    else:
        return "SIN_ESPECIFICO"

async def obtener_archivo(nombre_archivo: str) -> dict:
    """
    Obtiene la información de un archivo específico.
    
    Args:
        nombre_archivo: Nombre del archivo a obtener
        
    Returns:
        Diccionario con la información del archivo o un mensaje de error
    """
    ruta_completa = os.path.join(UPLOAD_DIR, nombre_archivo)
    
    if os.path.exists(ruta_completa):
        return {
            "existe": True,
            "ruta": ruta_completa,
            "nombre": nombre_archivo
        }
    else:
        return {
            "existe": False,
            "mensaje": "Archivo no encontrado"
        }
