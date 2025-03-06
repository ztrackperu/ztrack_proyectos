from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class PreDerivadosSchema(BaseModel) :
    id_pre_derivado:Optional[int] | None =0
    nombre_pre_derivado :str = Field(...)
    observaciones_pre_derivado :str = Field(...)
    estado_pre_derivado:Optional[int] | None =1
    valor_pre_derivado:Optional[int] | None =0
    cantidad_actividades :Optional[int] | None =0 
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico
    class Config:
        json_schema_extra = {
            "example": {
            "id_pre_derivado":None,
            "nombre_pre_derivado":"XL 40 PIES LADO DERECHO",
            "observaciones_pre_derivado":"Piso plano SIN MAQUINA",
            "estado_pre_derivado":None,
            "valor_pre_derivado":None,
            "cantidad_actividades":None,
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

