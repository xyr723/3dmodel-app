"""
3D模型生成应用的FastAPI主入口
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.api import generate, evaluate
from app.core.config import settings
from app.utils.logger import logger
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    # 启动时初始化数据库
    logger.info("正在初始化数据库连接...")
    await init_db()
    logger.info("应用启动完成")
    
    yield
    
    # 关闭时清理资源
    logger.info("应用正在关闭...")


# 创建FastAPI实例
app = FastAPI(
    title="3D模型生成API",
    description="基于AI的3D模型生成和评估服务",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"全局异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误", "detail": str(exc)}
    )


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "message": "服务运行正常"}


# 注册路由
app.include_router(generate.router, prefix="/api", tags=["生成"])
app.include_router(evaluate.router, prefix="/api", tags=["评估"])


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
