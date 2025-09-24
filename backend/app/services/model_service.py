"""
3D模型生成服务
"""
import asyncio
import uuid
from typing import Optional, Dict, Any
import aiohttp
import json
from datetime import datetime, timedelta

from app.models.request import GenerateRequest
from app.models.response import GenerateResponse, TaskStatus, TaskStatusResponse
from app.core.config import settings
from app.services.storage_service import StorageService
from app.utils.logger import logger
from app.services.sketchfab_service import SketchfabService
from app.models.request import SketchfabSearchRequest, SketchfabDownloadRequest


class ModelService:
    """3D模型生成服务"""
    
    def __init__(self):
        self.storage_service = StorageService()
        self.tasks = {}  # 内存中的任务状态存储，生产环境应使用Redis
        self.provider = settings.MODEL_PROVIDER
        self.sketchfab_service = SketchfabService()
    
    async def generate_model(self, request: GenerateRequest, provider_override: Optional[str] = None) -> GenerateResponse:
        """
        生成3D模型
        
        Args:
            request: 生成请求
            provider_override: 可选，覆盖默认提供商
        
        Returns:
            GenerateResponse: 生成响应
        """
        task_id = str(uuid.uuid4())
        
        # 创建任务记录
        task_data = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "request": request.dict(),
            "created_at": datetime.utcnow(),
            "progress": 0.0
        }
        self.tasks[task_id] = task_data
        
        # 根据提供商选择生成/检索方法
        provider = (provider_override or self.provider or "").lower()
        if provider == "meshy":
            result = await self._generate_with_meshy(task_id, request)
        elif provider == "local":
            result = await self._generate_with_local_model(task_id, request)
        elif provider == "sketchfab":
            result = await self._generate_with_sketchfab(task_id, request)
        else:
            raise ValueError(f"不支持的模型提供商: {provider}")
        
        return result
    
    async def _generate_with_meshy(
        self, 
        task_id: str, 
        request: GenerateRequest
    ) -> GenerateResponse:
        """使用Meshy API生成模型"""
        try:
            # 更新任务状态
            self.tasks[task_id]["status"] = TaskStatus.PROCESSING
            self.tasks[task_id]["progress"] = 10.0
            
            # 准备API请求
            headers = {
                "Authorization": f"Bearer {settings.MESHY_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "mode": "preview",  # Meshy v2 API 需要明确指定为 preview
                "prompt": request.prompt,
                "art_style": request.style.value,
            }
            
            if request.image_url:
                payload["image_url"] = request.image_url
            
            async with aiohttp.ClientSession() as session:
                # 提交生成任务
                print(headers)
                print(payload)
                async with session.post(
                    f"{settings.MESHY_API_URL}/openapi/v2/text-to-3d",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        print(response.status)
                        error_text = await response.text()
                        raise Exception(f"Meshy API错误: {error_text}")
                    
                    meshy_result = await response.json()
                    meshy_task_id = meshy_result.get("result")
                
                # 更新进度
                self.tasks[task_id]["progress"] = 30.0
                self.tasks[task_id]["meshy_task_id"] = meshy_task_id
                
                # 轮询任务状态
                model_url = await self._poll_meshy_task(session, headers, meshy_task_id)
                
                # 更新进度
                self.tasks[task_id]["progress"] = 80.0
                
                # 下载并存储模型文件
                file_path = await self._download_and_store_model(
                    session, model_url, task_id, request.output_format
                )
                
                # 生成预览图
                preview_url = await self._generate_preview(file_path)
                
                # 完成任务
                self.tasks[task_id]["status"] = TaskStatus.COMPLETED
                self.tasks[task_id]["progress"] = 100.0
                self.tasks[task_id]["completed_at"] = datetime.utcnow()
                self.tasks[task_id]["model_url"] = model_url
                self.tasks[task_id]["file_path"] = file_path
                
                # 计算处理时间
                processing_time = (
                    self.tasks[task_id]["completed_at"] - 
                    self.tasks[task_id]["created_at"]
                ).total_seconds()
                
                return GenerateResponse(
                    task_id=task_id,
                    status=TaskStatus.COMPLETED,
                    message="模型生成完成",
                    model_url=model_url,
                    preview_url=preview_url,
                    download_url=f"/api/generate/download/{task_id}",
                    file_format=request.output_format,
                    created_at=self.tasks[task_id]["created_at"],
                    completed_at=self.tasks[task_id]["completed_at"],
                    processing_time=processing_time
                )
        
        except Exception as e:
            # 标记任务失败
            self.tasks[task_id]["status"] = TaskStatus.FAILED
            self.tasks[task_id]["error"] = str(e)

            logger.error(f"Meshy模型生成失败 {task_id}: {str(e)}")
            return GenerateResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                message="生成失败",
                error_details=str(e),
                created_at=self.tasks[task_id]["created_at"],
            )
    
    async def _poll_meshy_task(self, session, headers, meshy_task_id) -> str:
        """轮询Meshy任务直至完成，返回模型URL"""
        start_time = datetime.utcnow()
        timeout = timedelta(seconds=settings.MAX_GENERATION_TIME)
        while datetime.utcnow() - start_time < timeout:
            await asyncio.sleep(1.5)
            async with session.get(
                f"{settings.MESHY_API_URL}/openapi/v2/text-to-3d/{meshy_task_id}",
                headers=headers
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"Meshy状态查询失败: {resp.status}")
                result = await resp.json()
                status = result.get("status")
                
                if status == "SUCCEEDED":
                    model_urls = result.get("model_urls", {})
                    # 优先返回obj格式，其次是glb
                    return model_urls.get("obj") or model_urls.get("glb")
                elif status == "FAILED":
                    raise Exception("Meshy任务失败")
        
        raise Exception("Meshy任务超时")
    
    async def _generate_with_local_model(
        self, 
        task_id: str, 
        request: GenerateRequest
    ) -> GenerateResponse:
        """使用本地模型生成（占位实现）"""
        try:
            # 标记处理中
            self.tasks[task_id]["status"] = TaskStatus.PROCESSING
            self.tasks[task_id]["progress"] = 10.0
            
            # 生成一个简单的 OBJ 立方体占位模型（几何体很小）
            obj_data = (
                "# minimal cube\n"
                "o cube\n"
                "v -0.5 -0.5 -0.5\n"
                "v  0.5 -0.5 -0.5\n"
                "v  0.5  0.5 -0.5\n"
                "v -0.5  0.5 -0.5\n"
                "v -0.5 -0.5  0.5\n"
                "v  0.5 -0.5  0.5\n"
                "v  0.5  0.5  0.5\n"
                "v -0.5  0.5  0.5\n"
                "f 1 2 3 4\n"
                "f 5 6 7 8\n"
                "f 1 5 8 4\n"
                "f 2 6 7 3\n"
                "f 4 3 7 8\n"
                "f 1 2 6 5\n"
            ).encode("utf-8")
            
            # 模拟一定的处理时间
            await asyncio.sleep(0.5)
            self.tasks[task_id]["progress"] = 60.0
            
            # 保存占位模型文件
            file_path = await self.storage_service.save_model_file(
                task_id=task_id,
                file_data=obj_data,
                file_format=request.output_format or "obj",
            )
            
            # 生成预览（可选，当前返回 None）
            preview_url = await self._generate_preview(file_path)
            
            # 标记完成
            self.tasks[task_id]["status"] = TaskStatus.COMPLETED
            self.tasks[task_id]["progress"] = 100.0
            self.tasks[task_id]["completed_at"] = datetime.utcnow()
            self.tasks[task_id]["file_path"] = file_path
            
            processing_time = (
                self.tasks[task_id]["completed_at"] - self.tasks[task_id]["created_at"]
            ).total_seconds()
            
            return GenerateResponse(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                message="本地占位模型生成完成",
                model_url=None,  # 本地存储路径通过下载接口提供
                preview_url=preview_url,
                download_url=f"/api/generate/download/{task_id}",
                file_format=request.output_format or "obj",
                created_at=self.tasks[task_id]["created_at"],
                completed_at=self.tasks[task_id]["completed_at"],
                processing_time=processing_time,
            )
        except Exception as e:
            self.tasks[task_id]["status"] = TaskStatus.FAILED
            self.tasks[task_id]["error"] = str(e)
            logger.error(f"本地模型生成失败 {task_id}: {str(e)}")
            return GenerateResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                message="生成失败",
                error_details=str(e),
                created_at=self.tasks[task_id]["created_at"],
            )
    
    async def _download_and_store_model(
        self,
        session: aiohttp.ClientSession,
        model_url: str,
        task_id: str,
        file_format: str
    ) -> str:
        """下载并存储模型文件"""
        async with session.get(model_url) as response:
            if response.status != 200:
                raise Exception(f"下载模型文件失败: {response.status}")
            
            model_data = await response.read()
            
            # 存储文件
            file_path = await self.storage_service.save_model_file(
                task_id, model_data, file_format
            )
            
            return file_path
    
    async def _generate_preview(self, file_path: str) -> Optional[str]:
        """生成模型预览图"""
        # 这里可以实现3D模型预览图生成逻辑
        # 使用Blender、Three.js或其他渲染引擎
        return None
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            Optional[Dict[str, Any]]: 任务状态信息
        """
        if task_id not in self.tasks:
            return None
        
        task_data = self.tasks[task_id]
        
        return {
            "task_id": task_id,
            "status": task_data["status"],
            "progress": task_data.get("progress", 0.0),
            "message": self._get_status_message(task_data["status"]),
            "created_at": task_data["created_at"],
            "updated_at": datetime.utcnow(),
            "estimated_completion": self._estimate_completion_time(task_data)
        }
    
    async def get_model_file(
        self, 
        task_id: str, 
        file_format: str = "obj"
    ) -> Optional[str]:
        """
        获取模型文件路径
        
        Args:
            task_id: 任务ID
            file_format: 文件格式
        
        Returns:
            Optional[str]: 文件路径
        """
        if task_id not in self.tasks:
            return None
        
        task_data = self.tasks[task_id]
        if task_data["status"] != TaskStatus.COMPLETED:
            return None
        
        return task_data.get("file_path")
    
    def _get_status_message(self, status: TaskStatus) -> str:
        """获取状态消息"""
        messages = {
            TaskStatus.PENDING: "任务已提交，等待处理",
            TaskStatus.PROCESSING: "正在生成3D模型",
            TaskStatus.COMPLETED: "模型生成完成",
            TaskStatus.FAILED: "模型生成失败",
            TaskStatus.CANCELLED: "任务已取消"
        }
        return messages.get(status, "未知状态")
    
    def _estimate_completion_time(self, task_data: Dict[str, Any]) -> Optional[datetime]:
        """估算完成时间"""
        if task_data["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return None
        
        # 基于历史数据估算，这里使用简单的固定时间
        estimated_duration = timedelta(minutes=5)  # 假设平均5分钟完成
        return task_data["created_at"] + estimated_duration
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        取消任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            bool: 是否成功取消
        """
        if task_id not in self.tasks:
            return False
        
        task_data = self.tasks[task_id]
        if task_data["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            return False
        
        self.tasks[task_id]["status"] = TaskStatus.CANCELLED
        logger.info(f"任务已取消: {task_id}")
        return True
    
    async def _generate_with_sketchfab(
        self,
        task_id: str,
        request: GenerateRequest
    ) -> GenerateResponse:
        """使用Sketchfab搜索并返回最匹配模型"""
        try:
            self.tasks[task_id]["status"] = TaskStatus.PROCESSING
            self.tasks[task_id]["progress"] = 10.0

            # 搜索可下载、相关性最高的模型
            search_req = SketchfabSearchRequest(
                query=request.prompt,
                downloadable=True,
                per_page=1,
                sort_by="relevance"
            )
            search_res = await self.sketchfab_service.search_models(search_req)
            if not search_res.models:
                raise Exception("未找到相关模型")
            top = search_res.models[0]

            self.tasks[task_id]["progress"] = 50.0

            model_url: Optional[str] = None
            file_format: Optional[str] = None
            preview_url: Optional[str] = top.preview_url or top.thumbnail_url

            # 尝试获取可下载的gltf链接
            if top.downloadable:
                dl_res = await self.sketchfab_service.download_model(
                    SketchfabDownloadRequest(model_uid=top.uid, format="gltf")
                )
                if dl_res.status == "success" and dl_res.download_url:
                    model_url = dl_res.download_url
                    file_format = dl_res.file_format or "gltf"
            
            # 若无法下载，退回到可嵌入/预览链接（前端GLTF加载可能失败，这里仍返回以便前端处理）
            if not model_url:
                model_url = top.embed_url or top.preview_url
                file_format = file_format or None

            self.tasks[task_id]["status"] = TaskStatus.COMPLETED
            self.tasks[task_id]["progress"] = 100.0
            self.tasks[task_id]["completed_at"] = datetime.utcnow()
            self.tasks[task_id]["model_url"] = model_url

            processing_time = (
                self.tasks[task_id]["completed_at"] - self.tasks[task_id]["created_at"]
            ).total_seconds()

            return GenerateResponse(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                message="已从Sketchfab返回最匹配模型",
                model_url=model_url,
                preview_url=preview_url,
                download_url=None,
                file_format=file_format,
                created_at=self.tasks[task_id]["created_at"],
                completed_at=self.tasks[task_id]["completed_at"],
                processing_time=processing_time,
                metadata={
                    "sketchfab_uid": top.uid,
                    "sketchfab_name": top.name,
                    "license": top.license,
                }
            )
        except Exception as e:
            self.tasks[task_id]["status"] = TaskStatus.FAILED
            self.tasks[task_id]["error"] = str(e)
            logger.error(f"Sketchfab检索失败 {task_id}: {str(e)}")
            return GenerateResponse(
                task_id=task_id,
                status=TaskStatus.FAILED,
                message="生成失败",
                error_details=str(e),
                created_at=self.tasks[task_id]["created_at"],
            )
