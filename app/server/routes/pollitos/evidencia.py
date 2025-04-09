from fastapi import APIRouter, Body, File, UploadFile, Form, Depends, Query, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import shutil
import base64
import mimetypes
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

# Importaciones de funciones
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

# Modelo para documentación del ejemplo
class EvidenciaRequest(BaseModel):
    id_evidencia: Optional[int] = 0
    tipo_entidad: str
    entidad_id: int
    titulo_evidencia: str
    descripcion_evidencia: Optional[str] = None
    ubicacion_evidencia: Optional[str] = None
    foto_evidencia: Optional[str] = None
    archivo_evidencia: Optional[str] = None
    archivo_nombre: Optional[str] = None
    archivo_tipo: Optional[str] = None
    user_c: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_evidencia": 0,
                "tipo_entidad": "operacion",
                "entidad_id": 1,
                "titulo_evidencia": "Carga de pollitos en camión",
                "descripcion_evidencia": "Evidencia de la carga de pollitos en el camión AKB-2340",
                "ubicacion_evidencia": "Granja 1, zona de carga",
                "foto_evidencia": None,
                "archivo_evidencia": None,
                "archivo_nombre": None,
                "archivo_tipo": None,
                "user_c": 1
            }
        }

@router.post("/", response_description="Evidencia creada o actualizada", response_model=Dict[str, Any])
async def crear_actualizar_evidencia(
    request: Request,
    evidencia: Optional[EvidenciaRequest] = None
):
    """
    Crea o actualiza una evidencia, con soporte para múltiples archivos adjuntos.
    
    Acepta datos en formato JSON o multipart/form-data.
    
    Para crear una nueva evidencia, no incluir el campo id_evidencia o establecerlo a 0.
    Para actualizar una evidencia existente, incluir el id_evidencia con un valor válido.
    
    Ejemplo de JSON:
    ```json
    {
        "id_evidencia": 0,
        "tipo_entidad": "operacion",
        "entidad_id": 1,
        "titulo_evidencia": "Carga de pollitos en camión",
        "descripcion_evidencia": "Evidencia de la carga de pollitos en el camión AKB-2340",
        "ubicacion_evidencia": "Granja 1, zona de carga",
        "user_c": 1,
        "archivos": [
            {
                "nombre": "foto1.jpg",
                "tipo": "image/jpeg",
                "contenido": "base64_encoded_content..."
            },
            {
                "nombre": "documento.pdf",
                "tipo": "application/pdf",
                "contenido": "base64_encoded_content..."
            }
        ]
    }
    ```
    
    Para enviar archivos, use multipart/form-data con los mismos campos y añada:
    - archivos[]: múltiples archivos (pueden ser imágenes, PDFs, etc.)
    """
    content_type = request.headers.get("Content-Type", "")
    datos_dict = {}
    
    # Procesar según el tipo de contenido
    if "application/json" in content_type:
        # Procesar datos JSON
        datos_dict = await request.json()
        
        # Verificar si hay archivos en formato base64
        if "archivos" in datos_dict and isinstance(datos_dict["archivos"], list):
            # Los archivos ya están en el formato esperado por la función guardar_evidencia
            pass
        # Mantener compatibilidad con el formato anterior (archivo único)
        elif "archivo_evidencia" in datos_dict and datos_dict["archivo_evidencia"] and isinstance(datos_dict["archivo_evidencia"], str) and not datos_dict["archivo_evidencia"].startswith("http"):
            try:
                # Determinar la extensión del archivo basada en el tipo MIME
                extension = ".png"  # Por defecto
                if datos_dict.get("archivo_tipo"):
                    mime_type = datos_dict["archivo_tipo"]
                    if mime_type == "image/jpeg":
                        extension = ".jpg"
                    elif mime_type == "image/png":
                        extension = ".png"
                    elif mime_type == "application/pdf":
                        extension = ".pdf"
                
                # Crear un archivo en el formato esperado por la nueva función
                archivo = {
                    "nombre": datos_dict.get("archivo_nombre", f"archivo{extension}"),
                    "tipo": datos_dict.get("archivo_tipo", "application/octet-stream"),
                    "contenido": datos_dict["archivo_evidencia"]
                }
                
                # Agregar a la lista de archivos
                datos_dict["archivos"] = [archivo]
                
                # Eliminar los campos antiguos para evitar duplicación
                if "archivo_evidencia" in datos_dict:
                    del datos_dict["archivo_evidencia"]
                if "archivo_nombre" in datos_dict:
                    del datos_dict["archivo_nombre"]
                if "archivo_tipo" in datos_dict:
                    del datos_dict["archivo_tipo"]
                
            except Exception as e:
                return ErrorResponseModel("Error", 400, f"Error al procesar el archivo: {str(e)}")
        
        # Procesar foto si existe (mantener compatibilidad)
        if "foto_evidencia" in datos_dict and datos_dict["foto_evidencia"] and isinstance(datos_dict["foto_evidencia"], str) and not datos_dict["foto_evidencia"].startswith("http"):
            try:
                # Crear un archivo en el formato esperado
                foto = {
                    "nombre": "foto.jpg",
                    "tipo": "image/jpeg",
                    "contenido": datos_dict["foto_evidencia"]
                }
                
                # Agregar a la lista de archivos
                if "archivos" not in datos_dict:
                    datos_dict["archivos"] = []
                datos_dict["archivos"].append(foto)
                
                # Eliminar el campo antiguo
                del datos_dict["foto_evidencia"]
                
            except Exception as e:
                return ErrorResponseModel("Error", 400, f"Error al procesar la foto: {str(e)}")
    
    elif "multipart/form-data" in content_type:
        # Procesar datos de formulario
        form_data = await request.form()
        
        # Extraer campos básicos
        for key, value in form_data.items():
            if not key.startswith("archivos"):
                # Convertir valores numéricos si es posible
                if isinstance(value, str) and value.isdigit():
                    datos_dict[key] = int(value)
                else:
                    datos_dict[key] = value
        
        # Procesar múltiples archivos
        archivos = []
        for key in form_data.keys():
            if key.startswith("archivos"):
                archivo = form_data[key]
                if hasattr(archivo, "filename") and archivo.filename:
                    try:
                        # Leer el contenido del archivo
                        content = await archivo.read()
                        
                        # Codificar en base64
                        contenido_base64 = base64.b64encode(content).decode('utf-8')
                        
                        # Agregar a la lista de archivos
                        archivos.append({
                            "nombre": archivo.filename,
                            "tipo": archivo.content_type,
                            "contenido": contenido_base64
                        })
                    except Exception as e:
                        return ErrorResponseModel("Error", 400, f"Error al procesar el archivo {archivo.filename}: {str(e)}")
        
        # Agregar archivos al diccionario de datos
        if archivos:
            datos_dict["archivos"] = archivos
        
        # Mantener compatibilidad con el formato anterior
        if "foto" in form_data:
            foto = form_data["foto"]
            if hasattr(foto, "filename") and foto.filename:
                try:
                    # Leer el contenido del archivo
                    content = await foto.read()
                    
                    # Codificar en base64
                    contenido_base64 = base64.b64encode(content).decode('utf-8')
                    
                    # Agregar a la lista de archivos
                    if "archivos" not in datos_dict:
                        datos_dict["archivos"] = []
                    
                    datos_dict["archivos"].append({
                        "nombre": foto.filename,
                        "tipo": foto.content_type,
                        "contenido": contenido_base64
                    })
                except Exception as e:
                    return ErrorResponseModel("Error", 400, f"Error al procesar la foto: {str(e)}")
        
        if "archivo" in form_data:
            archivo = form_data["archivo"]
            if hasattr(archivo, "filename") and archivo.filename:
                try:
                    # Leer el contenido del archivo
                    content = await archivo.read()
                    
                    # Codificar en base64
                    contenido_base64 = base64.b64encode(content).decode('utf-8')
                    
                    # Agregar a la lista de archivos
                    if "archivos" not in datos_dict:
                        datos_dict["archivos"] = []
                    
                    datos_dict["archivos"].append({
                        "nombre": archivo.filename,
                        "tipo": archivo.content_type,
                        "contenido": contenido_base64
                    })
                except Exception as e:
                    return ErrorResponseModel("Error", 400, f"Error al procesar el archivo: {str(e)}")
    
    else:
        return ErrorResponseModel("Error", 400, "Tipo de contenido no soportado")
    
    # Verificar campos obligatorios
    campos_requeridos = ["tipo_entidad", "entidad_id", "titulo_evidencia", "user_c"]
    for campo in campos_requeridos:
        if campo not in datos_dict or datos_dict[campo] is None:
            return ErrorResponseModel("Error", 422, f"El campo '{campo}' es obligatorio")
    
    # Asegurar que id_evidencia sea 0 o None si no se proporciona
    if "id_evidencia" not in datos_dict or datos_dict["id_evidencia"] is None:
        datos_dict["id_evidencia"] = 0
    
    # Guardar evidencia
    new_evidencia = await guardar_evidencia(datos_dict)
    
    # Manejar posibles errores
    if new_evidencia == "DUPLICADO":
        return ErrorResponseModel("Error", 400, "Ya existe una evidencia con este título para la misma entidad")
    elif new_evidencia == "NO EXISTE":
        return ErrorResponseModel("Error", 404, "La evidencia a actualizar no existe")
    elif isinstance(new_evidencia, str) and new_evidencia.startswith("ERROR"):
        return ErrorResponseModel("Error", 400, new_evidencia)
    
    return ResponseModel(new_evidencia, "Evidencia guardada correctamente")



