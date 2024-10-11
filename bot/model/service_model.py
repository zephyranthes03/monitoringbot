from datetime import datetime
from pydantic import BaseModel

class ServiceModel(BaseModel):
    host: str
    port: int
    alias: str
    time: int

class ServiceDataModel(ServiceModel):
    status: str
    last_check_time: datetime
