from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import base64
from typing import Optional
from datetime import datetime

# Importaciones existentes
from server.funciones.pollitos.evidencia import (
    guardar_evidencia,
    listar_evidencias,
    ver_evidencia,
    eliminar_evidencia,
    reestablecer_evidencia,
)
from server.models.pollitos.evidencia import (
    ErrorResponseModel,
    ResponseModel,
    EvidenciaSchema,
    ConsultarSchema,
)

router = APIRouter()

# Directorio para almacenar archivos
UPLOAD_DIR = "app/server/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Endpoint unificado para crear/actualizar evidencias (solo JSON)
@router.post("/", response_description="Evidencia creada o actualizada")
async def guardar_evidencia_ok(datos: EvidenciaSchema = Body(...)):
    """
    Crea o actualiza una evidencia.
    
    Para crear una nueva evidencia, no incluir el campo id_evidencia.
    Para actualizar una evidencia existente, incluir el id_evidencia.
    
    Para incluir archivos, se debe enviar en el JSON:
    - archivo_base64: string con el contenido del archivo en base64
    - archivo_nombre: nombre original del archivo
    - archivo_tipo: tipo MIME del archivo
    - es_foto: booleano que indica si es una imagen (true) o documento (false)
    """
    datos_dict = jsonable_encoder(datos)
    
    # Asegurar que id_evidencia sea 0 o None si no se proporciona
    # Esto indica al backend que debe crear una nueva evidencia
    if "id_evidencia" not in datos_dict or datos_dict["id_evidencia"] is None:
        datos_dict["id_evidencia"] = 0
    
    # Procesar archivo en base64 si existe
    if "archivo_base64" in datos_dict and datos_dict["archivo_base64"]:
        try:
            # Decodificar el archivo base64
            archivo_data = base64.b64decode(datos_dict["archivo_base64"])
            
            # Obtener extensión del archivo
            nombre_archivo = datos_dict.get("archivo_nombre", "archivo")
            extension = os.path.splitext(nombre_archivo)[1]
            if not extension:
                # Asignar extensión basada en el tipo MIME
                mime_type = datos_dict.get("archivo_tipo", "")
                if mime_type.startswith("image/"):
                    extension = ".jpg" if "jpeg" in mime_type else f".{mime_type.split('/')[1]}"
                elif mime_type.startswith("application/pdf"):
                    extension = ".pdf"
                else:
                    extension = ".bin"
            
            # Generar nombre único para el archivo
            unique_filename = f"{uuid.uuid4()}{extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            # Guardar archivo
            with open(file_path, "wb") as buffer:
                buffer.write(archivo_data)
            
            # Generar URL relativa
            file_url = f"/evidencias/files/{unique_filename}"
            
            # Asignar URL según tipo de archivo
            es_foto = datos_dict.get("es_foto", False)
            if es_foto:
                datos_dict["link_evidencia"] = file_url
            else:
                datos_dict["archivo_evidencia"] = file_url
            
            # Eliminar el campo base64 para no guardarlo en la BD
            del datos_dict["archivo_base64"]
            
        except Exception as e:
            return ErrorResponseModel("Error", 400, f"Error al procesar el archivo: {str(e)}")
    
    # Eliminar campos adicionales que no corresponden al modelo de datos
    if "es_foto" in datos_dict:
        del datos_dict["es_foto"]
    
    # Guardar evidencia
    new_evidencia = await guardar_evidencia(datos_dict)
    
    # Manejar posibles errores
    if new_evidencia == "DUPLICADO":
        return ErrorResponseModel("Error", 400, "Ya existe una evidencia con este título")
    elif new_evidencia == "NO EXISTE":
        return ErrorResponseModel("Error", 404, "La evidencia a actualizar no existe")
    elif isinstance(new_evidencia, str) and new_evidencia.startswith("ERROR"):
        return ErrorResponseModel("Error", 400, new_evidencia)
    
    return ResponseModel(new_evidencia, "Evidencia guardada correctamente")

# Resto del código igual...


# Endpoint para listar evidencias
@router.post("/listar", response_description="Listado de evidencias")
async def listar_evidencias_ok(datos: ConsultarSchema = Body(...)):
    """
    Obtiene un listado de evidencias según los criterios especificados.
    """
    datos = jsonable_encoder(datos)
    resultado = await listar_evidencias(datos)
    
    if resultado:
        return ResponseModel(resultado, "Listado de evidencias obtenido correctamente")
    else:
        return ErrorResponseModel("Error", 404, "No se encontraron evidencias con los criterios especificados")

# Endpoint para ver una evidencia específica
@router.post("/ver", response_description="Detalle de evidencia")
async def ver_evidencia_ok(datos: ConsultarSchema = Body(...)):
    """
    Obtiene el detalle de una evidencia específica.
    """
    datos = jsonable_encoder(datos)
    resultado = await ver_evidencia(datos)
    
    if resultado:
        return ResponseModel(resultado, "Detalle de evidencia obtenido correctamente")
    else:
        return ErrorResponseModel("Error", 404, "No se encontró la evidencia especificada")

# Endpoint para eliminar una evidencia
@router.post("/eliminar", response_description="Evidencia eliminada")
async def eliminar_evidencia_ok(datos: ConsultarSchema = Body(...)):
    """
    Elimina lógicamente una evidencia.
    """
    datos = jsonable_encoder(datos)
    resultado = await eliminar_evidencia(datos)
    
    if resultado:
        return ResponseModel(resultado, "Evidencia eliminada correctamente")
    else:
        return ErrorResponseModel("Error", 404, "No se encontró la evidencia a eliminar")

# Endpoint para reestablecer una evidencia
@router.post("/reestablecer", response_description="Evidencia reestablecida")
async def reestablecer_evidencia_ok(datos: ConsultarSchema = Body(...)):
    """
    Reestablece una evidencia previamente eliminada.
    """
    datos = jsonable_encoder(datos)
    resultado = await reestablecer_evidencia(datos)
    
    if resultado:
        return ResponseModel(resultado, "Evidencia reestablecida correctamente")
    else:
        return ErrorResponseModel("Error", 404, "No se encontró la evidencia a reestablecer")
