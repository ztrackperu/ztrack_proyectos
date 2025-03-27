from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ArchivosSchema(BaseModel) :
    id_archivo:Optional[int] | None =0
    operacion_id : int = Field(...)
    titulo_archivo :str = Field(...)
    tipo_archivo :Optional[str] | None ="FOTO"
    link_archivo :str = Field(...)
    observacion_archivo :Optional[str] | None ="SIN OBSERVACION"
    fecha_archivo :Optional[datetime] | None =None
    estado_archivo :Optional[int] | None =1
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico
    class Config:
        json_schema_extra = {
            "example": {
                "id_archivo":None,
                "operacion_id":1,
                "titulo_archivo":"Llenado de Furgon",
                "tipo_archivo":"FOTO",
                "link_archivo":"/pollitos/scan.jpg",
                "observacion_archivo":"Segun lo programado se procede a llenar los pollos em la unidad desdde las 8 PM",
                "fecha_archivo" : None ,
                "estado_archivo":None,
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

