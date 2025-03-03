from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class IncidenciaSchema(BaseModel) :
    id_incidencia :Optional[int] | None =0
    proyecto_id : int = Field(...)
    estado_incidente : Optional[int] | None =1
    nombre_incidencia : str = Field(...)
    descripcion_incidencia : str = Field(...)
    responsable_incidencia : str = Field(...)
    implicancia_incidencia : str = Field(...)
    cantidad_fotos_incidencias : Optional[int] | None =0
    updated_at: Optional[datetime] | None =datetime.now() #generico
    created_at: Optional[datetime] | None =datetime.now() #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
            "id_incidencia":None,
            "proyecto_id":1,
            "estado_incidente":None,
            "nombre_incidencia": "Corto circuito en instalacion de luminarias",
            "descripcion_incidencia":"El estuvo expuesto a un exceso de voltaje  ",
            "responsable_incidencia":"Mario Matumay",
            "implicancia_incidencia":"proyecto se retrasa de 3 a 5 dias habiles",
            "cantidad_fotos_incidencias":2,
            "created_at":None,
            "updated_at":None,
            "user_c":0,
            "user_m":0
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
