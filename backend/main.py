import os
import sys
import time
import threading
import webbrowser
from typing import List, Optional
from datetime import datetime

# 第三方库
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, func
from pydantic import BaseModel

# 本地模块 (使用绝对导入，配合 build.yml 中的 --paths "backend")
import models
import database

# ==========================================
# 1. 数据库模型扩展 (SQLAlchemy Models)
# ==========================================

# 投递申请表
class Application(models.Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String)
    major = Column(String)
    job_title = Column(String)
    enterprise_name = Column(String)
    status = Column(String, default="待初筛")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 自动建表
models.Base.metadata.create_all(bind=database.engine)

# ==========================================
# 2. 数据验证模型 (Pydantic Schemas)
# ==========================================

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str

class JobCreate(BaseModel):
    title: str
    requirements: str
    count: int
    enterprise_name: Optional[str] = None 

class AppCreate(BaseModel):
    student_name: str
    major: str
    job_title: str
    enterprise_name: str

class AppUpdate(BaseModel):
    status: str

# ==========================================
# 3. FastAPI 应用配置
# ==========================================

app = FastAPI(title="庆阳校企对接平台")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库依赖
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 4. 自动初始化数据 (数据去敏化)
# ==========================================
def init_data():
    db = database.SessionLocal()
    
    # A. 初始化账号
    if not db.query(models.User).first():
        db.add(models.User(username="school", hashed_password="123", full_name="庆阳职业技术学院", role="school"))
        db.add(models.User(username="company", hashed_password="123", full_name="西峰数据云创科技", role="enterprise"))
        print(">>> ✅ 账号初始化完成")
    
    # B. 初始化岗位
    if not db.query(models.Job).first():
        jobs = [
            {"title": "Python数据清洗专员", "req": "Pandas, NumPy", "count": 10, "ent": "西峰数据云创科技"},
            {"title": "IDC机房运维工程师", "req": "Linux, 网络基础", "count": 5, "ent": "西部算力枢纽中心"},
            {"title": "AI数据标注组长", "req": "Office, 细心", "count": 20, "ent": "智云互联科技"}
        ]
        for j in jobs:
            db.add(models.Job(title=j["title"], requirements=j["req"], count=j["count"], enterprise_name=j["ent"]))
        print(">>> ✅ 岗位初始化完成")

    # C. 初始化简历
    if not db.query(Application).first():
        apps = [
            {"s": "张伟", "m": "大数据技术", "j": "Python数据清洗专员", "e": "西峰数据云创科技", "st": "待初筛"},
            {"s": "李娜", "m": "云计算应用", "j": "IDC机房运维工程师", "e": "西峰数据云创科技", "st": "待面试"},
            {"s": "王强", "m": "人工智能", "j": "Python数据清洗专员", "e": "西峰数据云创科技", "st": "待初筛"}
        ]
        for a in apps:
            db.add(Application(student_name=a["s"], major=a["m"], job_title=a["j"], enterprise_name=a["e"], status=a["st"]))
        print(">>> ✅ 简历数据初始化完成")

    db.commit()
    db.close()

init_data()

# ==========================================
# 5. API 接口
# ==========================================

@app.post("/api/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if not user or user.hashed_password != user_in.password:
        raise HTTPException(status_code=401, detail="账号或密码错误")
    return {"access_token": f"token-{user.id}", "role": user.role, "name": user.full_name}

@app.post("/api/register")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    exist = db.query(models.User).filter(models.User.username == user_in.username).first()
    if exist: raise HTTPException(status_code=400, detail="账号已存在")
    new_user = models.User(username=user_in.username, hashed_password=user_in.password, full_name=user_in.full_name, role="enterprise")
    db.add(new_user)
    db.commit()
    return {"msg": "注册成功"}

@app.get("/api/enterprises")
def get_enterprises(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == "enterprise").all()

@app.delete("/api/enterprises/{user_id}")
def delete_enterprise(user_id: int, db: Session = Depends(get_db)):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return {"msg": "删除成功"}

@app.get("/api/jobs")
def read_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).order_by(models.Job.created_at.desc()).all()

@app.post("/api/jobs")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    ent_name = job.enterprise_name if job.enterprise_name else "演示发布企业"
    new_job = models.Job(title=job.title, requirements=job.requirements, count=job.count, enterprise_name=ent_name)
    db.add(new_job)
    db.commit()
    return new_job

@app.post("/api/applications")
def create_app(app: AppCreate, db: Session = Depends(get_db)):
    new_app = Application(student_name=app.student_name, major=app.major, job_title=app.job_title, enterprise_name=app.enterprise_name)
    db.add(new_app)
    db.commit()
    return new_app

@app.get("/api/applications")
def get_apps(db: Session = Depends(get_db)):
    return db.query(Application).order_by(Application.created_at.desc()).all()

@app.put("/api/applications/{app_id}")
def update_app(app_id: int, update: AppUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app: raise HTTPException(status_code=404, detail="记录不存在")
    app.status = update.status
    db.commit()
    return app

# ==========================================
# 6. 静态资源托管 (适配 PyInstaller)
# ==========================================

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

dist_path = resource_path(os.path.join("frontend", "dist"))

if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
    
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(dist_path, "index.html"))
        
    @app.exception_handler(404)
    async def not_found(request, exc):
        return FileResponse(os.path.join(dist_path, "index.html"))

# ==========================================
# 7. 程序入口 (关键：修复无控制台崩溃)
# ==========================================

def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # 1. 修复 PyInstaller --noconfirm --windowed 模式下 stdout/stderr 为 None 导致的崩溃
    if sys.stdout is None:
        sys.stdout = open(os.devnull, "w")
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w")

    # 2. 启动浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 3. 启动服务 (log_config=None 是必须的，否则打包后还会报错)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)