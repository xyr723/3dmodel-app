"""
安全和认证相关功能
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings
from app.utils.logger import logger

# HTTP Bearer认证
security = HTTPBearer()


class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def create_access_token(self, data: Dict[Any, Any]) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[Any, Any]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="令牌已过期")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="无效的令牌")
    
    def generate_api_key(self, prefix: str = "sk") -> str:
        """生成API密钥"""
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"
    
    def hash_api_key(self, api_key: str) -> str:
        """哈希API密钥"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def verify_api_key_hash(self, api_key: str, hashed_key: str) -> bool:
        """验证API密钥哈希"""
        return hmac.compare_digest(
            hashlib.sha256(api_key.encode()).hexdigest(),
            hashed_key
        )


# 全局安全管理器实例
security_manager = SecurityManager()


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    验证API密钥
    
    Args:
        credentials: HTTP认证凭据
    
    Returns:
        str: 验证通过的API密钥
    
    Raises:
        HTTPException: 认证失败时抛出
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="缺少认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = credentials.credentials
    
    # 如果配置中设置了固定的API密钥，则直接比较
    if settings.API_KEY:
        if not hmac.compare_digest(api_key, settings.API_KEY):
            logger.warning(f"API密钥验证失败: {api_key[:10]}...")
            raise HTTPException(
                status_code=401,
                detail="无效的API密钥",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        # 这里可以实现更复杂的API密钥验证逻辑
        # 比如从数据库中查询API密钥
        if not api_key or len(api_key) < 10:
            raise HTTPException(
                status_code=401,
                detail="无效的API密钥格式",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    logger.info(f"API密钥验证成功: {api_key[:10]}...")
    return api_key


async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[Any, Any]:
    """
    验证JWT令牌
    
    Args:
        credentials: HTTP认证凭据
    
    Returns:
        Dict[Any, Any]: 令牌载荷
    
    Raises:
        HTTPException: 认证失败时抛出
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="缺少认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = security_manager.verify_token(token)
    
    return payload


def create_user_token(user_id: str, additional_data: Optional[Dict] = None) -> str:
    """
    为用户创建访问令牌
    
    Args:
        user_id: 用户ID
        additional_data: 额外数据
    
    Returns:
        str: 访问令牌
    """
    data = {"sub": user_id, "type": "access"}
    if additional_data:
        data.update(additional_data)
    
    return security_manager.create_access_token(data)


def validate_request_signature(
    payload: str,
    signature: str,
    secret: str
) -> bool:
    """
    验证请求签名
    
    Args:
        payload: 请求载荷
        signature: 签名
        secret: 密钥
    
    Returns:
        bool: 验证结果
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


class RateLimiter:
    """简单的内存速率限制器"""
    
    def __init__(self):
        self.requests = {}  # {key: [timestamp, ...]}
    
    def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int = 60
    ) -> bool:
        """
        检查是否允许请求
        
        Args:
            key: 限制键（通常是IP或API密钥）
            limit: 限制次数
            window_seconds: 时间窗口（秒）
        
        Returns:
            bool: 是否允许
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        
        # 清理过期记录
        if key in self.requests:
            self.requests[key] = [
                timestamp for timestamp in self.requests[key]
                if timestamp > cutoff
            ]
        else:
            self.requests[key] = []
        
        # 检查是否超过限制
        if len(self.requests[key]) >= limit:
            return False
        
        # 记录本次请求
        self.requests[key].append(now)
        return True


# 全局速率限制器
rate_limiter = RateLimiter()
