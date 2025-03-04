from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

#aqui pedimos las funciones que incluyen nuestro CRUD
from server.funciones.usuarios import (
    guardar_usuario,
    login_proyecto,
    listar_usuarios,
    super_usuario,
)
#Aqui importamos el modelo necesario para la clase 
from server.models.usuarios import (
    ErrorResponseModel,
    ResponseModel,
    UsuarioSchema,
    LoginSchema,
    ConsultarSchema,
)
router = APIRouter()

@router.post("/", response_description="Datos agregados a la base de datos.")
async def add_usuario(datos: UsuarioSchema = Body(...)):
    datos = jsonable_encoder(datos)   
    new_notificacion = await guardar_usuario(datos)
    #print(new_notificacion)
    #return new_notificacion
    return ResponseModel(new_notificacion, "ok")

@router.post("/login", response_description="Datos agregados a la base de datos.")
async def add_usuario(datos: LoginSchema = Body(...)):
    datos = jsonable_encoder(datos)   
    new_notificacion = await login_proyecto(datos)
    #print(new_notificacion)
    #return new_notificacion
    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("USUARIO/CLAVE INCORRECTO", 404, "NO SE HA ENCONTRADO")

@router.post("/listar", response_description="Datos Listados de los usuarios.")
async def listar_usuarios_ok(datos: ConsultarSchema = Body(...)):
    datos = jsonable_encoder(datos) 
    print("********")
    print(datos)  
    print("********")

    new_notificacion = await listar_usuarios(datos)

    if  new_notificacion:
        return ResponseModel(new_notificacion, "ok")
    else :
        return ErrorResponseModel("USUARIO/CLAVE INCORRECTO", 404, "NO SE HA ENCONTRADO")
    #return "ola"

@router.get("/superusuario/", response_description="Datos recuperados")
async def get_super():
    notificacions = await super_usuario()
    if notificacions:
        return ResponseModel(notificacions, "Datos  recuperados exitosamente.")
    return ResponseModel(notificacions, "Lista vacía devuelta")


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

