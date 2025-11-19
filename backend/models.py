from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String)

# 新增：岗位需求表
class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)          # 岗位名称
    requirements = Column(String)   # 技能要求
    count = Column(Integer)         # 招聘人数
    enterprise_name = Column(String) # 发布企业名称
    status = Column(String, default="active") # active / closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())