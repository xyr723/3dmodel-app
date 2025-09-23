"""
缓存服务
"""
import json
import hashlib
from typing import Optional, Dict, Any
import redis.asyncio as redis
from datetime import timedelta

from app.models.request import GenerateRequest
from app.core.config import settings
from app.utils.logger import logger


class CacheService:
    """缓存服务类"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}  # 内存缓存作为备选方案
        self.ttl = settings.CACHE_TTL
    
    async def _get_redis_client(self):
        """获取Redis客户端"""
        if self.redis_client is None:
            try:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                # 测试连接
                await self.redis_client.ping()
                logger.info("Redis连接成功")
            except Exception as e:
                logger.warning(f"Redis连接失败，使用内存缓存: {str(e)}")
                self.redis_client = None
        
        return self.redis_client
    
    def generate_cache_key(self, request: GenerateRequest) -> str:
        """
        生成缓存键
        
        Args:
            request: 生成请求
        
        Returns:
            str: 缓存键
        """
        # 创建包含主要参数的字典
        cache_data = {
            "prompt": request.prompt,
            "style": request.style.value,
            "mode": request.mode.value,
            "quality": request.quality,
            "resolution": request.resolution,
            "output_format": request.output_format,
            "include_texture": request.include_texture,
            "negative_prompt": request.negative_prompt,
            "seed": request.seed,  # 如果有seed，确保相同参数得到相同结果
        }
        
        # 如果有图片URL，也要包含在内
        if request.image_url:
            cache_data["image_url"] = request.image_url
        
        # 生成哈希值作为缓存键
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.md5(cache_string.encode()).hexdigest()
        
        return f"3d_model:{cache_hash}"
    
    async def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存结果
        
        Args:
            cache_key: 缓存键
        
        Returns:
            Optional[Dict[str, Any]]: 缓存的结果
        """
        try:
            redis_client = await self._get_redis_client()
            
            if redis_client:
                # 从Redis获取
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    logger.info(f"从Redis缓存获取结果: {cache_key}")
                    return json.loads(cached_data)
            else:
                # 从内存缓存获取
                if cache_key in self.memory_cache:
                    cache_entry = self.memory_cache[cache_key]
                    # 检查是否过期
                    if cache_entry["expires_at"] > self._current_timestamp():
                        logger.info(f"从内存缓存获取结果: {cache_key}")
                        return cache_entry["data"]
                    else:
                        # 删除过期条目
                        del self.memory_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.error(f"获取缓存失败: {str(e)}")
            return None
    
    async def cache_result(
        self, 
        cache_key: str, 
        result: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        缓存结果
        
        Args:
            cache_key: 缓存键
            result: 要缓存的结果
            ttl: 过期时间（秒）
        
        Returns:
            bool: 是否成功缓存
        """
        try:
            cache_ttl = ttl or self.ttl
            redis_client = await self._get_redis_client()
            
            if redis_client:
                # 存储到Redis
                await redis_client.setex(
                    cache_key,
                    cache_ttl,
                    json.dumps(result, default=str)
                )
                logger.info(f"结果已缓存到Redis: {cache_key}")
            else:
                # 存储到内存缓存
                self.memory_cache[cache_key] = {
                    "data": result,
                    "expires_at": self._current_timestamp() + cache_ttl
                }
                
                # 清理过期的内存缓存条目
                await self._cleanup_memory_cache()
                
                logger.info(f"结果已缓存到内存: {cache_key}")
            
            return True
            
        except Exception as e:
            logger.error(f"缓存结果失败: {str(e)}")
            return False
    
    async def delete_cache(self, cache_key: str) -> bool:
        """
        删除缓存
        
        Args:
            cache_key: 缓存键
        
        Returns:
            bool: 是否成功删除
        """
        try:
            redis_client = await self._get_redis_client()
            
            if redis_client:
                # 从Redis删除
                result = await redis_client.delete(cache_key)
                logger.info(f"从Redis删除缓存: {cache_key}")
                return result > 0
            else:
                # 从内存缓存删除
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                    logger.info(f"从内存删除缓存: {cache_key}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"删除缓存失败: {str(e)}")
            return False
    
    async def clear_all_cache(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            bool: 是否成功清空
        """
        try:
            redis_client = await self._get_redis_client()
            
            if redis_client:
                # 删除所有3D模型相关的缓存
                keys = await redis_client.keys("3d_model:*")
                if keys:
                    await redis_client.delete(*keys)
                logger.info("Redis缓存已清空")
            
            # 清空内存缓存
            self.memory_cache.clear()
            logger.info("内存缓存已清空")
            
            return True
            
        except Exception as e:
            logger.error(f"清空缓存失败: {str(e)}")
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict[str, Any]: 缓存统计
        """
        stats = {
            "memory_cache_size": len(self.memory_cache),
            "redis_connected": False,
            "redis_cache_size": 0
        }
        
        try:
            redis_client = await self._get_redis_client()
            
            if redis_client:
                stats["redis_connected"] = True
                # 获取Redis中3D模型相关的缓存数量
                keys = await redis_client.keys("3d_model:*")
                stats["redis_cache_size"] = len(keys)
                
                # 获取Redis内存使用情况
                info = await redis_client.info("memory")
                stats["redis_memory_usage"] = info.get("used_memory_human", "unknown")
        
        except Exception as e:
            logger.error(f"获取缓存统计失败: {str(e)}")
        
        return stats
    
    async def _cleanup_memory_cache(self):
        """清理过期的内存缓存条目"""
        current_time = self._current_timestamp()
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry["expires_at"] <= current_time
        ]
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # 如果内存缓存过大，删除最旧的条目
        max_size = settings.CACHE_MAX_SIZE
        if len(self.memory_cache) > max_size:
            # 按过期时间排序，删除最旧的条目
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1]["expires_at"]
            )
            
            items_to_remove = len(self.memory_cache) - max_size
            for i in range(items_to_remove):
                key = sorted_items[i][0]
                del self.memory_cache[key]
    
    def _current_timestamp(self) -> int:
        """获取当前时间戳"""
        import time
        return int(time.time())
    
    async def preload_popular_models(self):
        """预加载热门模型（可选功能）"""
        # 这里可以实现预加载逻辑
        # 比如根据历史数据预生成一些热门的模型
        pass
    
    async def close(self):
        """关闭缓存服务"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis连接已关闭")
