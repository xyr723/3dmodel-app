"""
应用配置管理
"""
import os
from typing import List, Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "3D模型生成API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    API_KEY: Optional[str] = None
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 数据库配置
    DATABASE_URL: Optional[str] = None
    MONGODB_URL: Optional[str] = None
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # 第三方API配置
    MESHY_API_KEY: Optional[str] = None
    MESHY_API_URL: str = "https://api.meshy.ai"
    OPENAI_API_KEY: Optional[str] = None
    
    # 模型配置
    MODEL_PROVIDER: str = "meshy"  # meshy, local, openai
    MAX_GENERATION_TIME: int = 300  # 秒
    MAX_FILE_SIZE: int = 100  # MB
    SUPPORTED_FORMATS: List[str] = ["obj", "glb", "ply", "fbx"]
    
    # 存储配置
    STORAGE_TYPE: str = "local"  # local, s3, gcs
    STORAGE_PATH: str = "./storage"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # 缓存配置
    CACHE_TTL: int = 3600  # 秒
    CACHE_MAX_SIZE: int = 1000  # 最大缓存条目数
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/app.log"
    
    # 限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()


def get_database_url() -> str:
    """获取数据库连接URL"""
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    elif settings.MONGODB_URL:
        return settings.MONGODB_URL
    else:
        # 默认SQLite数据库 - 使用异步驱动
        return "sqlite+aiosqlite:///./app.db"


def get_storage_config() -> dict:
    """获取存储配置"""
    if settings.STORAGE_TYPE == "s3":
        return {
            "type": "s3",
            "access_key": settings.AWS_ACCESS_KEY_ID,
            "secret_key": settings.AWS_SECRET_ACCESS_KEY,
            "bucket": settings.AWS_BUCKET_NAME,
            "region": settings.AWS_REGION
        }
    elif settings.STORAGE_TYPE == "gcs":
        return {
            "type": "gcs",
            "bucket": settings.AWS_BUCKET_NAME  # 重用配置
        }
    else:
        return {
            "type": "local",
            "path": settings.STORAGE_PATH
        }


def validate_config():
    """验证配置的有效性"""
    errors = []
    
    # 检查必需的API密钥
    if settings.MODEL_PROVIDER == "meshy" and not settings.MESHY_API_KEY:
        errors.append("MESHY_API_KEY is required when using meshy provider")
    
    if settings.MODEL_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required when using openai provider")
    
    # 检查存储配置
    if settings.STORAGE_TYPE == "s3":
        if not all([settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, settings.AWS_BUCKET_NAME]):
            errors.append("AWS credentials and bucket name are required for S3 storage")
    
    # 检查数据库配置
    if not any([settings.DATABASE_URL, settings.MONGODB_URL]):
        print("Warning: No database URL configured, using SQLite by default")
    
    if errors:
        raise ValueError("Configuration errors: " + "; ".join(errors))
    
    return True
