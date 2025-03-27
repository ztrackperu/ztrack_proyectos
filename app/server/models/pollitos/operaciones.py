from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class OperacionesSchema(BaseModel) :
    id_operacion:Optional[int] | None =0
    codigo_operacion :Optional[str] | None ="D000"
    titulo_operacion :str = Field(...)
    supervisor_operacion :str = Field(...)
    conductor_operacion :str = Field(...)
    unidad_operacion : str = Field(...)
    ruta_operacion :str = Field(...)
    producto_operacion :str = Field(...)
    fecha_operacion :Optional[datetime] | None =None
    cantidad_control : Optional[int] | None =None 
    user_cierra_operacion :Optional[int] | None =None 
    fecha_cierra_operacion : Optional[datetime] | None =None
    estado_operacion :Optional[int] | None =1
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:int = Field(...)
    user_m:Optional[int] | None =0 #generico
    class Config:
        json_schema_extra = {
            "example": {
                "id_operacion":None,
                "codigo_operacion":None,
                "titulo_operacion":"Desplazar pollitos de la Granja 1 a la Granja2",
                "supervisor_operacion":"Eusebio Avellaneda",
                "conductor_operacion":"Alonso Chavez",
                "unidad_operacion":"AKB-2340",
                "ruta_operacion":"TARAPOTO-TABALOSOS",
                "producto_operacion" :"POLLITOS",
                "fecha_operacion" : None ,
                "cantidad_control":3000,
                "user_cierra_operacion":None,
                "fecha_cierra_operacion":None,
                "created_at":None,
                "updated_at":None,
                "user_c":None,
                "user_m":None
            }
        }

class ConsultarSchema(BaseModel):
    id_usuario: Optional[int] | None =0
    #tipo_usuario: Optional[int] | None =0
    #token_proyecto : Optional[str] | None ="blablabla"
    especifico: Optional[int] | None =0
    fecha_inicio: Optional[str] | None=None
    fecha_fin: Optional[str] | None =None
    class Config:
        json_schema_extra = {
            "example": {
                "id_usuario": 0,
                #"tipo_usuario": 0,
                #"token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "especifico" :0,
                "fecha_inicio" :None,
                "fecha_fin" :None
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

