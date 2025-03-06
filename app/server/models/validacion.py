from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ValidacionSchema(BaseModel) :
    id_validacion :Optional[int] | None =0
    actividad_id : int = Field(...)
    nombre_validacion : str = Field(...)
    descripcion_validacion : str = Field(...)
    estado_validacion :Optional[int] | None =1
    observaciones_validacion : Optional[str] | None ="SIN OBSERVACIONES"
    estandar_validacion : str = Field(...)
    dato_validacion : str = Field(...)
    evaluacion_validacion : Optional[int] | None = 0
    comentarios_validacion : Optional[str] | None ="SIN COMENTARIOS"
    cantidad_fotos_validacion : Optional[int] | None = 0
    updated_at: Optional[datetime] | None =datetime.now() #generico
    created_at: Optional[datetime] | None =datetime.now() #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
            "id_validacion":None,
            "actividad_id":1,
            "nombre_validacion": "MEDICIONES DE NIVEL DE PISO -LADO VERTICAL 1 ",
            "descripcion_validacion":"Se valida los grados de inclinacion /elevacion del piso  ",
            "observaciones_validacion":"todo correcto ",
            "estandar_validacion":[-1,1],
            "dato_validacion":0.3,
            "evaluacion_validacion":None,
            "comentarios_validacion":None,
            "cantidad_fotos_validacion": 3,
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

