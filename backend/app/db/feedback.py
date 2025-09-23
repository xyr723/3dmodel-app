"""
用户反馈数据库操作
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from app.db.database import get_mongo_db, async_session_maker, FeedbackRecord, EvaluationRecord
from app.utils.logger import logger


class FeedbackDB:
    """反馈数据库操作类"""
    
    def __init__(self):
        from app.core.config import get_database_url
        self.use_mongodb = get_database_url().startswith('mongodb')
    
    async def save_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, str]:
        """
        保存用户反馈
        
        Args:
            feedback_data: 反馈数据
        
        Returns:
            Dict[str, str]: 包含feedback_id的结果
        """
        feedback_id = str(uuid.uuid4())
        feedback_data['id'] = feedback_id
        feedback_data['created_at'] = datetime.utcnow()
        
        if self.use_mongodb:
            return await self._save_feedback_mongo(feedback_data)
        else:
            return await self._save_feedback_sql(feedback_data)
    
    async def _save_feedback_mongo(self, feedback_data: Dict[str, Any]) -> Dict[str, str]:
        """保存反馈到MongoDB"""
        db = get_mongo_db()
        collection = db.feedback
        
        try:
            await collection.insert_one(feedback_data)
            logger.info(f"反馈已保存到MongoDB: {feedback_data['id']}")
            return {"feedback_id": feedback_data['id']}
        except Exception as e:
            logger.error(f"保存反馈到MongoDB失败: {str(e)}")
            raise
    
    async def _save_feedback_sql(self, feedback_data: Dict[str, Any]) -> Dict[str, str]:
        """保存反馈到SQL数据库"""
        async with async_session_maker() as session:
            try:
                feedback_record = FeedbackRecord(
                    id=feedback_data['id'],
                    task_id=feedback_data['task_id'],
                    user_id=feedback_data.get('user_id'),
                    rating=feedback_data['rating'],
                    comment=feedback_data.get('comment'),
                    feedback_type=feedback_data.get('feedback_type'),
                    quality_rating=feedback_data.get('quality_rating'),
                    accuracy_rating=feedback_data.get('accuracy_rating'),
                    speed_rating=feedback_data.get('speed_rating'),
                    issues=json.dumps(feedback_data.get('issues', [])),
                    suggestions=feedback_data.get('suggestions'),
                    created_at=feedback_data['created_at']
                )
                
                session.add(feedback_record)
                await session.commit()
                
                logger.info(f"反馈已保存到SQL数据库: {feedback_data['id']}")
                return {"feedback_id": feedback_data['id']}
                
            except Exception as e:
                await session.rollback()
                logger.error(f"保存反馈到SQL数据库失败: {str(e)}")
                raise
    
    async def get_feedback_by_task(self, task_id: str) -> List[Dict[str, Any]]:
        """
        获取特定任务的所有反馈
        
        Args:
            task_id: 任务ID
        
        Returns:
            List[Dict[str, Any]]: 反馈列表
        """
        if self.use_mongodb:
            return await self._get_feedback_by_task_mongo(task_id)
        else:
            return await self._get_feedback_by_task_sql(task_id)
    
    async def _get_feedback_by_task_mongo(self, task_id: str) -> List[Dict[str, Any]]:
        """从MongoDB获取任务反馈"""
        db = get_mongo_db()
        collection = db.feedback
        
        try:
            cursor = collection.find({"task_id": task_id}).sort("created_at", -1)
            feedback_list = []
            
            async for feedback in cursor:
                feedback.pop('_id', None)  # 移除MongoDB的_id字段
                feedback_list.append(feedback)
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"从MongoDB获取任务反馈失败: {str(e)}")
            return []
    
    async def _get_feedback_by_task_sql(self, task_id: str) -> List[Dict[str, Any]]:
        """从SQL数据库获取任务反馈"""
        async with async_session_maker() as session:
            try:
                from sqlalchemy import select
                
                result = await session.execute(
                    select(FeedbackRecord)
                    .where(FeedbackRecord.task_id == task_id)
                    .order_by(FeedbackRecord.created_at.desc())
                )
                
                feedback_records = result.scalars().all()
                feedback_list = []
                
                for record in feedback_records:
                    feedback_data = {
                        'id': record.id,
                        'task_id': record.task_id,
                        'user_id': record.user_id,
                        'rating': record.rating,
                        'comment': record.comment,
                        'feedback_type': record.feedback_type,
                        'quality_rating': record.quality_rating,
                        'accuracy_rating': record.accuracy_rating,
                        'speed_rating': record.speed_rating,
                        'issues': json.loads(record.issues) if record.issues else [],
                        'suggestions': record.suggestions,
                        'created_at': record.created_at
                    }
                    feedback_list.append(feedback_data)
                
                return feedback_list
                
            except Exception as e:
                logger.error(f"从SQL数据库获取任务反馈失败: {str(e)}")
                return []
    
    async def save_evaluation(self, evaluation_data: Dict[str, Any]) -> Dict[str, str]:
        """
        保存模型评估结果
        
        Args:
            evaluation_data: 评估数据
        
        Returns:
            Dict[str, str]: 包含evaluation_id的结果
        """
        evaluation_id = str(uuid.uuid4())
        evaluation_data['id'] = evaluation_id
        evaluation_data['created_at'] = datetime.utcnow()
        
        if self.use_mongodb:
            return await self._save_evaluation_mongo(evaluation_data)
        else:
            return await self._save_evaluation_sql(evaluation_data)
    
    async def _save_evaluation_mongo(self, evaluation_data: Dict[str, Any]) -> Dict[str, str]:
        """保存评估到MongoDB"""
        db = get_mongo_db()
        collection = db.evaluations
        
        try:
            await collection.insert_one(evaluation_data)
            logger.info(f"评估已保存到MongoDB: {evaluation_data['id']}")
            return {"evaluation_id": evaluation_data['id']}
        except Exception as e:
            logger.error(f"保存评估到MongoDB失败: {str(e)}")
            raise
    
    async def _save_evaluation_sql(self, evaluation_data: Dict[str, Any]) -> Dict[str, str]:
        """保存评估到SQL数据库"""
        async with async_session_maker() as session:
            try:
                evaluation_record = EvaluationRecord(
                    id=evaluation_data['id'],
                    task_id=evaluation_data['task_id'],
                    score=evaluation_data['score'],
                    geometry_score=evaluation_data.get('geometry_score'),
                    texture_score=evaluation_data.get('texture_score'),
                    topology_score=evaluation_data.get('topology_score'),
                    metrics=json.dumps(evaluation_data.get('metrics', {})),
                    issues=json.dumps(evaluation_data.get('issues', [])),
                    recommendations=json.dumps(evaluation_data.get('recommendations', [])),
                    created_at=evaluation_data['created_at']
                )
                
                session.add(evaluation_record)
                await session.commit()
                
                logger.info(f"评估已保存到SQL数据库: {evaluation_data['id']}")
                return {"evaluation_id": evaluation_data['id']}
                
            except Exception as e:
                await session.rollback()
                logger.error(f"保存评估到SQL数据库失败: {str(e)}")
                raise
    
    async def get_evaluation_by_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务的评估结果
        
        Args:
            task_id: 任务ID
        
        Returns:
            Optional[Dict[str, Any]]: 评估数据
        """
        if self.use_mongodb:
            return await self._get_evaluation_by_task_mongo(task_id)
        else:
            return await self._get_evaluation_by_task_sql(task_id)
    
    async def _get_evaluation_by_task_mongo(self, task_id: str) -> Optional[Dict[str, Any]]:
        """从MongoDB获取任务评估"""
        db = get_mongo_db()
        collection = db.evaluations
        
        try:
            evaluation = await collection.find_one(
                {"task_id": task_id},
                sort=[("created_at", -1)]
            )
            
            if evaluation:
                evaluation.pop('_id', None)  # 移除MongoDB的_id字段
            
            return evaluation
            
        except Exception as e:
            logger.error(f"从MongoDB获取任务评估失败: {str(e)}")
            return None
    
    async def _get_evaluation_by_task_sql(self, task_id: str) -> Optional[Dict[str, Any]]:
        """从SQL数据库获取任务评估"""
        async with async_session_maker() as session:
            try:
                from sqlalchemy import select
                
                result = await session.execute(
                    select(EvaluationRecord)
                    .where(EvaluationRecord.task_id == task_id)
                    .order_by(EvaluationRecord.created_at.desc())
                )
                
                evaluation_record = result.scalar_one_or_none()
                
                if evaluation_record:
                    return {
                        'id': evaluation_record.id,
                        'task_id': evaluation_record.task_id,
                        'score': evaluation_record.score,
                        'geometry_score': evaluation_record.geometry_score,
                        'texture_score': evaluation_record.texture_score,
                        'topology_score': evaluation_record.topology_score,
                        'metrics': json.loads(evaluation_record.metrics) if evaluation_record.metrics else {},
                        'issues': json.loads(evaluation_record.issues) if evaluation_record.issues else [],
                        'recommendations': json.loads(evaluation_record.recommendations) if evaluation_record.recommendations else [],
                        'created_at': evaluation_record.created_at
                    }
                
                return None
                
            except Exception as e:
                logger.error(f"从SQL数据库获取任务评估失败: {str(e)}")
                return None
    
    async def get_feedback_stats(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        获取反馈统计信息
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        if self.use_mongodb:
            return await self._get_feedback_stats_mongo(start_date, end_date)
        else:
            return await self._get_feedback_stats_sql(start_date, end_date)
    
    async def _get_feedback_stats_mongo(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> Dict[str, Any]:
        """从MongoDB获取反馈统计"""
        db = get_mongo_db()
        collection = db.feedback
        
        try:
            # 构建时间范围查询
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            
            match_stage = {}
            if date_filter:
                match_stage["created_at"] = date_filter
            
            # 聚合管道
            pipeline = []
            if match_stage:
                pipeline.append({"$match": match_stage})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_feedback": {"$sum": 1},
                        "avg_rating": {"$avg": "$rating"},
                        "rating_distribution": {
                            "$push": "$rating"
                        }
                    }
                }
            ])
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            if result:
                stats = result[0]
                
                # 计算评分分布
                ratings = stats.get("rating_distribution", [])
                rating_counts = {}
                for rating in ratings:
                    rating_counts[rating] = rating_counts.get(rating, 0) + 1
                
                return {
                    "total_feedback": stats.get("total_feedback", 0),
                    "average_rating": round(stats.get("avg_rating", 0), 2),
                    "rating_distribution": rating_counts
                }
            
            return {
                "total_feedback": 0,
                "average_rating": 0,
                "rating_distribution": {}
            }
            
        except Exception as e:
            logger.error(f"从MongoDB获取反馈统计失败: {str(e)}")
            return {}
    
    async def _get_feedback_stats_sql(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> Dict[str, Any]:
        """从SQL数据库获取反馈统计"""
        async with async_session_maker() as session:
            try:
                from sqlalchemy import select, func
                
                query = select(FeedbackRecord)
                
                # 添加时间范围过滤
                if start_date:
                    query = query.where(FeedbackRecord.created_at >= start_date)
                if end_date:
                    query = query.where(FeedbackRecord.created_at <= end_date)
                
                # 总反馈数和平均评分
                stats_query = select(
                    func.count(FeedbackRecord.id).label('total_feedback'),
                    func.avg(FeedbackRecord.rating).label('avg_rating')
                )
                
                if start_date:
                    stats_query = stats_query.where(FeedbackRecord.created_at >= start_date)
                if end_date:
                    stats_query = stats_query.where(FeedbackRecord.created_at <= end_date)
                
                stats_result = await session.execute(stats_query)
                stats_row = stats_result.first()
                
                # 评分分布
                rating_query = select(
                    FeedbackRecord.rating,
                    func.count(FeedbackRecord.id).label('count')
                ).group_by(FeedbackRecord.rating)
                
                if start_date:
                    rating_query = rating_query.where(FeedbackRecord.created_at >= start_date)
                if end_date:
                    rating_query = rating_query.where(FeedbackRecord.created_at <= end_date)
                
                rating_result = await session.execute(rating_query)
                rating_distribution = {}
                
                for rating, count in rating_result:
                    rating_distribution[rating] = count
                
                return {
                    "total_feedback": stats_row.total_feedback or 0,
                    "average_rating": round(float(stats_row.avg_rating or 0), 2),
                    "rating_distribution": rating_distribution
                }
                
            except Exception as e:
                logger.error(f"从SQL数据库获取反馈统计失败: {str(e)}")
                return {}
    
    async def delete_feedback(self, feedback_id: str) -> bool:
        """
        删除反馈记录
        
        Args:
            feedback_id: 反馈ID
        
        Returns:
            bool: 是否成功删除
        """
        if self.use_mongodb:
            return await self._delete_feedback_mongo(feedback_id)
        else:
            return await self._delete_feedback_sql(feedback_id)
    
    async def _delete_feedback_mongo(self, feedback_id: str) -> bool:
        """从MongoDB删除反馈"""
        db = get_mongo_db()
        collection = db.feedback
        
        try:
            result = await collection.delete_one({"id": feedback_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"从MongoDB删除反馈失败: {str(e)}")
            return False
    
    async def _delete_feedback_sql(self, feedback_id: str) -> bool:
        """从SQL数据库删除反馈"""
        async with async_session_maker() as session:
            try:
                from sqlalchemy import delete
                
                stmt = delete(FeedbackRecord).where(FeedbackRecord.id == feedback_id)
                result = await session.execute(stmt)
                await session.commit()
                
                return result.rowcount > 0
                
            except Exception as e:
                await session.rollback()
                logger.error(f"从SQL数据库删除反馈失败: {str(e)}")
                return False
