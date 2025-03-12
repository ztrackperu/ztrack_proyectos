from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field


class ActividadEditarSchema(BaseModel):
    id_re_derivado_actividad: Optional[int] = None
    pre_actividad_id: Optional[int] = None
    valor_pre_actividad: Optional[int] = None
    requisito_pre_actividad: Optional[List[int]] = []  # Lista de enteros

class ActividadSchema(BaseModel):
    #temas_actividad_id: Optional[str] = None
    pre_actividad_id: Optional[int] = None
    valor_pre_actividad: Optional[int] = None
    requisito_pre_actividad: Optional[List[int]] = []  # Lista de enteros

class ReDerivadoActividadSchema(BaseModel) :
    pre_derivado_id :int = Field(...)
    estado_re_derivado_actividad:Optional[int] | None =1
    suma_valor_pre_derivado : Optional[int] | None =0 #generico
    conjunto: Optional[List[ActividadSchema]] = []
    token_proyecto : Optional[str] | None ="blablabla"
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    class Config:
        json_schema_extra = {
            "example": {
                "pre_derivado_id":0,
                "suma_valor_pre_derivada":None,
                "suma_valor_pre_proyecto":0,
                "conjunto" :[{"pre_actividad_id":1,"valor_pre_actividad":2,"requisito_pre_actividad":[2,4]},{"pre_derivado_id":3,"valor_pre_derivado":1,"requisito_pre_actividad":[]}],
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "created_at":None,
                "user_c":0
            }
        }

class ReDerivadoActividadEditarSchema(BaseModel) :
    pre_derivado_id :int = Field(...)
    conjunto: Optional[List[ActividadEditarSchema]] = []
    token_proyecto : Optional[str] | None ="blablabla"
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
                "pre_derivado_id":0,
                "conjunto" :[{"id_re_derivado_actividad":2,"pre_derivado_id":1,"valor_pre_derivado":2,"requisito_pre_actividad":[]},{"id_re_derivado_actividad":3,"pre_derivado_id":3,"valor_pre_derivado":1,"requisito_pre_actividad":[]}],
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "created_at":None,
                "user_c":0
            }
        }


class ConsultarSchema(BaseModel):
    id_usuario: Optional[int] | None =0
    tipo_usuario: Optional[int] | None =0
    token_proyecto : Optional[str] | None ="blablabla"
    especifico_actividad: Optional[int] | None =0
    especifico_derivado: Optional[int] | None =0
    fecha_inicio: Optional[datetime] | None=None
    fecha_fin: Optional[datetime] | None =None
    class Config:
        json_schema_extra = {
            "example": {
                "id_usuario": 0,
                "tipo_usuario": 0,
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "especifico_actividad" :0,
                "especifico_derivado" :0,
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


