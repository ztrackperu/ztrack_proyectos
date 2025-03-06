from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class DerivadosSchema(BaseModel) :
    id_derivado:Optional[int] | None =0
    proyecto_id:Optional[int] | None =0
    activar_reportar:Optional[int] | None =1
    fecha_inicio_derivado: Optional[datetime] | None =None
    fecha_fin_derivado: Optional[datetime] | None =None
    nombre_derivado :str = Field(...)
    observaciones_derivado :str = Field(...)
    encargado_derivado :str = Field(...)
    estado_derivado:Optional[int] | None =1
    progreso_derivado:Optional[int] | None =0
    valor_derivado:Optional[int] | None =0
    user_cierra_derivado :Optional[int] | None =0 
    fecha_cierra_derivado : Optional[datetime] | None =None
    cantidad_actividades :Optional[int] | None =0 
    updated_at: Optional[datetime] | None =None #generico
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico
    class Config:
        json_schema_extra = {
            "example": {
            "id_derivado":None,
            "proyecto_id":0,
            "activar_reportar":None,
            "fecha_inicio_derivado":None,
            "fecha_fin_derivado":None,
            "nombre_derivado":"XL 40 PIES LADO DERECHO",
            "observaciones_derivado":"Piso plano SIN MAQUINA",
            "encargado_derivado":"JHON TELLO ARIAS",
            "estado_derivado":None,
            "progreso_derivado":None,
            "valor_derivado":None,
            "user_cierra_derivado":None,
            "fecha_cierra_derivado":None,
            "cantidad_actividades":None,
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

