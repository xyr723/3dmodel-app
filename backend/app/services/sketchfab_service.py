"""
Sketchfab API服务
提供3D模型搜索、获取和下载功能
"""
import os
import asyncio
import aiohttp
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from urllib.parse import urlencode

from app.models.request import SketchfabSearchRequest, SketchfabDownloadRequest
from app.models.response import (
    SketchfabModel, 
    SketchfabSearchResponse, 
    SketchfabDownloadResponse
)
from app.core.config import settings
from app.utils.logger import logger
from app.services.cache_service import CacheService
from app.services.storage_service import StorageService


class SketchfabService:
    """Sketchfab API服务类"""
    
    def __init__(self):
        self.base_url = "https://api.sketchfab.com/v3"
        # 尝试多种方式获取API token
        self.api_token = (
            os.environ.get('SKETCHFAB_API_TOKEN') or
            getattr(settings, 'SKETCHFAB_API_TOKEN', None) or
            "28c369ecc5a4434fb0f4d75d29dbb8f8"  # 直接使用您的token作为备选
        )
        self.cache_service = CacheService()
        self.storage_service = StorageService()
        
        # 请求限制配置
        self.rate_limit = 60  # 每分钟请求数
        self.request_interval = 60 / self.rate_limit  # 请求间隔
        self.last_request_time = 0
        
        # 缓存配置
        self.cache_ttl = 3600  # 1小时缓存
        
    async def _make_request(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """发起API请求"""
        
        # 速率限制
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_interval:
            await asyncio.sleep(self.request_interval - time_since_last)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "3DModelApp/1.0"
        }
        
        # 添加认证头（如果有token）
        if self.api_token:
            headers["Authorization"] = f"Token {self.api_token}"
        
        # 调试信息
        logger.info(f"请求URL: {url}")
        logger.info(f"请求参数: {params}")
        
        try:
            async with aiohttp.ClientSession() as session:
                if method.upper() == "GET":
                    async with session.get(url, params=params, headers=headers) as response:
                        self.last_request_time = time.time()
                        
                        logger.info(f"响应状态: {response.status}")
                        
                        if response.status == 200:
                            data = await response.json()
                            logger.info(f"响应数据: {len(data.get('results', []))} 个结果")
                            return data
                        elif response.status == 429:
                            # 速率限制，等待后重试
                            retry_after = int(response.headers.get('Retry-After', 60))
                            logger.warning(f"API速率限制，等待{retry_after}秒后重试")
                            await asyncio.sleep(retry_after)
                            return await self._make_request(endpoint, params, method)
                        else:
                            error_text = await response.text()
                            logger.error(f"API请求失败: {response.status} - {error_text}")
                            raise Exception(f"API请求失败: {response.status} - {error_text}")
                            
        except Exception as e:
            logger.error(f"Sketchfab API请求异常: {str(e)}")
            raise
    
    def _parse_model_data(self, model_data: Dict[str, Any]) -> SketchfabModel:
        """解析模型数据"""
        
        # 解析作者信息
        author_info = model_data.get('user', {})
        author = author_info.get('displayName', author_info.get('username', 'Unknown'))
        author_url = author_info.get('profileUrl')
        
        # 解析模型属性
        face_count = None
        vertex_count = None
        if 'geometries' in model_data:
            geometries = model_data['geometries']
            if geometries:
                face_count = geometries.get('faceCount')
                vertex_count = geometries.get('vertexCount')
        
        # 解析许可证信息
        license_info = model_data.get('license', {})
        license_type = license_info.get('slug')
        license_label = license_info.get('label')
        
        # 解析媒体信息
        thumbnails = model_data.get('thumbnails', {})
        thumbnail_url = ""
        if 'images' in thumbnails:
            images = thumbnails.get('images', [])
            if images:
                # 选择合适大小的缩略图
                for img in images:
                    if img.get('width', 0) >= 200:
                        thumbnail_url = img.get('url', '')
                        break
                if not thumbnail_url and images:
                    thumbnail_url = images[0].get('url', '')
        
        # 解析分类和标签
        categories = []
        if 'categories' in model_data:
            categories = [cat.get('name', '') for cat in model_data['categories']]
        
        tags = []
        if 'tags' in model_data:
            tags = [tag.get('name', '') for tag in model_data['tags']]
        
        # 解析时间
        published_at = None
        created_at = None
        if 'publishedAt' in model_data:
            try:
                published_at = datetime.fromisoformat(
                    model_data['publishedAt'].replace('Z', '+00:00')
                )
            except:
                pass
        
        if 'createdAt' in model_data:
            try:
                created_at = datetime.fromisoformat(
                    model_data['createdAt'].replace('Z', '+00:00')
                )
            except:
                pass
        
        return SketchfabModel(
            uid=model_data.get('uid', ''),
            name=model_data.get('name', ''),
            description=model_data.get('description', ''),
            author=author,
            author_url=author_url,
            face_count=face_count,
            vertex_count=vertex_count,
            animated=model_data.get('isAnimated', False),
            rigged=model_data.get('isRigged', False),
            license=license_type,
            license_label=license_label,
            view_count=model_data.get('viewCount', 0),
            like_count=model_data.get('likeCount', 0),
            comment_count=model_data.get('commentCount', 0),
            thumbnail_url=thumbnail_url,
            preview_url=model_data.get('viewerUrl'),
            embed_url=model_data.get('embedUrl'),
            downloadable=model_data.get('isDownloadable', False),
            categories=categories,
            tags=tags,
            published_at=published_at,
            created_at=created_at
        )
    
    async def search_models(self, request: SketchfabSearchRequest) -> SketchfabSearchResponse:
        """搜索3D模型"""
        
        # 生成缓存键
        cache_key = f"sketchfab_search_{hash(str(request.dict()))}"
        
        # 检查缓存
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            logger.info(f"从缓存返回Sketchfab搜索结果: {request.query}")
            return SketchfabSearchResponse(**cached_result)
        
        # 构建搜索参数 - 严格按照Sketchfab API格式
        params = {
            'q': request.query,
            'type': 'models',
            'count': request.per_page,
            'sort_by': request.sort_by or 'relevance'
        }
        
        # 分页处理
        if request.page > 1:
            params['offset'] = (request.page - 1) * request.per_page
        
        # 添加筛选条件
        if request.category:
            params['categories'] = request.category
            
        if request.license:
            # Sketchfab API许可证参数格式映射
            # 根据API文档，正确的许可证值应该是简化格式
            license_mapping = {
                'cc0': None,  # CC0通常不需要特殊参数，使用免费/开放筛选
                'cc-by': 'by',
                'cc-by-sa': 'by-sa', 
                'cc-by-nc': 'by-nc',
                'cc-by-nc-sa': 'by-nc-sa',
                'cc': None  # 通用CC许可证，不指定具体类型
            }
            
            mapped_license = license_mapping.get(request.license.lower(), request.license)
            if mapped_license:  # 只有在有映射值时才添加许可证参数
                params['license'] = mapped_license
            
            # 对于CC0，我们使用免费下载筛选而不是许可证参数
            if request.license.lower() in ['cc0', 'cc']:
                params['downloadable'] = "true"  # 确保可下载
                # 移除可能冲突的许可证参数
                if 'license' in params:
                    del params['license']
            
        if request.animated is not None:
            params['animated'] = "true" if request.animated else "false"
            
        if request.rigged is not None:
            params['rigged'] = "true" if request.rigged else "false"
            
        # 下载筛选 - 必须传字符串
        if request.downloadable:
            params['downloadable'] = "true"
            
        if request.min_face_count is not None:
            params['min_face_count'] = request.min_face_count
            
        if request.max_face_count is not None:
            params['max_face_count'] = request.max_face_count
            
        if request.staff_picked:
            params['staffpicked'] = "true"
        
        try:
            start_time = time.time()
            
            # 调试日志 - 显示实际发送的参数
            logger.info(f"发送到Sketchfab API的参数: {params}")
            
            # 发起搜索请求
            response_data = await self._make_request('search', params)
            
            search_time = time.time() - start_time
            
            # 解析结果
            results = response_data.get('results', [])
            models = [self._parse_model_data(model) for model in results]
            
            # 计算分页信息
            total_count = response_data.get('count', 0)
            total_pages = (total_count + request.per_page - 1) // request.per_page
            
            search_response = SketchfabSearchResponse(
                query=request.query,
                total_count=total_count,
                page=request.page,
                per_page=request.per_page,
                total_pages=total_pages,
                models=models,
                search_time=search_time,
                filters_applied=params
            )
            
            # 缓存结果
            await self.cache_service.set(
                cache_key, 
                search_response.dict(), 
                ttl=self.cache_ttl
            )
            
            logger.info(
                f"Sketchfab搜索完成: {request.query}, "
                f"找到{total_count}个结果, 耗时{search_time:.2f}秒"
            )
            
            return search_response
            
        except Exception as e:
            logger.error(f"Sketchfab搜索失败: {str(e)}")
            raise
    
    async def get_model_details(self, model_uid: str) -> SketchfabModel:
        """获取模型详细信息"""
        
        # 检查缓存
        cache_key = f"sketchfab_model_{model_uid}"
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            return SketchfabModel(**cached_result)
        
        try:
            # 获取模型详情
            response_data = await self._make_request(f'models/{model_uid}')
            model = self._parse_model_data(response_data)
            
            # 缓存结果
            await self.cache_service.set(
                cache_key, 
                model.dict(), 
                ttl=self.cache_ttl
            )
            
            return model
            
        except Exception as e:
            logger.error(f"获取Sketchfab模型详情失败: {str(e)}")
            raise
    
    async def download_model(self, request: SketchfabDownloadRequest) -> SketchfabDownloadResponse:
        """下载3D模型"""
        
        try:
            # 首先获取模型信息
            model = await self.get_model_details(request.model_uid)
            
            if not model.downloadable:
                raise Exception("该模型不支持下载")
            
            # 生成下载ID
            download_id = f"dl_{int(time.time())}_{request.model_uid}"
            
            # 获取下载链接 - 需要认证
            download_url = None
            file_size = None
            
            if not self.api_token:
                logger.warning("下载功能需要Sketchfab API Token")
                return SketchfabDownloadResponse(
                    model_uid=request.model_uid,
                    download_id=download_id,
                    status="failed",
                    message="下载功能需要有效的Sketchfab API Token"
                )
            
            try:
                # 调用下载API
                download_data = await self._make_request(
                    f'models/{request.model_uid}/download'
                )
                
                # 尝试获取不同格式的下载链接
                if request.format == 'original' or request.format == 'source':
                    source_data = download_data.get('source', {})
                    download_url = source_data.get('url')
                    file_size = source_data.get('size')
                elif request.format == 'gltf':
                    gltf_data = download_data.get('gltf', {})
                    download_url = gltf_data.get('url')
                    file_size = gltf_data.get('size')
                elif request.format == 'usdz':
                    usdz_data = download_data.get('usdz', {})
                    download_url = usdz_data.get('url')
                    file_size = usdz_data.get('size')
                else:
                    # 默认尝试获取任何可用格式
                    for format_key in ['source', 'gltf', 'usdz']:
                        if format_key in download_data and download_data[format_key].get('url'):
                            format_data = download_data[format_key]
                            download_url = format_data['url']
                            file_size = format_data.get('size')
                            break
                            
            except Exception as e:
                logger.error(f"获取下载链接失败: {str(e)}")
                return SketchfabDownloadResponse(
                    model_uid=request.model_uid,
                    download_id=download_id,
                    status="failed",
                    message=f"获取下载链接失败: {str(e)}"
                )
            
            if not download_url:
                raise Exception("无法获取下载链接")
            
            # 计算链接过期时间（通常24小时）
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # 检查许可证信息
            attribution_required = True
            commercial_use = False
            
            if model.license:
                if 'cc0' in model.license.lower():
                    attribution_required = False
                    commercial_use = True
                elif 'cc-by' in model.license.lower():
                    commercial_use = True
            
            response = SketchfabDownloadResponse(
                model_uid=request.model_uid,
                download_id=download_id,
                status="success",
                message="下载链接生成成功",
                download_url=download_url,
                file_format=request.format,
                file_size=file_size,
                model_name=model.name,
                author=model.author,
                license=model.license,
                expires_at=expires_at,
                attribution_required=attribution_required,
                commercial_use=commercial_use
            )
            
            logger.info(f"Sketchfab模型下载请求成功: {request.model_uid}")
            return response
            
        except Exception as e:
            logger.error(f"Sketchfab模型下载失败: {str(e)}")
            
            return SketchfabDownloadResponse(
                model_uid=request.model_uid,
                download_id=f"failed_{int(time.time())}",
                status="failed",
                message=f"下载失败: {str(e)}"
            )
    
    async def get_popular_models(
        self, 
        category: Optional[str] = None,
        limit: int = 20
    ) -> List[SketchfabModel]:
        """获取热门模型"""
        
        search_request = SketchfabSearchRequest(
            query="*",  # 搜索所有模型
            category=category,
            sort_by="likes",
            per_page=limit,
            downloadable=True,
            staff_picked=True
        )
        
        result = await self.search_models(search_request)
        return result.models
    
    async def get_categories(self) -> List[Dict[str, str]]:
        """获取模型分类列表"""
        
        cache_key = "sketchfab_categories"
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            response_data = await self._make_request('categories')
            categories = []
            
            for cat in response_data.get('results', []):
                categories.append({
                    'slug': cat.get('slug', ''),
                    'name': cat.get('name', ''),
                    'count': cat.get('count', 0)
                })
            
            # 缓存24小时
            await self.cache_service.set(cache_key, categories, ttl=86400)
            return categories
            
        except Exception as e:
            logger.error(f"获取Sketchfab分类失败: {str(e)}")
            return []
