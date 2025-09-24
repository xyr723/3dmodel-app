"""
数据库连接和管理
"""
import asyncio
from typing import Optional, Dict, Any, List
import motor.motor_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, Float, Text, Boolean
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings, get_database_url
from app.utils.logger import logger

# SQLAlchemy Base
Base = declarative_base()

# 全局数据库连接
db_engine = None
async_session_maker = None
mongo_client = None
mongo_db = None


class TaskRecord(Base):
    """任务记录表（SQLAlchemy模型）"""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    style = Column(String)
    mode = Column(String)
    user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    processing_time = Column(Float)
    model_url = Column(String)
    file_path = Column(String)
    error_message = Column(Text)
    task_metadata = Column(Text)  # JSON字符串


class FeedbackRecord(Base):
    """反馈记录表（SQLAlchemy模型）"""
    __tablename__ = "feedback"
    
    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False)
    user_id = Column(String)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    feedback_type = Column(String)
    quality_rating = Column(Integer)
    accuracy_rating = Column(Integer)
    speed_rating = Column(Integer)
    issues = Column(Text)  # JSON字符串
    suggestions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class EvaluationRecord(Base):
    """评估记录表（SQLAlchemy模型）"""
    __tablename__ = "evaluations"
    
    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    geometry_score = Column(Float)
    texture_score = Column(Float)
    topology_score = Column(Float)
    metrics = Column(Text)  # JSON字符串
    issues = Column(Text)  # JSON字符串
    recommendations = Column(Text)  # JSON字符串
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """初始化数据库连接"""
    global db_engine, async_session_maker, mongo_client, mongo_db
    
    database_url = get_database_url()
    
    try:
        if database_url.startswith('mongodb'):
            # MongoDB连接
            mongo_client = motor.motor_asyncio.AsyncIOMotorClient(database_url)
            mongo_db = mongo_client.get_default_database()
            
            # 测试连接
            await mongo_client.admin.command('ping')
            logger.info("MongoDB连接成功")
            
        else:
            # SQL数据库连接（SQLite, PostgreSQL等）
            db_engine = create_async_engine(
                database_url,
                echo=settings.DEBUG,
                pool_pre_ping=True
            )
            
            async_session_maker = async_sessionmaker(
                db_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # 创建表
            async with db_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("SQL数据库连接成功")
    
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        raise


async def get_db_session():
    """获取数据库会话（SQL数据库）"""
    if async_session_maker is None:
        raise RuntimeError("数据库未初始化")
    
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def get_mongo_db():
    """获取MongoDB数据库实例"""
    if mongo_db is None:
        raise RuntimeError("MongoDB未初始化")
    return mongo_db


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.use_mongodb = get_database_url().startswith('mongodb')
    
    async def save_task(self, task_data: Dict[str, Any]) -> str:
        """
        保存任务记录
        
        Args:
            task_data: 任务数据
        
        Returns:
            str: 任务ID
        """
        if self.use_mongodb:
            return await self._save_task_mongo(task_data)
        else:
            return await self._save_task_sql(task_data)
    
    async def _save_task_mongo(self, task_data: Dict[str, Any]) -> str:
        """保存任务到MongoDB"""
        db = get_mongo_db()
        collection = db.tasks
        
        # 添加时间戳
        task_data['created_at'] = datetime.utcnow()
        
        result = await collection.insert_one(task_data)
        logger.info(f"任务已保存到MongoDB: {task_data['id']}")
        return task_data['id']
    
    async def _save_task_sql(self, task_data: Dict[str, Any]) -> str:
        """保存任务到SQL数据库"""
        async with async_session_maker() as session:
            task_record = TaskRecord(
                id=task_data['id'],
                status=task_data['status'],
                prompt=task_data['prompt'],
                style=task_data.get('style'),
                mode=task_data.get('mode'),
                user_id=task_data.get('user_id'),
                model_url=task_data.get('model_url'),
                file_path=task_data.get('file_path'),
                error_message=task_data.get('error_message'),
                processing_time=task_data.get('processing_time'),
                completed_at=task_data.get('completed_at'),
                task_metadata=str(task_data.get('metadata', {}))
            )
            
            session.add(task_record)
            await session.commit()
            
            logger.info(f"任务已保存到SQL数据库: {task_data['id']}")
            return task_data['id']
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务记录
        
        Args:
            task_id: 任务ID
        
        Returns:
            Optional[Dict[str, Any]]: 任务数据
        """
        if self.use_mongodb:
            return await self._get_task_mongo(task_id)
        else:
            return await self._get_task_sql(task_id)
    
    async def _get_task_mongo(self, task_id: str) -> Optional[Dict[str, Any]]:
        """从MongoDB获取任务"""
        db = get_mongo_db()
        collection = db.tasks
        
        task = await collection.find_one({"id": task_id})
        if task:
            # 移除MongoDB的_id字段
            task.pop('_id', None)
        
        return task
    
    async def _get_task_sql(self, task_id: str) -> Optional[Dict[str, Any]]:
        """从SQL数据库获取任务"""
        async with async_session_maker() as session:
            from sqlalchemy import select
            
            result = await session.execute(
                select(TaskRecord).where(TaskRecord.id == task_id)
            )
            task_record = result.scalar_one_or_none()
            
            if task_record:
                return {
                    'id': task_record.id,
                    'status': task_record.status,
                    'prompt': task_record.prompt,
                    'style': task_record.style,
                    'mode': task_record.mode,
                    'user_id': task_record.user_id,
                    'created_at': task_record.created_at,
                    'completed_at': task_record.completed_at,
                    'processing_time': task_record.processing_time,
                    'model_url': task_record.model_url,
                    'file_path': task_record.file_path,
                    'error_message': task_record.error_message,
                    'metadata': task_record.task_metadata
                }
        
        return None
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新任务记录
        
        Args:
            task_id: 任务ID
            updates: 更新数据
        
        Returns:
            bool: 是否成功更新
        """
        if self.use_mongodb:
            return await self._update_task_mongo(task_id, updates)
        else:
            return await self._update_task_sql(task_id, updates)
    
    async def _update_task_mongo(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """更新MongoDB中的任务"""
        db = get_mongo_db()
        collection = db.tasks
        
        updates['updated_at'] = datetime.utcnow()
        
        result = await collection.update_one(
            {"id": task_id},
            {"$set": updates}
        )
        
        return result.modified_count > 0
    
    async def _update_task_sql(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """更新SQL数据库中的任务"""
        async with async_session_maker() as session:
            from sqlalchemy import select, update
            
            stmt = update(TaskRecord).where(TaskRecord.id == task_id).values(**updates)
            result = await session.execute(stmt)
            await session.commit()
            
            return result.rowcount > 0
    
    async def list_tasks(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        列出任务记录
        
        Args:
            user_id: 用户ID过滤
            status: 状态过滤
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            List[Dict[str, Any]]: 任务列表
        """
        if self.use_mongodb:
            return await self._list_tasks_mongo(user_id, status, limit, offset)
        else:
            return await self._list_tasks_sql(user_id, status, limit, offset)
    
    async def _list_tasks_mongo(
        self,
        user_id: Optional[str],
        status: Optional[str],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """从MongoDB列出任务"""
        db = get_mongo_db()
        collection = db.tasks
        
        # 构建查询条件
        query = {}
        if user_id:
            query['user_id'] = user_id
        if status:
            query['status'] = status
        
        # 执行查询
        cursor = collection.find(query).sort('created_at', -1).skip(offset).limit(limit)
        tasks = []
        
        async for task in cursor:
            task.pop('_id', None)  # 移除MongoDB的_id字段
            tasks.append(task)
        
        return tasks
    
    async def _list_tasks_sql(
        self,
        user_id: Optional[str],
        status: Optional[str],
        limit: int,
        offset: int
    ) -> List[Dict[str, Any]]:
        """从SQL数据库列出任务"""
        async with async_session_maker() as session:
            from sqlalchemy import select
            
            query = select(TaskRecord)
            
            if user_id:
                query = query.where(TaskRecord.user_id == user_id)
            if status:
                query = query.where(TaskRecord.status == status)
            
            query = query.order_by(TaskRecord.created_at.desc()).offset(offset).limit(limit)
            
            result = await session.execute(query)
            task_records = result.scalars().all()
            
            tasks = []
            for record in task_records:
                tasks.append({
                    'id': record.id,
                    'status': record.status,
                    'prompt': record.prompt,
                    'style': record.style,
                    'mode': record.mode,
                    'user_id': record.user_id,
                    'created_at': record.created_at,
                    'completed_at': record.completed_at,
                    'processing_time': record.processing_time,
                    'model_url': record.model_url,
                    'file_path': record.file_path,
                    'error_message': record.error_message,
                    'metadata': record.task_metadata
                })
            
            return tasks
    
    async def get_task_stats(self) -> Dict[str, Any]:
        """
        获取任务统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        if self.use_mongodb:
            return await self._get_task_stats_mongo()
        else:
            return await self._get_task_stats_sql()
    
    async def _get_task_stats_mongo(self) -> Dict[str, Any]:
        """从MongoDB获取任务统计"""
        db = get_mongo_db()
        collection = db.tasks
        
        # 使用聚合管道统计
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        status_counts = {}
        total_count = 0
        
        async for doc in cursor:
            status_counts[doc["_id"]] = doc["count"]
            total_count += doc["count"]
        
        return {
            "total_tasks": total_count,
            "status_counts": status_counts
        }
    
    async def _get_task_stats_sql(self) -> Dict[str, Any]:
        """从SQL数据库获取任务统计"""
        async with async_session_maker() as session:
            from sqlalchemy import select, func
            
            # 总任务数
            total_result = await session.execute(
                select(func.count(TaskRecord.id))
            )
            total_tasks = total_result.scalar()
            
            # 按状态统计
            status_result = await session.execute(
                select(TaskRecord.status, func.count(TaskRecord.id))
                .group_by(TaskRecord.status)
            )
            
            status_counts = {}
            for status, count in status_result:
                status_counts[status] = count
            
            return {
                "total_tasks": total_tasks,
                "status_counts": status_counts
            }


async def close_db():
    """关闭数据库连接"""
    global db_engine, mongo_client
    
    if db_engine:
        await db_engine.dispose()
        logger.info("SQL数据库连接已关闭")
    
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB连接已关闭")
