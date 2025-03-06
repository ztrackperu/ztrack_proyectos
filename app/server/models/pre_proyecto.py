from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class PreProyectosSchema(BaseModel) :
    id_pre_proyecto:Optional[int] | None =0
    nombre_pre_proyecto :str = Field(...)
    observaciones_pre_proyecto :str = Field(...)
    estado_pre_proyecto:Optional[int] | None =1
    cantidad_pre_derivados :Optional[int] | None =0 
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =None #generico
    user_m:Optional[int] | None =None #generico
    class Config:
        json_schema_extra = {
            "example": {
            "id_pre_proyecto":None,
            "nombre_pre_proyecto":"40RH BLAST CHILLER 2XL CON CARACTERISTICAS DE MADURADOR",
            "observaciones_pre_proyecto":"Piso plano 5 máquinas Reefer nuevas MAGNUM PLUS MP4000 (4 reefer y 1 madurador ambos con sistema de aire forzado)",
            "estado_pre_proyecto":None,
            "cantidad_pre_derivados":None,
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

