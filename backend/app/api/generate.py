"""
3D模型生成API路由
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional

from app.models.request import GenerateRequest
from app.models.response import GenerateResponse, TaskStatusResponse
from app.services.model_service import ModelService
from app.services.cache_service import CacheService
from app.core.security import verify_api_key
from app.utils.logger import logger

router = APIRouter()

# 依赖注入
def get_model_service() -> ModelService:
    return ModelService()

def get_cache_service() -> CacheService:
    return CacheService()


@router.post("/generate", response_model=GenerateResponse)
async def generate_3d_model(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    model_service: ModelService = Depends(get_model_service),
    cache_service: CacheService = Depends(get_cache_service),
    api_key: str = Depends(verify_api_key)
):
    """
    生成3D模型
    
    Args:
        request: 生成请求参数
        background_tasks: 后台任务
        model_service: 模型服务
        cache_service: 缓存服务
        api_key: API密钥
    
    Returns:
        GenerateResponse: 生成结果
    """
    try:
        logger.info(f"收到3D模型生成请求: {request.prompt}")
        
        # 检查缓存
        cache_key = cache_service.generate_cache_key(request)
        cached_result = await cache_service.get_cached_result(cache_key)
        
        if cached_result:
            logger.info("从缓存返回结果")
            return GenerateResponse(**cached_result)
        
        # 调用模型服务生成3D模型
        result = await model_service.generate_model(request)
        
        # 缓存结果
        background_tasks.add_task(
            cache_service.cache_result,
            cache_key,
            result.dict()
        )
        
        logger.info(f"3D模型生成完成: {result.task_id}")
        return result
        
    except Exception as e:
        logger.error(f"3D模型生成失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/generate/status/{task_id}", response_model=TaskStatusResponse)
async def get_generation_status(
    task_id: str,
    model_service: ModelService = Depends(get_model_service),
    api_key: str = Depends(verify_api_key)
):
    """
    获取生成任务状态
    
    Args:
        task_id: 任务ID
        model_service: 模型服务
        api_key: API密钥
    
    Returns:
        TaskStatusResponse: 任务状态
    """
    try:
        status = await model_service.get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return TaskStatusResponse(**status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.get("/generate/download/{task_id}")
async def download_model(
    task_id: str,
    format: Optional[str] = "obj",
    model_service: ModelService = Depends(get_model_service),
    api_key: str = Depends(verify_api_key)
):
    """
    下载生成的3D模型文件
    
    Args:
        task_id: 任务ID
        format: 文件格式 (obj, glb, ply等)
        model_service: 模型服务
        api_key: API密钥
    
    Returns:
        FileResponse: 模型文件
    """
    try:
        file_path = await model_service.get_model_file(task_id, format)
        if not file_path:
            raise HTTPException(status_code=404, detail="模型文件不存在")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=f"{task_id}.{format}",
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"下载模型文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
