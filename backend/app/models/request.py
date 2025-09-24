"""
请求数据模型
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class ModelStyle(str, Enum):
    """模型风格枚举"""
    REALISTIC = "realistic"
    CARTOON = "cartoon"
    LOW_POLY = "low_poly"
    ABSTRACT = "abstract"
    ARCHITECTURAL = "architectural"


class GenerationMode(str, Enum):
    """生成模式枚举"""
    TEXT_TO_3D = "text_to_3d"
    IMAGE_TO_3D = "image_to_3d"
    SKETCH_TO_3D = "sketch_to_3d"


class GenerateRequest(BaseModel):
    """3D模型生成请求"""
    
    prompt: str = Field(..., min_length=1, max_length=1000, description="生成提示词")
    style: ModelStyle = Field(default=ModelStyle.REALISTIC, description="模型风格")
    mode: GenerationMode = Field(default=GenerationMode.TEXT_TO_3D, description="生成模式")
    
    # 可选参数
    image_url: Optional[str] = Field(None, description="参考图片URL（image_to_3d模式）")
    negative_prompt: Optional[str] = Field(None, max_length=500, description="负面提示词")
    quality: Optional[str] = Field("medium", description="生成质量 (low/medium/high)")
    resolution: Optional[int] = Field(512, ge=256, le=2048, description="分辨率")
    
    # 高级参数
    seed: Optional[int] = Field(None, description="随机种子")
    steps: Optional[int] = Field(50, ge=10, le=150, description="生成步数")
    guidance_scale: Optional[float] = Field(7.5, ge=1.0, le=20.0, description="引导强度")
    
    # 输出格式
    output_format: Optional[str] = Field("obj", description="输出格式")
    include_texture: bool = Field(True, description="是否包含纹理")
    include_animation: bool = Field(False, description="是否包含动画")
    
    # 用户信息
    user_id: Optional[str] = Field(None, description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """验证提示词"""
        if not v or v.strip() == "":
            raise ValueError("提示词不能为空")
        return v.strip()
    
    @validator('image_url')
    def validate_image_url(cls, v, values):
        """验证图片URL"""
        if values.get('mode') == GenerationMode.IMAGE_TO_3D and not v:
            raise ValueError("image_to_3d模式需要提供图片URL")
        return v


class EvaluateRequest(BaseModel):
    """模型评估请求"""
    
    task_id: str = Field(..., description="任务ID")
    metrics: Optional[Dict[str, float]] = Field(None, description="评估指标")
    auto_evaluate: bool = Field(True, description="是否自动评估")
    
    # 评估参数
    check_geometry: bool = Field(True, description="检查几何质量")
    check_texture: bool = Field(True, description="检查纹理质量")
    check_topology: bool = Field(True, description="检查拓扑结构")
    
    @validator('task_id')
    def validate_task_id(cls, v):
        """验证任务ID"""
        if not v or len(v) < 8:
            raise ValueError("无效的任务ID")
        return v


class FeedbackRequest(BaseModel):
    """用户反馈请求"""
    
    task_id: str = Field(..., description="任务ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    rating: int = Field(..., ge=1, le=5, description="评分 (1-5)")
    comment: Optional[str] = Field(None, max_length=1000, description="评论")
    feedback_type: str = Field("general", description="反馈类型")
    
    # 详细评分
    quality_rating: Optional[int] = Field(None, ge=1, le=5, description="质量评分")
    accuracy_rating: Optional[int] = Field(None, ge=1, le=5, description="准确性评分")
    speed_rating: Optional[int] = Field(None, ge=1, le=5, description="速度评分")
    
    # 问题分类
    issues: Optional[List[str]] = Field(None, description="问题列表")
    suggestions: Optional[str] = Field(None, max_length=500, description="改进建议")
    
    @validator('task_id')
    def validate_task_id(cls, v):
        """验证任务ID"""
        if not v or len(v) < 8:
            raise ValueError("无效的任务ID")
        return v


class BatchGenerateRequest(BaseModel):
    """批量生成请求"""
    
    requests: List[GenerateRequest] = Field(..., min_items=1, max_items=10)
    priority: Optional[str] = Field("normal", description="优先级")
    callback_url: Optional[str] = Field(None, description="回调URL")
    
    @validator('requests')
    def validate_requests(cls, v):
        """验证批量请求"""
        if len(v) > 10:
            raise ValueError("批量请求最多支持10个")
        return v


class ModelOptimizeRequest(BaseModel):
    """模型优化请求"""
    
    task_id: str = Field(..., description="任务ID")
    target_size: Optional[int] = Field(None, description="目标文件大小(KB)")
    target_polygons: Optional[int] = Field(None, description="目标面数")
    optimize_texture: bool = Field(True, description="优化纹理")
    optimize_geometry: bool = Field(True, description="优化几何")
    
    @validator('task_id')
    def validate_task_id(cls, v):
        """验证任务ID"""
        if not v or len(v) < 8:
            raise ValueError("无效的任务ID")
        return v


class SketchfabSearchRequest(BaseModel):
    """Sketchfab模型搜索请求"""
    
    query: str = Field(..., min_length=1, max_length=200, description="搜索关键词")
    category: Optional[str] = Field(None, description="模型分类")
    license: Optional[str] = Field("cc", description="许可证类型 (cc, cc-by, cc-by-sa等)")
    animated: Optional[bool] = Field(None, description="是否包含动画")
    rigged: Optional[bool] = Field(None, description="是否有骨骼绑定")
    downloadable: bool = Field(True, description="是否可下载")
    
    # 分页参数
    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(20, ge=1, le=100, description="每页数量")
    
    # 排序参数
    sort_by: Optional[str] = Field("relevance", description="排序方式 (relevance, likes, views, recent)")
    
    # 筛选参数
    min_face_count: Optional[int] = Field(None, ge=0, description="最小面数")
    max_face_count: Optional[int] = Field(None, ge=0, description="最大面数")
    staff_picked: Optional[bool] = Field(None, description="是否为官方推荐")
    
    @validator('query')
    def validate_query(cls, v):
        """验证搜索关键词"""
        if not v or v.strip() == "":
            raise ValueError("搜索关键词不能为空")
        return v.strip()
    
    @validator('max_face_count')
    def validate_face_count(cls, v, values):
        """验证面数范围"""
        min_face = values.get('min_face_count')
        if min_face and v and v < min_face:
            raise ValueError("最大面数不能小于最小面数")
        return v


class SketchfabDownloadRequest(BaseModel):
    """Sketchfab模型下载请求"""
    
    model_uid: str = Field(..., description="Sketchfab模型UID")
    format: Optional[str] = Field("original", description="下载格式")
    user_id: Optional[str] = Field(None, description="用户ID")
    
    @validator('model_uid')
    def validate_model_uid(cls, v):
        """验证模型UID"""
        if not v or len(v) < 8:
            raise ValueError("无效的模型UID")
        return v