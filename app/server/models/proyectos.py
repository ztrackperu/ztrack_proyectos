from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ProyectosSchema(BaseModel) :
    id_proyecto:Optional[int] | None =0
    cotizacion_proyecto :str = Field(...)
    cliente_proyecto :str = Field(...)
    activar_reportar:Optional[int] | None =1
    fecha_solicitud_proyecto: Optional[datetime] | None =datetime.now()
    fecha_limite_proyecto: Optional[datetime] | None =datetime.now()
    nombre_proyecto :str = Field(...)
    observaciones_proyecto :str = Field(...)
    encargado_proyecto :str = Field(...)
    prioridad_proyecto :str = Field(...)
    url_proyecto :str | None= "test"
    estado_proyecto:Optional[int] | None =1
    progreso_proyecto:Optional[int] | None =0
    updated_at: Optional[datetime] | None =datetime.now()
    created_at: Optional[datetime] | None =datetime.now()
    user_c:Optional[int] | None =0
    user_m:Optional[int] | None =0
    class Config:
        json_schema_extra = {
            "example": {
            "id_proyecto":0,
            "cotizacion_proyecto": "10020250451",
            "cliente_proyecto":"FRANK DONIO - ZGROUP USA ",
            "activar_reportar":1,
            "fecha_solicitud_proyecto":None,
            "fecha_limite_proyecto":None,
            "nombre_proyecto":"40RH BLAST CHILLER 2XL CON CARACTERISTICAS DE MADURADOR",
            "observaciones_proyecto":"Piso plano 5 máquinas Reefer nuevas MAGNUM PLUS MP4000 (4 reefer y 1 madurador ambos con sistema de aire forzado)",
            "encargado_proyecto":"JHON TELLO ARIAS",
            "prioridad_proyecto":"ALTA",
            "estado_proyecto":1,
            "progreso_proyecto":0,
            "url_proyecto":"test/test.jpg",
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