# Cambiar listar a POST en /listar
@router.post("/listar", response_description="Evidencias listadas")
async def listar_todas_evidencias(datos: ConsultarSchema = Body(...)):
    """
    Lista todas las evidencias según los criterios de filtrado.
    
    Requiere al menos el id_usuario en el cuerpo de la solicitud.
    """
    datos_dict = jsonable_encoder(datos)
    evidencias = await listar_evidencias(datos_dict)
    
    if evidencias:
        return ResponseModel(evidencias, "ok")
    else:
        return ErrorResponseModel("VERIFICA TUS DATOS", 404, "NO SE HA ENCONTRADO")


# Cambiar ver a POST
@router.post("/ver", response_description="Evidencia recuperada")
async def obtener_evidencia(id_evidencia: int = Body(...), id_usuario: int = Body(...)):
    """
    Obtiene los detalles de una evidencia específica.
    """
    datos_dict = {
        "id_usuario": id_usuario,
        "especifico": id_evidencia
    }
    evidencia = await ver_evidencia(datos_dict)
    
    if evidencia:
        return ResponseModel(evidencia, "Evidencia recuperada correctamente")
    return ErrorResponseModel("Error", 404, "Evidencia no encontrada")

# Cambiar eliminar a POST
@router.post("/eliminar", response_description="Evidencia eliminada")
async def eliminar_una_evidencia(id_evidencia: int = Body(...), id_usuario: int = Body(...)):
    """
    Elimina lógicamente una evidencia (cambia estado_evidencia a 0).
    """
    datos_dict = {
        "id_usuario": id_usuario,
        "especifico": id_evidencia
    }
    resultado = await eliminar_evidencia(datos_dict)
    
    if resultado == "OK":
        return ResponseModel("Eliminado", "Evidencia eliminada correctamente")
    elif resultado == "FAIL":
        return ErrorResponseModel("Error", 404, "Evidencia no encontrada")
    else:
        return ErrorResponseModel("Error", 400, "Se requiere especificar una evidencia")

