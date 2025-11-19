from pydantic import BaseModel
from datetime import datetime

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str

# 新增
class JobCreate(BaseModel):
    title: str
    requirements: str
    count: int

class JobOut(BaseModel):
    id: int
    title: str
    requirements: str
    count: int
    enterprise_name: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True