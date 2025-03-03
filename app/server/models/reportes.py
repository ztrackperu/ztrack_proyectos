from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ReporteSchema(BaseModel) :
    id_reporte :Optional[int] | None =0
    actividad_id : int = Field(...)
    nombre_reporte : str = Field(...)
    descripcion_reporte : str = Field(...)
    estado_reporte : Optional[int] | None = 1
    observaciones_reporte : Optional[str] | None ="SIN OBSERVACIONES"
    cantidad_fotos_reporte : Optional[int] | None = 0
    updated_at: Optional[datetime] | None =datetime.now() #generico
    created_at: Optional[datetime] | None =datetime.now() #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
            "id_reporte":None,
            "actividad_id":1,
            "nombre_reporte": "Soldaduro de esquina izquierda ",
            "descripcion_reporte":"Se unen los angulos para las bases de piso por el señor wilmer ortega ",
            "observaciones_reporte":"todo correcto ",
            "cantidad_fotos_reporte": 3,
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