# Cambiar reestablecer a POST
@router.post("/reestablecer", response_description="Evidencia reestablecida")
async def reestablecer_una_evidencia(id_evidencia: int = Body(...), id_usuario: int = Body(...)):
    """
    Reestablece una evidencia previamente eliminada (cambia estado_evidencia a 1).
    """
    datos_dict = {
        "id_usuario": id_usuario,
        "especifico": id_evidencia
    }
    resultado = await reestablecer_evidencia(datos_dict)
    
    if resultado == "OK":
        return ResponseModel("Reestablecido", "Evidencia reestablecida correctamente")
    elif resultado == "FAIL":
        return ErrorResponseModel("Error", 404, "Evidencia no encontrada o ya está activa")
    else:
        return ErrorResponseModel("Error", 400, "Se requiere especificar una evidencia")

# Mantener get_file como GET ya que es para servir archivos
@router.get("/files/{nombre_archivo}", response_description="Archivo de evidencia")
async def descargar_archivo(nombre_archivo: str):
    """
    Descarga un archivo específico de evidencia.
    """
    resultado = await obtener_archivo(nombre_archivo)
    
    if resultado["existe"]:
        # Determinar el tipo de contenido usando la biblioteca mimetypes
        content_type, _ = mimetypes.guess_type(nombre_archivo)
        
        # Si no se puede determinar, usar el tipo genérico
        if content_type is None:
            content_type = "application/octet-stream"
        
        return FileResponse(
            resultado["ruta"],
            media_type=content_type,
            filename=nombre_archivo
        )
    else:
        return ErrorResponseModel("Error", 404, "Archivo no encontrado")


# Agrega esta función justo antes de la función descargar_archivo

async def obtener_archivo(nombre_archivo: str):
    """
    Obtiene información sobre un archivo de evidencia.
    
    Args:
        nombre_archivo: Nombre del archivo a obtener
        
    Returns:
        Diccionario con información del archivo
    """
    file_path = os.path.join(UPLOAD_DIR, nombre_archivo)
    
    if os.path.exists(file_path):
        return {
            "existe": True,
            "ruta": file_path,
            "nombre": nombre_archivo
        }
    else:
        return {
            "existe": False,
            "mensaje": "Archivo no encontrado"
        }
