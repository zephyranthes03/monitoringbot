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
    
class UserModel(BaseModel):
    #id: PyObjectId
    chat_id: str
    host_cnt: int
    user_type: str


