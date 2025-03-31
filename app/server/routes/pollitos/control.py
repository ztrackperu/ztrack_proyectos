from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

#aqui pedimos las funciones que incluyen nuestro CRUD
from server.funciones.pollitos.control import (
    guardar_control,
    listar_control,
    buscar_control,
    ver_control,
    eliminar_control,
    reestablecer_control,   
)
#Aqui importamos el modelo necesario para la clase 
from server.models.pollitos.control import (
    ErrorResponseModel,
    ResponseModel,
    ControlSchema,
    ConsultarSchema,
)
router = APIRouter()

@router.post("/", response_description="Datos agregados a la base de datos.")
async def guardar_control_ok(datos: ControlSchema = Body(...)):
    datos = jsonable_encoder(datos)   
    new_notificacion = await guardar_control(datos)

    return ResponseModel(new_notificacion, "ok")

@router.post("/listar", response_description="Datos Listados de los usuarios.")
async def listar_control_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    print ("Hola estoy aca")
    new_notificacion = await listar_control(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("VERIFICA TUS DATOS", 404, "NO SE HA ENCONTRADO")

@router.post("/ver", response_description="Datos Listados de los usuarios.")
async def ver_control_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    print ("Hola estoy aca", datos)
    new_notificacion = await ver_control(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")

@router.post("/eliminar", response_description="Datos Listados de los usuarios.")
async def eliminar_control_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await eliminar_control(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")

@router.post("/reestablecer", response_description="Datos Listados de los usuarios.")
async def reestablecer_control_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await reestablecer_control(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")
    

@router.post("/buscar", response_description="Datos Listados de los usuarios.")
async def buscar_control_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    print ("Hola estoy aca")
    new_notificacion = await buscar_control(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("VERIFICA TUS DATOS", 404, "NO SE HA ENCONTRADO")