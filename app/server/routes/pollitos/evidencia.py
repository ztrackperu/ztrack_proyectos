from fastapi import APIRouter, Body, File, UploadFile, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
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

# Endpoint unificado para crear/actualizar evidencias
@router.post("/", response_description="Evidencia creada o actualizada")
async def guardar_evidencia_ok(
    file: Optional[UploadFile] = File(None),
    id_evidencia: Optional[int] = Form(0),
    tipo_entidad: Optional[str] = Form(None),
    entidad_id: Optional[int] = Form(None),
    titulo_evidencia: Optional[str] = Form(None),
    ubicacion_evidencia: Optional[str] = Form(None),
    temperatura_evidencia: Optional[str] = Form(None),
    parametro_1_evidencia: Optional[str] = Form(None),
    observacion_evidencia: Optional[str] = Form("SIN OBSERVACION"),
    es_foto: bool = Form(False),
    user_c: Optional[int] = Form(0),
    user_m: Optional[int] = Form(0),
    json_data: Optional[EvidenciaSchema] = None
):
    """
    Crea o actualiza una evidencia, con o sin archivo adjunto.
    
    Se puede usar de dos formas:
    1. Enviando un JSON con todos los datos (sin archivo)
    2. Enviando un formulario multipart con archivo y datos
    """
    # Determinar si estamos recibiendo datos JSON o de formulario
    if json_data:
        # Caso 1: Datos JSON (sin archivo)
        datos = jsonable_encoder(json_data)
    else:
        # Caso 2: Datos de formulario (posiblemente con archivo)
        datos = {
            "id_evidencia": id_evidencia,
            "tipo_entidad": tipo_entidad,
            "entidad_id": entidad_id,
            "titulo_evidencia": titulo_evidencia,
            "ubicacion_evidencia": ubicacion_evidencia,
            "temperatura_evidencia": temperatura_evidencia,
            "parametro_1_evidencia": parametro_1_evidencia,
            "observacion_evidencia": observacion_evidencia,
            "user_c": user_c,
            "user_m": user_m,
            "fecha_evidencia": datetime.now()
        }
        
        # Si hay archivo, procesarlo
        if file:
            # Generar nombre único para el archivo
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            # Guardar archivo
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Generar URL relativa
            file_url = f"/evidencias/files/{unique_filename}"
            
            # Asignar URL según tipo de archivo
            if es_foto:
                datos["link_evidencia"] = file_url
            else:
                datos["archivo_evidencia"] = file_url
                datos["archivo_nombre"] = file.filename
                datos["archivo_tipo"] = file.content_type
    
    # Guardar evidencia
    new_evidencia = await guardar_evidencia(datos)
    
    # Manejar posibles errores
    if new_evidencia == "DUPLICADO":
        return ErrorResponseModel("Error", 400, "Ya existe una evidencia con este título")
    elif new_evidencia == "NO EXISTE":
        return ErrorResponseModel("Error", 404, "La evidencia a actualizar no existe")
    elif isinstance(new_evidencia, str) and new_evidencia.startswith("ERROR"):
        return ErrorResponseModel("Error", 400, new_evidencia)
    
    return ResponseModel(new_evidencia, "Evidencia guardada correctamente")

# Endpoint para servir archivos con opción de visualización o descarga
@router.get("/files/{filename}", response_description="Archivo")
async def get_file(filename: str, inline: bool = True):
    """
    Sirve un archivo para visualización o descarga.
    
    - Si inline=True (predeterminado): Muestra el archivo en el navegador si es posible
    - Si inline=False: Fuerza la descarga del archivo
    """
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return ErrorResponseModel("Archivo no encontrado", 404, "El archivo solicitado no existe")
    
    # Determinar el tipo de contenido basado en la extensión
    content_disposition = "inline" if inline else "attachment"
    
    return FileResponse(
        path=file_path, 
        filename=filename,
        headers={"Content-Disposition": f"{content_disposition}; filename={filename}"}
    )

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
