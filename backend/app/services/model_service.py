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


class ModelService:
    """3D模型生成服务"""
    
    def __init__(self):
        self.storage_service = StorageService()
        self.tasks = {}  # 内存中的任务状态存储，生产环境应使用Redis
        self.provider = settings.MODEL_PROVIDER
    
    async def generate_model(self, request: GenerateRequest) -> GenerateResponse:
        """
        生成3D模型
        
        Args:
            request: 生成请求
        
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
        
        # 根据提供商选择生成方法
        if self.provider == "meshy":
            result = await self._generate_with_meshy(task_id, request)
        elif self.provider == "local":
            result = await self._generate_with_local_model(task_id, request)
        else:
            raise ValueError(f"不支持的模型提供商: {self.provider}")
        
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
                message="模型生成失败",
                error_details=str(e),
                created_at=self.tasks[task_id]["created_at"]
            )
    
    async def _poll_meshy_task(
        self, 
        session: aiohttp.ClientSession,
        headers: Dict[str, str],
        meshy_task_id: str
    ) -> str:
        """轮询Meshy任务状态"""
        max_attempts = 60  # 最多轮询60次（5分钟）
        
        for attempt in range(max_attempts):
            await asyncio.sleep(5)  # 等待5秒
            
            async with session.get(
                f"{settings.MESHY_API_URL}/openapi/v2/text-to-3d/{meshy_task_id}",
                headers=headers
            ) as response:
                if response.status != 200:
                    continue
                
                result = await response.json()
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
        """使用本地模型生成"""
        # 这里实现本地模型调用逻辑
        # 可以集成Stable Diffusion 3D、Point-E等开源模型
        raise NotImplementedError("本地模型生成尚未实现")
    
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
