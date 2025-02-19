from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

#aqui pedimos las funciones que incluyen nuestro CRUD
from server.funciones.proyectos import (
    guardar_proyectos,
    check_mongo_connection,
)
#Aqui importamos el modelo necesario para la clase 
from server.models.proyectos import (
    ErrorResponseModel,
    ResponseModel,
    ProyectosSchema,
)
router = APIRouter()

@router.get("/health")
async def health_check():
    mongo_status = await check_mongo_connection()
    if mongo_status:
        return {"status": "ok", "mongo": "connected"}
    else:
        return {"status": "error", "mongo": "not connected"}

@router.post("/", response_description="Datos agregados a la base de datos.")
async def add_proyecto(datos: ProyectosSchema = Body(...)):
    datos = jsonable_encoder(datos)   
    new_notificacion = await guardar_proyectos(datos)
    #print(new_notificacion)
    #return new_notificacion
    return ResponseModel(new_notificacion, "ok")

@router.get("/{imei}", response_description="Datos recuperados")
async def get_notificacions(imei:str):
    notificacions = await retrieve_datos(imei)
    if notificacions:
        return ResponseModel(notificacions, "Datos  recuperados exitosamente.")
    return ResponseModel(notificacions, "Lista vacía devuelta")

@router.get("/Live/{imei}", response_description="Datos recuperados")
async def get_notificacions(imei:str):
    notificacions = await retrieve_datos_unico(imei)
    if notificacions:
        return ResponseModel(notificacions, "Datos  recuperados exitosamente.")
    return ResponseModel(notificacions, "Lista vacía devuelta")

@router.get("/validarComando/", response_description="Datos recuperados")
async def validar_comando_ok():
    notificacions = await validar_comando()
    if notificacions:
        return ResponseModel(notificacions, "Datos  recuperados exitosamente.")
    return ResponseModel(notificacions, "Lista vacía devuelta")

