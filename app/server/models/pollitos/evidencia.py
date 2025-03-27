from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class EvidenciaSchema(BaseModel) :
    id_evidencia:Optional[int] | None =0
    muestra_id : int = Field(...)
    titulo_evidencia :str = Field(...)
    ubicacion_evidencia :Optional[str] | None =  None
    temperatura_evidencia :Optional[str] | None =  None
    parametro_1_evidencia :Optional[str] | None =  None
    observacion_evidencia :Optional[str] | None ="SIN OBSERVACION"
    link_evidencia :str = Field(...)
    fecha_evidencia :Optional[datetime] | None =None
    estado_evidencia :Optional[int] | None =1
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico
    class Config:
        json_schema_extra = {
            "example": {
                "id_evidencia":None,
                "muestra_id":1,
                "titulo_evidencia":"POLLO ALEATORIO SECTOR 1",
                "ubicacion_evidencia":"IZQUIERDA SUPERIOR",
                "temperatura_evidencia":"30.5 C°",
                "parametro_1_evidencia":None,
                "observacion_evidencia":None,
                "link_evidencia":"evidencia/manada.jpg",
                "fecha_evidencia" : None ,
                "estado_evidencia":None,
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

