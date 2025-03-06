from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

#aqui pedimos las funciones que incluyen nuestro CRUD
from server.funciones.pre_validacion import (
    guardar_pre_validacion,
    listar_pre_validacion,
    ver_pre_validacion,
    eliminar_pre_validacion,
    reestablecer_pre_validacion,   
)
#Aqui importamos el modelo necesario para la clase 
from server.models.pre_validacion import (
    ErrorResponseModel,
    ResponseModel,
    PreValidacionSchema,
    ConsultarSchema,
)
router = APIRouter()

@router.post("/", response_description="Datos agregados a la base de datos.")
async def guardar_pre_validacion_ok(datos: PreValidacionSchema = Body(...)):
    datos = jsonable_encoder(datos)   
    new_notificacion = await guardar_pre_validacion(datos)

    return ResponseModel(new_notificacion, "ok")

@router.post("/listar", response_description="Datos Listados de los usuarios.")
async def listar_pre_validacion_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await listar_pre_validacion(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("VERIFICA TUS DATOS", 404, "NO SE HA ENCONTRADO")

@router.post("/ver", response_description="Datos Listados de los usuarios.")
async def ver_pre_validacion_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await ver_pre_validacion(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")

@router.post("/eliminar", response_description="Datos Listados de los usuarios.")
async def eliminar_pre_validacion_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await eliminar_pre_validacion(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")

@router.post("/reestablecer", response_description="Datos Listados de los usuarios.")
async def reestablecer_pre_validacion_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await reestablecer_pre_validacion(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")
    
