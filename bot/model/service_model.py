from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    """ObjectId를 문자열로 변환하는 커스텀 타입"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise TypeError('ObjectId가 아닙니다.')
        return str(v)
    
class ServiceModel(BaseModel):
    #id: PyObjectId
    chat_id: int
    host: str
    port: int
    alias: str
    interval: int

    # class Config:
    #     arbitrary_types_allowed = True  # 임의 타입 허용

class ServiceDataModel(ServiceModel):
    status: str
    next_check_time: datetime
    last_check_time: datetime
