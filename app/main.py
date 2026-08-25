from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.user import router as user_router
from app.routers.projects import router as project_router
from app.routers.tasks import router as task_router
from app.routers.tasks import router as task_detail_router 
from app import models  # chỉ cần import package này, Python sẽ chạy __init__.py, tự đăng ký hết
from app.db.database import Base, engine
from app.utils.exceptions import exception

app =FastAPI()

exception(app)

Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(task_detail_router)