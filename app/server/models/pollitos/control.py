from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ControlSchema(BaseModel) :
    id_control:Optional[int] | None =0
    operacion_id : int = Field(...)
    condicion_control :Optional[str] | None ="INICIO"
    descripcion_control : Optional[str] | None ="SIN DESCRIPCION"
    cantidad_control :str = Field(...)
    merma_control : Optional[int] | None =0
    peso_control : Optional[str] | None ="SIN PESO"
    temperatura_control : Optional[str] | None ="SIN TEMPERATURA"
    parametro_1_control : Optional[str] | None ="NA"
    parametro_2_control : Optional[str] | None ="NA"
    parametro_3_control : Optional[str] | None ="NA"
    estado_control :Optional[int] | None =1
    fecha_control :Optional[datetime] | None =None
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:int = Field(...)
    user_m:Optional[int] | None =None
    class Config:
        json_schema_extra = {
            "example": {
                "id_control":None,
                "operacion_id":1,
                "condicion_control":"INICIO",
                "descripcion_control":None,
                "cantidad_control":5000,
                "merma_control":None,
                "peso_control":None,
                "temperatura_control" :None,
                "parametro_1_control" : None ,
                "parametro_2_control":None,
                "parametro_3_control":None,
                "fecha_control":None,
                "estado_control":None,
                "created_at":None,
                "updated_at":None,
                "user_c":None,
                "user_m":None
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

