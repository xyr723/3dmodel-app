"""
Sketchfab API路由
提供3D模型搜索、浏览和下载功能
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List

from app.models.request import SketchfabSearchRequest, SketchfabDownloadRequest
from app.models.response import (
    SketchfabSearchResponse, 
    SketchfabDownloadResponse,
    SketchfabModel
)
from app.services.sketchfab_service import SketchfabService
from app.core.security import verify_api_key
from app.utils.logger import logger

router = APIRouter()

# 依赖注入
def get_sketchfab_service() -> SketchfabService:
    return SketchfabService()


@router.post("/sketchfab/search", response_model=SketchfabSearchResponse)
async def search_sketchfab_models(
    request: SketchfabSearchRequest,
    sketchfab_service: SketchfabService = Depends(get_sketchfab_service),
    api_key: str = Depends(verify_api_key)
):
    """
    搜索Sketchfab 3D模型
    
    Args:
        request: 搜索请求参数
        sketchfab_service: Sketchfab服务
        api_key: API密钥
    
    Returns:
        SketchfabSearchResponse: 搜索结果
    """
    try:
        logger.info(f"收到Sketchfab搜索请求: {request.query}")
        
        result = await sketchfab_service.search_models(request)
        
        logger.info(
            f"Sketchfab搜索完成: {request.query}, "
            f"找到{result.total_count}个结果"
        )
        return result
        
    except Exception as e:
        logger.error(f"Sketchfab搜索失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/sketchfab/search", response_model=SketchfabSearchResponse)
async def search_sketchfab_models_get(
    query: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="模型分类"),
    license: Optional[str] = Query("cc0", description="许可证类型"),
    animated: Optional[bool] = Query(None, description="是否包含动画"),
    rigged: Optional[bool] = Query(None, description="是否有骨骼绑定"),
    downloadable: Optional[str] = Query("true", description="是否可下载"),
    page: int = Query(1, ge=1, description="页码"),
    per_page: int = Query(20, ge=1, le=100, description="每页数量"),
    sort_by: Optional[str] = Query("relevance", description="排序方式"),
    min_face_count: Optional[int] = Query(None, ge=0, description="最小面数"),
    max_face_count: Optional[int] = Query(None, ge=0, description="最大面数"),
    staff_picked: Optional[bool] = Query(None, description="是否为官方推荐"),
    sketchfab_service: SketchfabService = Depends(get_sketchfab_service),
    api_key: str = Depends(verify_api_key)
):
    """
    搜索Sketchfab 3D模型 (GET方式)
    
    提供GET接口方便直接在浏览器中测试
    """
    try:
        # 构建搜索请求
        request = SketchfabSearchRequest(
            query=query,
            category=category,
            license=license,
            animated=animated,
            rigged=rigged,
            downloadable=(downloadable.lower() == "true" if downloadable else True),
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            min_face_count=min_face_count,
            max_face_count=max_face_count,
            staff_picked=staff_picked
        )
        
        logger.info(f"收到Sketchfab搜索请求(GET): {query}")
        
        result = await sketchfab_service.search_models(request)
        
        logger.info(
            f"Sketchfab搜索完成(GET): {query}, "
            f"找到{result.total_count}个结果"
        )
        return result
        
    except Exception as e:
        logger.error(f"Sketchfab搜索失败(GET): {str(e)}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/sketchfab/model/{model_uid}", response_model=SketchfabModel)
async def get_sketchfab_model(
    model_uid: str,
    sketchfab_service: SketchfabService = Depends(get_sketchfab_service),
    api_key: str = Depends(verify_api_key)
):
    """
    获取Sketchfab模型详细信息
    
    Args:
        model_uid: 模型唯一标识符
        sketchfab_service: Sketchfab服务
        api_key: API密钥
    
    Returns:
        SketchfabModel: 模型详细信息
    """
    try:
        logger.info(f"获取Sketchfab模型详情: {model_uid}")
        
        model = await sketchfab_service.get_model_details(model_uid)
        
        if not model:
            raise HTTPException(status_code=404, detail="模型不存在")
        
        logger.info(f"获取Sketchfab模型详情成功: {model.name}")
        return model
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取Sketchfab模型详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取模型详情失败: {str(e)}")


@router.post("/sketchfab/download", response_model=SketchfabDownloadResponse)
async def download_sketchfab_model(
    request: SketchfabDownloadRequest,
    sketchfab_service: SketchfabService = Depends(get_sketchfab_service),
    api_key: str = Depends(verify_api_key)
):
    """
    下载Sketchfab 3D模型
    
    Args:
        request: 下载请求参数
        sketchfab_service: Sketchfab服务
        api_key: API密钥
    
    Returns:
        SketchfabDownloadResponse: 下载结果
    """
    try:
        logger.info(f"收到Sketchfab下载请求: {request.model_uid}")
        
        result = await sketchfab_service.download_model(request)
        
        if result.status == "failed":
            raise HTTPException(status_code=400, detail=result.message)
        
        logger.info(f"Sketchfab下载请求完成: {request.model_uid}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sketchfab下载失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/sketchfab/download/{model_uid}", response_model=SketchfabDownloadResponse)
async def download_sketchfab_model_get(
    model_uid: str,
    format: Optional[str] = Query("original", description="下载格式"),
    user_id: Optional[str] = Query(None, description="用户ID"),
    sketchfab_service: SketchfabService = Depends(get_sketchfab_service),
    api_key: str = Depends(verify_api_key)
):
    """
    下载Sketchfab 3D模型 (GET方式)
    
    Args:
        model_uid: 模型唯一标识符
        format: 下载格式
        user_id: 用户ID
        sketchfab_service: Sketchfab服务
        api_key: API密钥
    
    Returns:
        SketchfabDownloadResponse: 下载结果
    """
    try:
        # 构建下载请求
        request = SketchfabDownloadRequest(
            model_uid=model_uid,
            format=format,
            user_id=user_id
        )
        
        logger.info(f"收到Sketchfab下载请求(GET): {model_uid}")
        
        result = await sketchfab_service.download_model(request)
        
        if result.status == "failed":
            raise HTTPException(status_code=400, detail=result.message)
        
        logger.info(f"Sketchfab下载请求完成(GET): {model_uid}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sketchfab下载失败(GET): {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/sketchfab/popular", response_model=List[SketchfabModel])
async def get_popular_models(
    category: Optional[str] = Query(None, description="模型分类"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    sketchfab_service: SketchfabService = Depends(get_sketchfab_service),
    api_key: str = Depends(verify_api_key)
):
    """
    获取热门3D模型
    
    Args:
        category: 模型分类
        limit: 返回数量
        sketchfab_service: Sketchfab服务
        api_key: API密钥
    
    Returns:
        List[SketchfabModel]: 热门模型列表
    """
    try:
        logger.info(f"获取热门Sketchfab模型: category={category}, limit={limit}")
        
        models = await sketchfab_service.get_popular_models(category, limit)
        
        logger.info(f"获取热门模型完成: 返回{len(models)}个模型")
        return models
        
    except Exception as e:
        logger.error(f"获取热门模型失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门模型失败: {str(e)}")


@router.get("/sketchfab/categories")
async def get_sketchfab_categories(
    sketchfab_service: SketchfabService = Depends(get_sketchfab_service),
    api_key: str = Depends(verify_api_key)
):
    """
    获取Sketchfab模型分类列表
    
    Args:
        sketchfab_service: Sketchfab服务
        api_key: API密钥
    
    Returns:
        List: 分类列表
    """
    try:
        logger.info("获取Sketchfab分类列表")
        
        categories = await sketchfab_service.get_categories()
        
        logger.info(f"获取分类列表完成: 共{len(categories)}个分类")
        return {
            "categories": categories,
            "count": len(categories)
        }
        
    except Exception as e:
        logger.error(f"获取分类列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取分类列表失败: {str(e)}")
