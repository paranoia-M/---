import os
import sys
import time
import threading
import webbrowser
from typing import List, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, func
from pydantic import BaseModel

# 引入同级目录下的模块
import models
import database

# ==========================================
# 1. 数据库模型扩展 (SQLAlchemy Models)
# ==========================================

# 投递申请表 (用于简历收件箱)
# 注意：User 和 Job 模型定义在 models.py 中，这里扩展 Application
class Application(models.Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String)       # 学生姓名
    major = Column(String)              # 专业
    job_title = Column(String)          # 投递岗位
    enterprise_name = Column(String)    # 目标企业
    status = Column(String, default="待初筛") # 状态: 待初筛 / 待面试 / 已录用
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 自动创建所有表结构 (如果不存在)
models.Base.metadata.create_all(bind=database.engine)

# ==========================================
# 2. 数据验证模型 (Pydantic Schemas)
# ==========================================

# 登录请求
class UserLogin(BaseModel):
    username: str
    password: str

# 注册请求
class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str  # 企业名称

# 岗位创建
class JobCreate(BaseModel):
    title: str
    requirements: str
    count: int
    enterprise_name: Optional[str] = None 

# 申请创建 (学校端推送)
class AppCreate(BaseModel):
    student_name: str
    major: str
    job_title: str
    enterprise_name: str

# 申请状态更新 (企业端操作)
class AppUpdate(BaseModel):
    status: str

# ==========================================
# 3. FastAPI 应用配置
# ==========================================

app = FastAPI(title="庆阳校企对接平台")

# 配置 CORS (允许跨域，方便开发)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库会话依赖
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 4. 自动初始化演示数据 (Init Data)
# ==========================================
def init_data():
    db = database.SessionLocal()
    
    # A. 初始化默认账号 (去敏化)
    if not db.query(models.User).first():
        # 学校管理员
        db.add(models.User(username="school", hashed_password="123", full_name="庆阳职业技术学院", role="school"))
        # 默认企业
        db.add(models.User(username="company", hashed_password="123", full_name="西峰数据云创科技", role="enterprise"))
        print(">>> ✅ 账号初始化完成")
    
    # B. 初始化默认岗位
    if not db.query(models.Job).first():
        jobs = [
            {"title": "Python数据清洗专员", "req": "Pandas, NumPy", "count": 10, "ent": "西峰数据云创科技"},
            {"title": "IDC机房运维工程师", "req": "Linux, 网络基础", "count": 5, "ent": "西部算力枢纽中心"},
            {"title": "AI数据标注组长", "req": "Office, 细心", "count": 20, "ent": "智云互联科技"}
        ]
        for j in jobs:
            db.add(models.Job(title=j["title"], requirements=j["req"], count=j["count"], enterprise_name=j["ent"]))
        print(">>> ✅ 岗位初始化完成")

    # C. 初始化默认简历投递 (解决企业端 No Data 问题)
    if not db.query(Application).first():
        apps = [
            {"s": "张伟", "m": "大数据技术", "j": "Python数据清洗专员", "e": "西峰数据云创科技", "st": "待初筛"},
            {"s": "李娜", "m": "云计算应用", "j": "IDC机房运维工程师", "e": "西峰数据云创科技", "st": "待面试"},
            {"s": "王强", "m": "人工智能", "j": "Python数据清洗专员", "e": "西峰数据云创科技", "st": "待初筛"}
        ]
        for a in apps:
            db.add(Application(
                student_name=a["s"], 
                major=a["m"], 
                job_title=a["j"], 
                enterprise_name=a["e"], 
                status=a["st"]
            ))
        print(">>> ✅ 简历投递数据初始化完成")

    db.commit()
    db.close()

# 启动时执行初始化
init_data()

# ==========================================
# 5. API 接口实现
# ==========================================

# --- 认证模块 ---
@app.post("/api/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if not user or user.hashed_password != user_in.password:
        raise HTTPException(status_code=401, detail="账号或密码错误")
    return {
        "access_token": f"token-{user.id}",
        "role": user.role,
        "name": user.full_name
    }

@app.post("/api/register")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    exist_user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if exist_user:
        raise HTTPException(status_code=400, detail="该账号已被注册")
    new_user = models.User(
        username=user_in.username,
        hashed_password=user_in.password,
        full_name=user_in.full_name,
        role="enterprise"
    )
    db.add(new_user)
    db.commit()
    return {"msg": "注册成功"}

# --- 企业管理模块 ---
@app.get("/api/enterprises")
def get_enterprises(db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.role == "enterprise").all()

@app.delete("/api/enterprises/{user_id}")
def delete_enterprise(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return {"msg": "删除成功"}

# --- 岗位模块 ---
@app.get("/api/jobs")
def read_jobs(db: Session = Depends(get_db)):
    return db.query(models.Job).order_by(models.Job.created_at.desc()).all()

@app.post("/api/jobs")
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    ent_name = job.enterprise_name if job.enterprise_name else "演示发布企业"
    new_job = models.Job(
        title=job.title, 
        requirements=job.requirements, 
        count=job.count, 
        enterprise_name=ent_name
    )
    db.add(new_job)
    db.commit()
    return new_job

# --- 申请/简历模块 ---
@app.post("/api/applications")
def create_application(app: AppCreate, db: Session = Depends(get_db)):
    new_app = Application(
        student_name=app.student_name,
        major=app.major,
        job_title=app.job_title,
        enterprise_name=app.enterprise_name,
        status="待初筛"
    )
    db.add(new_app)
    db.commit()
    return new_app

@app.get("/api/applications")
def get_applications(db: Session = Depends(get_db)):
    return db.query(Application).order_by(Application.created_at.desc()).all()

@app.put("/api/applications/{app_id}")
def update_application_status(app_id: int, update: AppUpdate, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="未找到记录")
    app.status = update.status
    db.commit()
    return app

# ==========================================
# 6. 静态资源托管 (适配 EXE 打包)
# ==========================================

def resource_path(relative_path):
    """获取资源绝对路径，适配 PyInstaller 打包"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 定位前端构建产物目录
# GitHub Action 中配置的是 --add-data "frontend/dist;frontend/dist"
dist_path = resource_path(os.path.join("frontend", "dist"))

if os.path.exists(dist_path):
    print(f">>> ✅ 检测到前端静态资源，已开启 UI 托管: {dist_path}")
    # 1. 挂载 assets 目录 (js/css/img)
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
    
    # 2. 根路径 -> 返回 index.html
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(dist_path, "index.html"))
    
    # 3. 捕获所有 404 -> 返回 index.html (支持 Vue Router History 模式)
    @app.exception_handler(404)
    async def not_found(request, exc):
        return FileResponse(os.path.join(dist_path, "index.html"))
else:
    print(">>> ⚠️ 未找到前端 dist 目录，仅启动 API 服务 (本地开发请忽略)")

# ==========================================
# 7. 程序入口 (自动打开浏览器)
# ==========================================

def open_browser():
    """延迟 1.5 秒后打开浏览器"""
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # 仅在作为主脚本运行时执行 (uvicorn 命令不会触发这里)
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 启动服务 (注意：host 设为 0.0.0.0 以便防火墙放行，EXE 打包时 reload 必须为 False)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")