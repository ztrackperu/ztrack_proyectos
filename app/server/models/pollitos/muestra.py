from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class MuestraSchema(BaseModel) :
    id_muestra:Optional[int] | None =0
    operacion_id : int = Field(...)
    titulo_muestra :str = Field(...)
    condicion_muestra :Optional[str] | None ="INICIO"
    cantidad_muestra :int = Field(...)
    observacion_muestra :Optional[str] | None ="SIN OBSERVACION"
    fecha_muestra :Optional[datetime] | None =None
    estado_muestra :Optional[int] | None =1
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico
    class Config:
        json_schema_extra = {
            "example": {
                "id_muestra":None,
                "operacion_id":1,
                "titulo_muestra":"Test a grupo de pollos en base Tarapoto",
                "condicion_muestra":"INICIO",
                "cantidad_muestra":5,
                "observacion_muestra":None,
                "fecha_muestra" : None ,
                "estado_muestra":None,
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

