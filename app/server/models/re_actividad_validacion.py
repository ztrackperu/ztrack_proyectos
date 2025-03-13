from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class ValidacionEditarSchema(BaseModel):
    id_re_actividad_validacion: Optional[int] = None
    pre_validacion_id: Optional[int] = None
    unidad_pre_validacion : Optional[str] = "UNIDADES"
    valor_pre_validacion: Optional[int] = None
    rango_pre_validacion: Optional[List[int]] = [0,1]  # Lista de enteros

class ValidacionSchema(BaseModel):
    pre_validacion_id: Optional[int] = None
    unidad_pre_validacion : Optional[str] = "UNIDADES"
    valor_pre_validacion: Optional[int] = None
    rango_pre_validacion: Optional[List[int]] = []  # Lista de enteros

class ReActividadValidacionSchema(BaseModel) :
    pre_actividad_id :int = Field(...)
    estado_re_actividad_validacion:Optional[int] | None =1
    suma_valor_pre_actividad : Optional[int] | None =0 #generico
    conjunto: Optional[List[ValidacionSchema]] = []
    token_proyecto : Optional[str] | None ="blablabla"
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    class Config:
        json_schema_extra = {
            "example": {
                "pre_actividad_id":0,
                "estado_re_actividad_validacion":None,
                "suma_valor_pre_actividad":0,
                "conjunto" :[{"pre_validacion_id":1,"unidad_pre_validacion":"milimetros","valor_pre_validacion":2,"rango_pre_validacion":[0,2]},
                {"pre_validacion_id":3,"unidad_pre_validacion":"grados","valor_pre_validacion":1,"rango_pre_validacion":[0,5]}],
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "created_at":None,
                "user_c":0
            }
        }

class ReDerivadoActividadEditarSchema(BaseModel) :
    pre_actividad_id :int = Field(...)
    conjunto: Optional[List[ValidacionEditarSchema]] = []
    token_proyecto : Optional[str] | None ="blablabla"
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico
    class Config:
        json_schema_extra = {
            "example": {
                "pre_actividad_id":0,
                "conjunto" :[{"id_re_actividad_validacion":1 ,"pre_validacion_id":1,"unidad_pre_validacion":"milimetros","valor_pre_validacion":2,"rango_pre_validacion":[0,2]},
                {"id_re_actividad_validacion":2 ,"pre_validacion_id":3,"unidad_pre_validacion":"grados","valor_pre_validacion":1,"rango_pre_validacion":[0,5]}],
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "created_at":None,
                "user_c":0
            }
        }

class ConsultarSchema(BaseModel):
    id_usuario: Optional[int] | None =0
    tipo_usuario: Optional[int] | None =0
    token_proyecto : Optional[str] | None ="blablabla"
    especifico_id: Optional[int] | None =0
    especifico_actividad: Optional[int] | None =0
    especifico_validacion: Optional[int] | None =0
    fecha_inicio: Optional[datetime] | None=None
    fecha_fin: Optional[datetime] | None =None
    class Config:
        json_schema_extra = {
            "example": {
                "id_usuario": 0,
                "tipo_usuario": 0,
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "especifico_id" :0,
                "especifico_actividad" :0,
                "especifico_validacion" :0,
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

