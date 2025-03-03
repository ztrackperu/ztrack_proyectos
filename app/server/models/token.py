from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class TokenSchema(BaseModel) :
    id_token :Optional[int] | None =0
    usuario_id :Optional[int] | None =1 
    token_proyecto :  str = Field(...)
    estado_token : Optional[int] | None =1 
    fecha_inicio: Optional[datetime] | None =datetime.now() #generico
    fecha_fin : Optional[datetime] | None =datetime.now() #generico

    class Config:
        json_schema_extra = {
            "example": {
            "id_token":None,
            "usuario_id":1,
            "token_proyecto":"xyz123456789zyz",
            "estado_token":None,
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

