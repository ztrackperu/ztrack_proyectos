from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ProyectosSchema(BaseModel) :
    id_proyecto:Optional[int] | None =0
    cotizacion_proyecto :str = Field(...)
    cliente_proyecto :str = Field(...)
    fecha_solicitud_proyecto: Optional[datetime] | None =None
    fecha_limite_proyecto: Optional[datetime] | None =None
    nombre_proyecto :str = Field(...)
    observaciones_proyecto :str = Field(...)
    encargado_proyecto :str = Field(...)
    prioridad_proyecto :str = Field(...)
    url_proyecto :Optional[str]| None ="proyectos/proyectogenerico"
    estado_proyecto:Optional[int] | None =1
    progreso_proyecto:Optional[int] | None =0
    user_cierra_proyecto :Optional[int] | None =0 
    fecha_cierra_proyecto : Optional[datetime] | None =None
    cantidad_derivados :Optional[int] | None =0 
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =None #generico
    user_m:Optional[int] | None =None #generico
    class Config:
        json_schema_extra = {
            "example": {
            "id_proyecto":None,
            "cotizacion_proyecto": "10020250451",
            "cliente_proyecto":"FRANK DONIO - ZGROUP USA ",
            "fecha_solicitud_proyecto":None,
            "fecha_limite_proyecto":None,
            "nombre_proyecto":"40RH BLAST CHILLER 2XL CON CARACTERISTICAS DE MADURADOR",
            "observaciones_proyecto":"Piso plano 5 máquinas Reefer nuevas MAGNUM PLUS MP4000 (4 reefer y 1 madurador ambos con sistema de aire forzado)",
            "encargado_proyecto":"JHON TELLO ARIAS",
            "prioridad_proyecto":"ALTA",
            "url_proyecto":"proyecto/proyecto30/",
            "estado_proyecto":None,
            "progreso_proyecto":None,
            "user_cierra_proyecto":None,
            "fecha_cierra_proyecto":None,
            "cantidad_derivados":None,
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

