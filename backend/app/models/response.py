"""
响应数据模型
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerateResponse(BaseModel):
    """3D模型生成响应"""
    
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    message: str = Field(..., description="响应消息")
    
    # 生成结果
    model_url: Optional[str] = Field(None, description="模型文件URL")
    preview_url: Optional[str] = Field(None, description="预览图URL")
    download_url: Optional[str] = Field(None, description="下载链接")
    
    # 模型信息
    file_format: Optional[str] = Field(None, description="文件格式")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    polygon_count: Optional[int] = Field(None, description="面数")
    vertex_count: Optional[int] = Field(None, description="顶点数")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    processing_time: Optional[float] = Field(None, description="处理时间(秒)")
    
    # 额外信息
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    error_details: Optional[str] = Field(None, description="错误详情")


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="进度百分比")
    message: str = Field(..., description="状态消息")
    
    # 时间信息
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    estimated_completion: Optional[datetime] = Field(None, description="预计完成时间")
    
    # 结果信息（如果完成）
    result: Optional[GenerateResponse] = Field(None, description="生成结果")


class EvaluateResponse(BaseModel):
    """模型评估响应"""
    
    task_id: str = Field(..., description="任务ID")
    evaluation_id: str = Field(..., description="评估ID")
    score: float = Field(..., ge=0.0, le=100.0, description="总体评分")
    message: str = Field(..., description="评估消息")
    
    # 详细评分
    geometry_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="几何质量评分")
    texture_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="纹理质量评分")
    topology_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="拓扑质量评分")
    
    # 评估详情
    issues: Optional[List[str]] = Field(None, description="发现的问题")
    recommendations: Optional[List[str]] = Field(None, description="改进建议")
    
    # 时间信息
    evaluated_at: datetime = Field(default_factory=datetime.utcnow, description="评估时间")
    
    # 技术指标
    metrics: Optional[Dict[str, float]] = Field(None, description="技术指标")


class FeedbackResponse(BaseModel):
    """用户反馈响应"""
    
    feedback_id: str = Field(..., description="反馈ID")
    status: str = Field(..., description="提交状态")
    message: str = Field(..., description="响应消息")
    
    # 时间信息
    submitted_at: datetime = Field(default_factory=datetime.utcnow, description="提交时间")
    
    # 额外信息
    thank_you_message: Optional[str] = Field(None, description="感谢消息")


class BatchGenerateResponse(BaseModel):
    """批量生成响应"""
    
    batch_id: str = Field(..., description="批次ID")
    total_count: int = Field(..., description="总任务数")
    submitted_count: int = Field(..., description="已提交任务数")
    
    # 任务列表
    tasks: List[GenerateResponse] = Field(..., description="任务列表")
    
    # 状态统计
    status_summary: Dict[str, int] = Field(..., description="状态统计")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")


class ModelOptimizeResponse(BaseModel):
    """模型优化响应"""
    
    task_id: str = Field(..., description="原任务ID")
    optimize_id: str = Field(..., description="优化ID")
    status: TaskStatus = Field(..., description="优化状态")
    message: str = Field(..., description="响应消息")
    
    # 优化结果
    optimized_url: Optional[str] = Field(None, description="优化后模型URL")
    original_size: Optional[int] = Field(None, description="原始文件大小")
    optimized_size: Optional[int] = Field(None, description="优化后文件大小")
    compression_ratio: Optional[float] = Field(None, description="压缩比")
    
    # 质量对比
    quality_loss: Optional[float] = Field(None, description="质量损失百分比")
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class ErrorResponse(BaseModel):
    """错误响应"""
    
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误消息")
    error_type: str = Field(..., description="错误类型")
    
    # 详细信息
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    suggestions: Optional[List[str]] = Field(None, description="解决建议")
    
    # 时间信息
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="错误时间")
    
    # 请求信息
    request_id: Optional[str] = Field(None, description="请求ID")


class HealthResponse(BaseModel):
    """健康检查响应"""
    
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="检查时间")
    version: str = Field(..., description="版本号")
    
    # 服务信息
    uptime: Optional[float] = Field(None, description="运行时间(秒)")
    memory_usage: Optional[float] = Field(None, description="内存使用率")
    cpu_usage: Optional[float] = Field(None, description="CPU使用率")
    
    # 依赖服务状态
    database_status: Optional[str] = Field(None, description="数据库状态")
    cache_status: Optional[str] = Field(None, description="缓存状态")
    storage_status: Optional[str] = Field(None, description="存储状态")
    
    # 统计信息
    total_requests: Optional[int] = Field(None, description="总请求数")
    active_tasks: Optional[int] = Field(None, description="活跃任务数")


class ApiUsageResponse(BaseModel):
    """API使用情况响应"""
    
    api_key: str = Field(..., description="API密钥（部分显示）")
    usage_period: str = Field(..., description="使用周期")
    
    # 使用统计
    total_requests: int = Field(..., description="总请求数")
    successful_requests: int = Field(..., description="成功请求数")
    failed_requests: int = Field(..., description="失败请求数")
    
    # 配额信息
    quota_limit: Optional[int] = Field(None, description="配额限制")
    quota_used: int = Field(..., description="已使用配额")
    quota_remaining: Optional[int] = Field(None, description="剩余配额")
    
    # 时间信息
    period_start: datetime = Field(..., description="周期开始时间")
    period_end: datetime = Field(..., description="周期结束时间")
    last_request: Optional[datetime] = Field(None, description="最后请求时间")


class SketchfabModel(BaseModel):
    """Sketchfab模型信息"""
    
    uid: str = Field(..., description="模型唯一标识符")
    name: str = Field(..., description="模型名称")
    description: Optional[str] = Field(None, description="模型描述")
    
    # 作者信息
    author: str = Field(..., description="作者名称")
    author_url: Optional[str] = Field(None, description="作者链接")
    
    # 模型属性
    face_count: Optional[int] = Field(None, description="面数")
    vertex_count: Optional[int] = Field(None, description="顶点数")
    animated: bool = Field(False, description="是否有动画")
    rigged: bool = Field(False, description="是否有骨骼")
    
    # 许可证信息
    license: Optional[str] = Field(None, description="许可证类型")
    license_label: Optional[str] = Field(None, description="许可证标签")
    
    # 统计信息
    view_count: Optional[int] = Field(None, description="浏览次数")
    like_count: Optional[int] = Field(None, description="点赞数")
    comment_count: Optional[int] = Field(None, description="评论数")
    
    # 媒体信息
    thumbnail_url: str = Field(..., description="缩略图URL")
    preview_url: Optional[str] = Field(None, description="预览图URL")
    embed_url: Optional[str] = Field(None, description="嵌入链接")
    
    # 下载信息
    downloadable: bool = Field(False, description="是否可下载")
    download_url: Optional[str] = Field(None, description="下载链接")
    
    # 分类标签
    categories: Optional[List[str]] = Field(None, description="分类标签")
    tags: Optional[List[str]] = Field(None, description="标签")
    
    # 时间信息
    published_at: Optional[datetime] = Field(None, description="发布时间")
    created_at: Optional[datetime] = Field(None, description="创建时间")


class SketchfabSearchResponse(BaseModel):
    """Sketchfab搜索响应"""
    
    query: str = Field(..., description="搜索关键词")
    total_count: int = Field(..., description="总结果数")
    page: int = Field(..., description="当前页码")
    per_page: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    
    # 搜索结果
    models: List[SketchfabModel] = Field(..., description="模型列表")
    
    # 搜索统计
    search_time: Optional[float] = Field(None, description="搜索耗时(秒)")
    
    # 筛选统计
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="应用的筛选条件")
    
    # 时间信息
    searched_at: datetime = Field(default_factory=datetime.utcnow, description="搜索时间")


class SketchfabDownloadResponse(BaseModel):
    """Sketchfab下载响应"""
    
    model_uid: str = Field(..., description="模型UID")
    download_id: str = Field(..., description="下载ID")
    status: str = Field(..., description="下载状态")
    message: str = Field(..., description="响应消息")
    
    # 下载信息
    download_url: Optional[str] = Field(None, description="下载链接")
    file_format: Optional[str] = Field(None, description="文件格式")
    file_size: Optional[int] = Field(None, description="文件大小(字节)")
    
    # 模型信息
    model_name: Optional[str] = Field(None, description="模型名称")
    author: Optional[str] = Field(None, description="作者")
    license: Optional[str] = Field(None, description="许可证")
    
    # 时间信息
    requested_at: datetime = Field(default_factory=datetime.utcnow, description="请求时间")
    expires_at: Optional[datetime] = Field(None, description="链接过期时间")
    
    # 使用限制
    attribution_required: bool = Field(True, description="是否需要署名")
    commercial_use: bool = Field(False, description="是否允许商用")