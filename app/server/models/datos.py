from typing import Optional,List
from datetime import  datetime
from pydantic import BaseModel, Field





class DatosSchema(BaseModel):
    id :str = Field(...)
    IMEI :str = Field(...)
    time: str = Field(...)
    humidity: float = Field(...)
    temperature: float = Field(...)
    EC: float = Field(...)
    PH: float = Field(...)
    N: float = Field(...)
    P: float = Field(...)
    K: float = Field(...)
    power: float = Field(...)
    estado: Optional[float] | None =1
    #fecha: Optional[datetime] | None =datetime.now()
    #size: Optional[int] | None =3200
    class Config:
        json_schema_extra = {
            "example": {
            "id":"10000009",
            "IMEI":"860262050303481",
            "time":"2024/05/21 15:51:34",
            "humidity":0.00,
            "temperature":0.00,
            "EC":0.00,
            "PH":0.00,
            "N":0.00,
            "P":0.00,
            "K":0.00,
            "power":3.95}
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

