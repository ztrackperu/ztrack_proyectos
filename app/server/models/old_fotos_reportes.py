from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field

class FotosReportesSchema(BaseModel) :
    id_foto_reporte:Optional[int] | None =0
    link_foto_reporte :str = Field(...)
    reporte_id : int = Field(...)
    nombre_foto_reporte :str = Field(...)
    estado_foto_reporte: Optional[int] | None =1
    fecha_foto_reporte :  Optional[datetime] | None =datetime.now()
    updated_at: Optional[datetime] | None =datetime.now()
    created_at: Optional[datetime] | None =datetime.now()
    user_c:Optional[int] | None =0
    user_m:Optional[int] | None =0
    class Config:
        json_schema_extra = {
            "example": {
            "id_fotos_reportes":0,
            "link_foto_reporte": "/referencia/proyectos/fotosreportes/2_120230.jpg",
            "reporte_id":0,
            "nombre_foto_reporte":"2_120230.jpg",
            "estado_foto_reporte":1,
            "fecha_foto_reporte":None,
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

