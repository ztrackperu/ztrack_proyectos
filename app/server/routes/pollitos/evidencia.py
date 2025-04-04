from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

# Aquí pedimos las funciones que incluyen nuestro CRUD
from server.funciones.pollitos.evidencia import (
    guardar_evidencia,
    listar_evidencias,
    ver_evidencia,
    eliminar_evidencia,
    reestablecer_evidencia,
)

# Aquí importamos el modelo necesario para la clase
from server.models.pollitos.evidencia import (
    ErrorResponseModel,
    ResponseModel,
    EvidenciaSchema,
    ConsultarSchema,
)

router = APIRouter()

@router.post("/", response_description="Datos agregados a la base de datos.")
async def guardar_evidencia_ok(datos: EvidenciaSchema = Body(...)):
    datos = jsonable_encoder(datos)   
    new_notificacion = await guardar_evidencia(datos)
    return ResponseModel(new_notificacion, "ok")

@router.post("/listar", response_description="Datos Listados de las evidencias.")
async def listar_evidencias_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos)
    new_notificacion = await listar_evidencias(datos)
    if new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else:
        return ErrorResponseModel("VERIFICA TUS DATOS", 404, "NO SE HA ENCONTRADO")

@router.post("/ver", response_description="Datos de evidencia específica.")
async def ver_evidencia_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos)
    new_notificacion = await ver_evidencia(datos)
    if new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else:
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")

@router.post("/eliminar", response_description="Evidencia eliminada.")
async def eliminar_evidencia_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos)
    new_notificacion = await eliminar_evidencia(datos)
    if new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else:
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")

@router.post("/reestablecer", response_description="Evidencia reestablecida.")
async def reestablecer_evidencia_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos)
    new_notificacion = await reestablecer_evidencia(datos)
    if new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else:
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")
