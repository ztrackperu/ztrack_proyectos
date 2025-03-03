from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class PlanoSchema(BaseModel) :
    id_plano :Optional[int] | None =0
    proyecto_id : int = Field(...)
    estado_plano : Optional[int] | None =1
    nombre_plano : str = Field(...)
    descripcion_plano : Optional[str] | None ="SIN DESCRIPCION" 
    responsable_plano : str = Field(...)
    observaciones_plano : Optional[str] | None ="SIN OBSERVACIONES" 
    url_plano : str = Field(...)
    updated_at: Optional[datetime] | None =datetime.now() #generico
    created_at: Optional[datetime] | None =datetime.now() #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
                "id_plano":None,
                "proyecto_id":1,
                "estado_plano":None,
                "nombre_plano": "XL MODELO 2025 SAN FERNANDO",
                "descripcion_plano":"se considera modificaciones del cliente al 20/02/2025 ",
                "responsable_plano":"Sergio Ramirez",
                "observaciones_plano":"cambio de piso de firme a ranurado",
                "url_plano":"archivos/planos/XL_model_2025_1.pdf",
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
