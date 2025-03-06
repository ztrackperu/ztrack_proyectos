from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ActividadSchema(BaseModel) :
    id_actividad :Optional[int] | None =0
    derivado_id : Optional[int] | None =0
    nombre_actividad : str = Field(...)
    descripcion_actividad : Optional[str] | None ="SIN DESCRIPCION"
    responsable_actividad : str = Field(...)
    observaciones_actividad : Optional[str] | None ="SIN OBSERVACIONES"
    fecha_inicio_actividad :Optional[datetime] | None =None
    fecha_fin_actividad :Optional[datetime] | None =None
    peso_actividad : Optional[int] | None = 0
    estado_actividad : Optional[int] | None = 1
    user_cierre_actividad : Optional[int] | None =0 
    fecha_cierre_actividad : Optional[datetime] | None =None
    validacion_actividad :Optional[int] | None = 0
    pre_requisitos_actividad :Optional[int] | None =[]
    cantidad_reportes :Optional[int] | None = 0
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
            "id_actividad":None,
            "derivado_id":0,
            "nombre_actividad": "CONSTRUCCION DE PISO",
            "descripcion_actividad":"Sin descripcion",
            "responsable_actividad":"Luis Pablo Marcelo Perea",
            "observaciones_actividad": None,
            "fecha_inicio_actividad":None,
            "fecha_fin_actividad":None,
            "peso_actividad":0,
            "user_cierre_actividad":0,
            "fecha_cierre_actividad":None,
            "validacion_actividad":0,
            "pre_requisitos_actividad":[],
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

