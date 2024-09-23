from pydantic import BaseModel

class MonitorModel(BaseModel):
    delay: int

