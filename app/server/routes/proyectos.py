from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

#aqui pedimos las funciones que incluyen nuestro CRUD
from server.funciones.proyectos import (
    guardar_proyectos,
    check_mongo_connection,
    seleccionar_plantilla,
    datos_plantila,
    
)
#Aqui importamos el modelo necesario para la clase 
from server.models.proyectos import (
    ErrorResponseModel,
    ResponseModel,
    ProyectosSchema,
    ConsultarSchema,
)
router = APIRouter()

@router.post("/listar", response_description="Datos Listados de los usuarios.")
async def listar_pre_proyecto_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await seleccionar_plantilla(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("VERIFICA TUS DATOS", 404, "NO SE HA ENCONTRADO")


@router.post("/plantilla", response_description="Datos Listados de los usuarios.")
async def plantilla_pre_proyecto_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await datos_plantila(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("VERIFICA TUS DATOS", 404, "NO SE HA ENCONTRADO")

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

