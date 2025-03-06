from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class PreActividadSchema(BaseModel) :
    id_pre_actividad :Optional[int] | None =0
    nombre_pre_actividad : str = Field(...)
    descripcion_pre_actividad : Optional[str] | None ="SIN DESCRIPCION"
    observaciones_pre_actividad : Optional[str] | None ="SIN OBSERVACIONES"
    peso_pre_actividad : Optional[int] | None = 0
    estado_pre_actividad : Optional[int] | None = 1
    pre_requisitos_pre_actividad :Optional[int] | None =[]
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
            "id_pre_actividad":None,
            "nombre_pre_actividad": "CONSTRUCCION DE PISO",
            "descripcion_pre_actividad":"Sin descripcion",
            "observaciones_pre_actividad":"Luis Pablo Marcelo Perea",
            "peso_pre_actividad":None,
            "estado_pre_actividad":None,
            "pre_requisitos_actividad":None,
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

