from typing import Optional,List,Union,Dict
from datetime import  datetime
from pydantic import BaseModel, Field

class ReProyectoDerivadoSchema(BaseModel) :
    #id_re_proyecto_derivado:Optional[int] | None =0
    pre_proyecto_id :int = Field(...)
    #conjunto : List[Union[int, str]] =Field(...)
    suma_valor_pre_proyecto : Optional[int] | None =0 #generico
    conjunto: Optional[List[Dict[str, int]]] = []
    token_proyecto : Optional[str] | None ="blablabla"
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
                #"id_re_proyecto_derivado":None,
                "suma_valor_pre_proyecto":0,
                "pre_proyecto_id":0,
                #"conjunto" :[{"pre_derivado_id":1,"cantidad":2},{"pre_derivado_id":3,"cantidad":1}]
                #"conjunto" :[{"pre_derivado_id":1,"cantidad":2},{"pre_derivado_id":3,"cantidad":1}],
                "conjunto" :[{"pre_derivado_id":1,"valor_pre_derivado":2},{"pre_derivado_id":3,"valor_pre_derivado":1}],

                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "created_at":None,
                "user_c":0
            }
        }

class ReProyectoDerivadoEditarSchema(BaseModel) :
    #id_re_proyecto_derivado:Optional[int] | None =0
    pre_proyecto_id :int = Field(...)
    #conjunto : List[Union[int, str]] =Field(...)
    #suma_valor_pre_proyecto : Optional[int] | None =0 #generico
    conjunto: Optional[List[Dict[str, int]]] = []
    token_proyecto : Optional[str] | None ="blablabla"
    created_at: Optional[datetime] | None =None #generico
    user_c:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
                #"id_re_proyecto_derivado":None,
                #"suma_valor_pre_proyecto":0,
                "pre_proyecto_id":0,
                #"conjunto" :[{"pre_derivado_id":1,"cantidad":2},{"pre_derivado_id":3,"cantidad":1}]
                #"conjunto" :[{"pre_derivado_id":1,"cantidad":2},{"pre_derivado_id":3,"cantidad":1}],
                "conjunto" :[{"id_re_proyecto_derivado":2,"pre_derivado_id":1,"valor_pre_derivado":2},{"id_re_proyecto_derivado":3,"pre_derivado_id":3,"valor_pre_derivado":1}],

                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "created_at":None,
                "user_c":0
            }
        }

class ConsultarSchema(BaseModel):
    id_usuario: Optional[int] | None =0
    tipo_usuario: Optional[int] | None =0
    token_proyecto : Optional[str] | None ="blablabla"
    especifico_proyecto: Optional[int] | None =0
    especifico_derivado: Optional[int] | None =None
    especifico_id: Optional[int] | None =None

    #fecha_inicio: Optional[str] | None=None
    #fecha_fin: Optional[str] | None =None
    class Config:
        json_schema_extra = {
            "example": {
                "id_usuario": 0,
                "tipo_usuario": 0,
                "token_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5",
                "especifico_proyecto" :0,
                "especifico_derivado" :0,
                "especifico_id":0
                #"fecha_inicio" :None,
                #"fecha_fin" :None
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

