from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

#aqui pedimos las funciones que incluyen nuestro CRUD
from server.funciones.re_actividad_validacion import (
    guardar_re_actividad_validacion,
    editar_re_actividad_validacion,
    buscar_re,
    eliminar_re,
    listar,
)
#Aqui importamos el modelo necesario para la clase 
from server.models.re_actividad_validacion import (
    ErrorResponseModel,
    ResponseModel,
    ReActividadValidacionSchema,
    ReDerivadoActividadEditarSchema,
    ConsultarSchema,
)
router = APIRouter()

@router.post("/", response_description="Datos agregados a la base de datos.")
async def guardar_re_actividad_validacion_ok(datos: ReActividadValidacionSchema = Body(...)):
    datos = jsonable_encoder(datos)   
    new_notificacion = await guardar_re_actividad_validacion(datos)
    return ResponseModel(new_notificacion, "ok")

@router.post("/editar", response_description="Datos agregados a la base de datos.")
async def editar_re_actividad_validacion_ok(datos: ReDerivadoActividadEditarSchema = Body(...)):
    datos = jsonable_encoder(datos)   
    new_notificacion = await editar_re_actividad_validacion(datos)

    return ResponseModel(new_notificacion, "ok")

@router.post("/buscar", response_description="Datos Listados de los usuarios.")
async def buscar_re_actividad_validacion_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await buscar_re(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("VERIFICA TUS DATOS", 404, "NO SE HA ENCONTRADO")

@router.post("/eliminar", response_description="Datos Listados de los usuarios.")
async def eliminar_re_actividad_validacion_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await eliminar_re(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")

@router.post("/listar", response_description="Datos Listados de los usuarios.")
async def listar_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    new_notificacion = await listar(datos)
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("verifica tus datos", 404, "NO SE HA ENCONTRADO")
    
