from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ReProyectoDerivadoSchema(BaseModel) :
    id_re_proyecto_derivado:Optional[int] | None =0
    pre_derivado_id :int = Field(...)
    pre_proyecto_id :int = Field(...)
    estado_re_proyecto_derivado:Optional[int] | None =1
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =None #generico
    class Config:
        json_schema_extra = {
            "example": {
                "id_re_proyecto_derivado":None,
                "pre_derivado_id":0,
                "pre_proyecto_id":0,
                "estado_re_proyecto_derivado":None,
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "created_at":None,
                "updated_at":None,
                "user_c":0,
                "user_m":None
            }
        }

class ConsultarSchema(BaseModel):
    id_usuario: Optional[int] | None =0
    tipo_usuario: Optional[int] | None =0
    token_proyecto : Optional[str] | None ="blablabla"
    especifico_proyecto: Optional[int] | None =0
    especifico_derivado: Optional[int] | None =0
    fecha_inicio: Optional[str] | None=None
    fecha_fin: Optional[str] | None =None
    class Config:
        json_schema_extra = {
            "example": {
                "id_usuario": 0,
                "tipo_usuario": 0,
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "especifico_proyecto" :0,
                "especifico_derivado" :0,
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

