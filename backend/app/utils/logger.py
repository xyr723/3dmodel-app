"""
日志配置和管理
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional

from app.core.config import settings


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class LoggerManager:
    """日志管理器"""
    
    def __init__(self):
        self._loggers = {}
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """设置根日志记录器"""
        # 创建日志目录
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
        
        # 清除现有处理器
        root_logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # 文件处理器（轮转）
        if settings.LOG_FILE:
            file_handler = logging.handlers.RotatingFileHandler(
                settings.LOG_FILE,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
            file_formatter = logging.Formatter(settings.LOG_FORMAT)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        # 错误文件处理器
        error_log_file = settings.LOG_FILE.replace('.log', '_error.log') if settings.LOG_FILE else 'logs/error.log'
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        error_handler.setFormatter(error_formatter)
        root_logger.addHandler(error_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取指定名称的日志记录器
        
        Args:
            name: 日志记录器名称
        
        Returns:
            logging.Logger: 日志记录器实例
        """
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def set_level(self, level: str):
        """
        设置日志级别
        
        Args:
            level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        """
        log_level = getattr(logging, level.upper())
        logging.getLogger().setLevel(log_level)
        
        # 更新所有处理器的级别
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                handler.setLevel(logging.INFO)
            else:
                handler.setLevel(log_level)


# 全局日志管理器实例
logger_manager = LoggerManager()

# 默认日志记录器
logger = logger_manager.get_logger('3dmodel-app')


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器的便捷函数
    
    Args:
        name: 日志记录器名称
    
    Returns:
        logging.Logger: 日志记录器实例
    """
    return logger_manager.get_logger(name)


def log_request(request_id: str, method: str, url: str, user_agent: Optional[str] = None):
    """
    记录请求日志
    
    Args:
        request_id: 请求ID
        method: HTTP方法
        url: 请求URL
        user_agent: 用户代理
    """
    logger.info(
        f"REQUEST [{request_id}] {method} {url} - UA: {user_agent or 'Unknown'}"
    )


def log_response(request_id: str, status_code: int, processing_time: float):
    """
    记录响应日志
    
    Args:
        request_id: 请求ID
        status_code: HTTP状态码
        processing_time: 处理时间（秒）
    """
    logger.info(
        f"RESPONSE [{request_id}] {status_code} - {processing_time:.3f}s"
    )


def log_error(error: Exception, context: Optional[dict] = None):
    """
    记录错误日志
    
    Args:
        error: 异常对象
        context: 上下文信息
    """
    error_msg = f"ERROR: {str(error)}"
    if context:
        error_msg += f" - Context: {context}"
    
    logger.error(error_msg, exc_info=True)


def log_model_generation(task_id: str, prompt: str, status: str, processing_time: Optional[float] = None):
    """
    记录模型生成日志
    
    Args:
        task_id: 任务ID
        prompt: 生成提示词
        status: 任务状态
        processing_time: 处理时间
    """
    msg = f"MODEL_GEN [{task_id}] '{prompt[:50]}...' - Status: {status}"
    if processing_time:
        msg += f" - Time: {processing_time:.2f}s"
    
    if status == "completed":
        logger.info(msg)
    elif status == "failed":
        logger.error(msg)
    else:
        logger.info(msg)


def log_cache_operation(operation: str, cache_key: str, hit: bool = None):
    """
    记录缓存操作日志
    
    Args:
        operation: 操作类型（get, set, delete）
        cache_key: 缓存键
        hit: 是否命中（仅对get操作有效）
    """
    if operation == "get":
        result = "HIT" if hit else "MISS"
        logger.debug(f"CACHE_GET [{cache_key[:20]}...] - {result}")
    elif operation == "set":
        logger.debug(f"CACHE_SET [{cache_key[:20]}...]")
    elif operation == "delete":
        logger.debug(f"CACHE_DEL [{cache_key[:20]}...]")


def log_storage_operation(operation: str, file_path: str, size: Optional[int] = None):
    """
    记录存储操作日志
    
    Args:
        operation: 操作类型（save, get, delete）
        file_path: 文件路径
        size: 文件大小（字节）
    """
    msg = f"STORAGE_{operation.upper()} {file_path}"
    if size:
        msg += f" - Size: {size} bytes"
    
    logger.info(msg)


def log_api_usage(api_key: str, endpoint: str, success: bool):
    """
    记录API使用日志
    
    Args:
        api_key: API密钥（将被部分隐藏）
        endpoint: API端点
        success: 是否成功
    """
    masked_key = f"{api_key[:8]}..." if len(api_key) > 8 else "****"
    status = "SUCCESS" if success else "FAILED"
    logger.info(f"API_USAGE [{masked_key}] {endpoint} - {status}")


def setup_request_logging():
    """设置请求日志中间件"""
    import uuid
    from fastapi import Request
    import time
    
    async def log_requests(request: Request, call_next):
        # 生成请求ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # 记录请求开始
        start_time = time.time()
        log_request(
            request_id,
            request.method,
            str(request.url),
            request.headers.get('user-agent')
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应
        processing_time = time.time() - start_time
        log_response(request_id, response.status_code, processing_time)
        
        return response
    
    return log_requests


class StructuredLogger:
    """结构化日志记录器"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def log_structured(self, level: str, message: str, **kwargs):
        """
        记录结构化日志
        
        Args:
            level: 日志级别
            message: 日志消息
            **kwargs: 结构化数据
        """
        structured_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'message': message,
            **kwargs
        }
        
        # 将结构化数据转换为字符串
        import json
        log_message = f"{message} | {json.dumps(structured_data, default=str)}"
        
        getattr(self.logger, level.lower())(log_message)
