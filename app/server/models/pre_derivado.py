from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class PreDerivadosSchema(BaseModel) :
    id_pre_derivado:Optional[int] | None =0
    nombre_pre_derivado :str = Field(...)
    descripcion_pre_derivado :str = Field(...)
    estado_pre_derivado:Optional[int] | None =1
    #valor_pre_derivado:Optional[int] | None =0
    #cantidad_actividades :Optional[int] | None =0 
    token_proyecto : Optional[str] | None ="blablabla"
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =None #generico
    class Config:
        json_schema_extra = {
            "example": {
            "id_pre_derivado":None,
            "nombre_pre_derivado":"XL 40 PIES LADO DERECHO",
            "descripcion_pre_derivado":"Piso plano SIN MAQUINA",
            "estado_pre_derivado":None,
            #"valor_pre_derivado":None,
            #"cantidad_actividades":None,
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
    especifico: Optional[int] | None =0
    fecha_inicio: Optional[str] | None=None
    fecha_fin: Optional[str] | None =None
    class Config:
        json_schema_extra = {
            "example": {
                "id_usuario": 0,
                "tipo_usuario": 0,
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
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

