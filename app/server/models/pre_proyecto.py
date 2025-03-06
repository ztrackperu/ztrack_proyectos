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
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =None #generico
    class Config:
        json_schema_extra = {
            "example": {
            "id_pre_proyecto":None,
            "nombre_pre_proyecto":"40RH BLAST CHILLER 2XL CON CARACTERISTICAS DE MADURADOR",
            "observaciones_pre_proyecto":"Piso plano 5 máquinas Reefer nuevas MAGNUM PLUS MP4000 (4 reefer y 1 madurador ambos con sistema de aire forzado)",
            "estado_pre_proyecto":None,
            "cantidad_pre_derivados":None,
            "token_proyecto":"0f2adb0aee3de894ac4e28bf",
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
    fecha_inicio: Optional[datetime] | None=None
    fecha_fin: Optional[datetime] | None =None
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

