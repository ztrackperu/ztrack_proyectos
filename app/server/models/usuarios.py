from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class UsuarioSchema(BaseModel) :
    id_usuario :Optional[int] | None =0
    user_proyecto : str = Field(...)
    clave_proyecto :  str = Field(...)
    estado_usuario : Optional[int] | None =1 
    tipo_usuario : Optional[int] | None =2 
    dni_usuario : str = Field(...)
    token_proyecto : Optional[str] | None ="blablabla"
    nombres_usuario : str = Field(...)
    apellidos_usuario :str = Field(...)
    correo_usuario :str = Field(...)
    url_foto_usuario : Optional[str] | None ="fotos/usuarios/test_usuario.png"
    updated_at: Optional[datetime] | None =datetime.now() #generico
    created_at: Optional[datetime] | None =datetime.now() #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
            "id_usuario":None,
            "user_proyecto":"zgroup",
            "clave_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5a80b06cb4118b374892a1248b02a395",
            "estado_usuario":None,
            "tipo_usuario":None,
            "dni_usuario" :"73144309",
            "token_proyecto":None,
            "nombres_usuario" :"Luis Pablo",
            "apellidos_usuario" :" Marcelo Perea",
            "correo_usuario" : "ztrack@zgroup.com.pe",
            "url_foto_usuario" :"fotos/usuarios/test_usuario.png",
            "created_at":None,
            "updated_at":None,
            "user_c":None,
            "user_m":None
            }
        }

class LoginSchema(BaseModel) :
    user_proyecto : str = Field(...)
    clave_proyecto :  str = Field(...)
    class Config:
        json_schema_extra = {
            "example": {
                "user_proyecto": "zgroup",
                "clave_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5a80b06cb4118b374892a1248b02a395"

            }
        }

class ConsultarSchema(BaseModel):
    id_usuario: Optional[int] | None =0
    tipo_usuario: Optional[int] | None =0
    token_proyecto : Optional[str] | None ="blablabla"
    especifico: Optional[int] | None =0
    fecha_inicio: Optional[datetime] | None=None
    fecha_fin: Optional[datetime] | None =None
    class Config:
        json_schema_extra = {
            "example": {
                "id_usuario": 0,
                "tipo_usuario": 0,
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5a80b06cb4118b374892a1248b02a395",
                "especifico" :0
            }
        }

#respuesta cuando todo esta bien
def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }

#respuesta cuando algo sale mal 
def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}

