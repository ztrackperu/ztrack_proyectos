from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ArchivoIncidenteSchema(BaseModel) :
    id_archivo_incidente :Optional[int] | None =0
    incidente_id : int = Field(...)
    estado_archivo_incidente : Optional[int] | None =1
    url_archivo_incidente : str = Field(...)
    descripcion_archivo_incidente :str = Field(...)
    updated_at: Optional[datetime] | None =datetime.now() #generico
    created_at: Optional[datetime] | None =datetime.now() #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
                "id_archivo_incidente":None,
                "incidente_id":1,
                "estado_incidente":None,
                "url_archivo_incidente": "archivos/incidentes/fallo_electrico.png",
                "descripcion_archivo_incidente" :"Lado superior izquierdo  del techo ",
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

