from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

#aqui pedimos las funciones que incluyen nuestro CRUD
from server.funciones.pollitos.operaciones import (
    guardar_operaciones,
    listar_operaciones,
    ver_operaciones,
    eliminar_operaciones,
    reestablecer_operaciones,   
)
#Aqui importamos el modelo necesario para la clase 
from server.models.pollitos.operaciones import (
    ErrorResponseModel,
    ResponseModel,
    OperacionesSchema,
    ConsultarSchema,
)
router = APIRouter()

@router.post("/", response_description="Datos agregados a la base de datos.")
async def guardar_operaciones_ok(datos: OperacionesSchema = Body(...)):
    datos = jsonable_encoder(datos)   
    new_notificacion = await guardar_operaciones(datos)

    return ResponseModel(new_notificacion, "ok")

@router.post("/listar", response_description="Datos Listados de los usuarios.")
async def listar_operaciones_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await listar_operaciones(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("VERIFICA TUS DATOS", 404, "NO SE HA ENCONTRADO")

@router.post("/ver", response_description="Datos Listados de los usuarios.")
async def ver_operaciones_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await ver_operaciones(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")

@router.post("/eliminar", response_description="Datos Listados de los usuarios.")
async def eliminar_operaciones_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await eliminar_operaciones(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")

@router.post("/reestablecer", response_description="Datos Listados de los usuarios.")
async def reestablecer_operaciones_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await reestablecer_operaciones(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")
    
