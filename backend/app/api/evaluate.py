"""
用户反馈评估API路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from app.models.request import EvaluateRequest, FeedbackRequest
from app.models.response import EvaluateResponse, FeedbackResponse
from app.db.feedback import FeedbackDB
from app.core.security import verify_api_key
from app.utils.logger import logger

router = APIRouter()

# 依赖注入
def get_feedback_db() -> FeedbackDB:
    return FeedbackDB()


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_model(
    request: EvaluateRequest,
    feedback_db: FeedbackDB = Depends(get_feedback_db),
    api_key: str = Depends(verify_api_key)
):
    """
    评估3D模型质量
    
    Args:
        request: 评估请求参数
        feedback_db: 反馈数据库
        api_key: API密钥
    
    Returns:
        EvaluateResponse: 评估结果
    """
    try:
        logger.info(f"收到模型评估请求: {request.task_id}")
        
        # 这里可以实现自动评估逻辑
        # 比如检查模型的几何质量、纹理质量等
        
        # 简单的评估逻辑示例
        evaluation_score = await _calculate_model_quality(request)
        
        # 保存评估结果
        evaluation_data = {
            "task_id": request.task_id,
            "score": evaluation_score,
            "metrics": request.metrics,
            "timestamp": None  # 将在数据库中自动设置
        }
        
        result = await feedback_db.save_evaluation(evaluation_data)
        
        logger.info(f"模型评估完成: {request.task_id}, 得分: {evaluation_score}")
        
        return EvaluateResponse(
            task_id=request.task_id,
            score=evaluation_score,
            evaluation_id=result["evaluation_id"],
            message="评估完成"
        )
        
    except Exception as e:
        logger.error(f"模型评估失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"评估失败: {str(e)}")


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    feedback_db: FeedbackDB = Depends(get_feedback_db),
    api_key: str = Depends(verify_api_key)
):
    """
    提交用户反馈
    
    Args:
        request: 反馈请求参数
        feedback_db: 反馈数据库
        api_key: API密钥
    
    Returns:
        FeedbackResponse: 反馈提交结果
    """
    try:
        logger.info(f"收到用户反馈: {request.task_id}")
        
        # 保存用户反馈
        feedback_data = {
            "task_id": request.task_id,
            "user_id": request.user_id,
            "rating": request.rating,
            "comment": request.comment,
            "feedback_type": request.feedback_type,
            "timestamp": None  # 将在数据库中自动设置
        }
        
        result = await feedback_db.save_feedback(feedback_data)
        
        logger.info(f"用户反馈已保存: {result['feedback_id']}")
        
        return FeedbackResponse(
            feedback_id=result["feedback_id"],
            message="反馈提交成功",
            status="success"
        )
        
    except Exception as e:
        logger.error(f"反馈提交失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"反馈提交失败: {str(e)}")


@router.get("/feedback/{task_id}", response_model=List[dict])
async def get_feedback(
    task_id: str,
    feedback_db: FeedbackDB = Depends(get_feedback_db),
    api_key: str = Depends(verify_api_key)
):
    """
    获取特定任务的反馈信息
    
    Args:
        task_id: 任务ID
        feedback_db: 反馈数据库
        api_key: API密钥
    
    Returns:
        List[dict]: 反馈列表
    """
    try:
        feedback_list = await feedback_db.get_feedback_by_task(task_id)
        return feedback_list
        
    except Exception as e:
        logger.error(f"获取反馈失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取反馈失败: {str(e)}")


async def _calculate_model_quality(request: EvaluateRequest) -> float:
    """
    计算模型质量评分
    
    Args:
        request: 评估请求
    
    Returns:
        float: 质量评分 (0-100)
    """
    # 这里实现具体的评估逻辑
    # 可以基于几何复杂度、纹理质量、文件大小等因素
    
    base_score = 75.0  # 基础分数
    
    # 根据不同指标调整分数
    if request.metrics:
        for metric, value in request.metrics.items():
            if metric == "geometry_quality" and value > 0.8:
                base_score += 10
            elif metric == "texture_quality" and value > 0.8:
                base_score += 10
            elif metric == "file_size" and value < 50:  # MB
                base_score += 5
    
    return min(100.0, max(0.0, base_score))
