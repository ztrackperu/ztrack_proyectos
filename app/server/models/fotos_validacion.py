from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class FotoValidacionSchema(BaseModel) :
    id_foto_validacion :Optional[int] | None =0
    validacion_id : int = Field(...)
    url_foto_validacion : str = Field(...)
    estado_foto_validacion :Optional[int] | None =1 
    updated_at: Optional[datetime] | None =datetime.now() #generico
    created_at: Optional[datetime] | None =datetime.now() #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
            "id_foto_validacion":None,
            "validacion_id":1,
            "url_foto_validacion": "fotos/validacion/inclinacion_piso.png",
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

