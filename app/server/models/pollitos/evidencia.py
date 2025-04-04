from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class EvidenciaSchema(BaseModel):
    id_evidencia: Optional[int] | None = 0
    tipo_entidad: str = Field(...)  # "operacion" o "control"
    entidad_id: int = Field(...)  # id_operacion o id_control según tipo_entidad
    titulo_evidencia: str = Field(...)
    ubicacion_evidencia: Optional[str] | None = None
    temperatura_evidencia: Optional[str] | None = None
    parametro_1_evidencia: Optional[str] | None = None
    observacion_evidencia: Optional[str] | None = "SIN OBSERVACION"
    link_evidencia: str = Field(...)  # URL o ruta al archivo
    fecha_evidencia: Optional[datetime] | None = None
    estado_evidencia: Optional[int] | None = 1
    updated_at: Optional[datetime] | None = None
    created_at: Optional[datetime] | None = None
    user_c: Optional[int] | None = 0
    user_m: Optional[int] | None = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_evidencia": None,
                "tipo_entidad": "operacion",  # o "control"
                "entidad_id": 1,
                "titulo_evidencia": "POLLO ALEATORIO SECTOR 1",
                "ubicacion_evidencia": "IZQUIERDA SUPERIOR",
                "temperatura_evidencia": "30.5 C°",
                "parametro_1_evidencia": None,
                "observacion_evidencia": None,
                "link_evidencia": "https://ejemplo.com/imagen.jpg",  # URL externa
                "fecha_evidencia": None,
                "estado_evidencia": None,
                "created_at": None,
                "updated_at": None,
                "user_c": None,
                "user_m": None
            }
        }

class ConsultarSchema(BaseModel):
    id_usuario: int = Field(...)
    especifico: Optional[int] = None
    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    tipo_entidad: Optional[str] = None  # Para filtrar por "operacion" o "control"
    entidad_id: Optional[int] = None    # Para filtrar por ID de operación o control
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_usuario": 1,
                "especifico": 0,
                "fecha_inicio": None,
                "fecha_fin": None,
                "tipo_entidad": None,
                "entidad_id": None
            }
        }

# Respuesta cuando todo está bien
def ResponseModel(data, message):
    return {
        "data": data,
        "code": 200,
        "message": message,
    }

# Respuesta cuando algo sale mal
def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
