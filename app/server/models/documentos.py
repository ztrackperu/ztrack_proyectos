from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class DocumentoSchema(BaseModel) :
    id_documento :Optional[int] | None =0
    proyecto_id : int = Field(...)
    estado_documento : Optional[int] | None =1
    nombre_documento : str = Field(...)
    descripcion_documento : Optional[str] | None ="SIN DESCRIPCION" 
    responsable_documento : str = Field(...)
    observaciones_documento : Optional[str] | None ="SIN OBSERVACIONES" 
    url_documento : str = Field(...)
    updated_at: Optional[datetime] | None =datetime.now() #generico
    created_at: Optional[datetime] | None =datetime.now() #generico
    user_c:Optional[int] | None =0 #generico
    user_m:Optional[int] | None =0 #generico

    class Config:
        json_schema_extra = {
            "example": {
                "id_documento":None,
                "proyecto_id":1,
                "estado_documento":None,
                "nombre_documento": "SCTR FEBRERO 2025",
                "descripcion_documento":"Seguro contra accidentes de trabajadores en febrero ",
                "responsable_documento":"Angie chipana",
                "observaciones_documento":"Documento imortante para todos los servicios",
                "url_documento":"archivos/documentos/SCTR_02_2025.pdf",
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
