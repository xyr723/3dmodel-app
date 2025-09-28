"""
文件存储服务
"""
import os
import aiofiles
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from google.cloud import storage as gcs

from app.core.config import settings, get_storage_config
from app.utils.logger import logger
from app.utils.file_utils import ensure_directory_exists, get_file_size, get_file_extension


class StorageService:
    """文件存储服务类"""
    
    def __init__(self):
        self.config = get_storage_config()
        self.storage_type = self.config["type"]
        
        # 初始化不同的存储客户端
        if self.storage_type == "s3":
            self.s3_client = self._init_s3_client()
        elif self.storage_type == "gcs":
            self.gcs_client = self._init_gcs_client()
        else:
            # 本地存储
            self.base_path = self.config["path"]
            ensure_directory_exists(self.base_path)
    
    def _init_s3_client(self):
        """初始化S3客户端"""
        try:
            return boto3.client(
                's3',
                aws_access_key_id=self.config["access_key"],
                aws_secret_access_key=self.config["secret_key"],
                region_name=self.config["region"]
            )
        except Exception as e:
            logger.error(f"S3客户端初始化失败: {str(e)}")
            return None
    
    def _init_gcs_client(self):
        """初始化Google Cloud Storage客户端"""
        try:
            return gcs.Client()
        except Exception as e:
            logger.error(f"GCS客户端初始化失败: {str(e)}")
            return None
    
    async def save_model_file(
        self, 
        task_id: str, 
        file_data: bytes, 
        file_format: str
    ) -> str:
        """
        保存模型文件
        
        Args:
            task_id: 任务ID
            file_data: 文件数据
            file_format: 文件格式
        
        Returns:
            str: 文件路径或URL
        """
        filename = f"{task_id}.{file_format}"
        
        if self.storage_type == "local":
            return await self._save_local_file(filename, file_data, "models")
        elif self.storage_type == "s3":
            return await self._save_s3_file(filename, file_data, "models")
        elif self.storage_type == "gcs":
            return await self._save_gcs_file(filename, file_data, "models")
        else:
            raise ValueError(f"不支持的存储类型: {self.storage_type}")
    
    async def save_preview_image(
        self, 
        task_id: str, 
        image_data: bytes, 
        image_format: str = "png"
    ) -> str:
        """
        保存预览图
        
        Args:
            task_id: 任务ID
            image_data: 图片数据
            image_format: 图片格式
        
        Returns:
            str: 图片路径或URL
        """
        filename = f"{task_id}_preview.{image_format}"
        
        if self.storage_type == "local":
            return await self._save_local_file(filename, image_data, "previews")
        elif self.storage_type == "s3":
            return await self._save_s3_file(filename, image_data, "previews")
        elif self.storage_type == "gcs":
            return await self._save_gcs_file(filename, image_data, "previews")
        else:
            raise ValueError(f"不支持的存储类型: {self.storage_type}")
    
    async def _save_local_file(
        self, 
        filename: str, 
        file_data: bytes, 
        subfolder: str
    ) -> str:
        """保存文件到本地"""
        # 创建日期子目录
        date_folder = datetime.now().strftime("%Y/%m/%d")
        full_path = os.path.join(self.base_path, subfolder, date_folder)
        ensure_directory_exists(full_path)
        
        file_path = os.path.join(full_path, filename)
        
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            logger.info(f"文件已保存到本地: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"保存本地文件失败: {str(e)}")
            raise
    
    async def _save_s3_file(
        self, 
        filename: str, 
        file_data: bytes, 
        subfolder: str
    ) -> str:
        """保存文件到S3"""
        if not self.s3_client:
            raise Exception("S3客户端未初始化")
        
        # 创建S3键
        date_folder = datetime.now().strftime("%Y/%m/%d")
        s3_key = f"{subfolder}/{date_folder}/{filename}"
        bucket_name = self.config["bucket"]
        
        try:
            self.s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType=self._get_content_type(filename)
            )
            
            # 生成文件URL
            file_url = f"https://{bucket_name}.s3.{self.config['region']}.amazonaws.com/{s3_key}"
            logger.info(f"文件已保存到S3: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"保存S3文件失败: {str(e)}")
            raise
    
    async def _save_gcs_file(
        self, 
        filename: str, 
        file_data: bytes, 
        subfolder: str
    ) -> str:
        """保存文件到Google Cloud Storage"""
        if not self.gcs_client:
            raise Exception("GCS客户端未初始化")
        
        # 创建GCS路径
        date_folder = datetime.now().strftime("%Y/%m/%d")
        blob_name = f"{subfolder}/{date_folder}/{filename}"
        bucket_name = self.config["bucket"]
        
        try:
            bucket = self.gcs_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.upload_from_string(
                file_data,
                content_type=self._get_content_type(filename)
            )
            
            # 生成文件URL
            file_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
            logger.info(f"文件已保存到GCS: {file_url}")
            return file_url
            
        except Exception as e:
            logger.error(f"保存GCS文件失败: {str(e)}")
            raise
    
    async def get_file(self, file_path: str) -> Optional[bytes]:
        """
        获取文件内容
        
        Args:
            file_path: 文件路径
        
        Returns:
            Optional[bytes]: 文件内容
        """
        if self.storage_type == "local":
            return await self._get_local_file(file_path)
        elif self.storage_type == "s3":
            return await self._get_s3_file(file_path)
        elif self.storage_type == "gcs":
            return await self._get_gcs_file(file_path)
        else:
            return None
    
    async def _get_local_file(self, file_path: str) -> Optional[bytes]:
        """获取本地文件"""
        try:
            if os.path.exists(file_path):
                async with aiofiles.open(file_path, 'rb') as f:
                    return await f.read()
        except Exception as e:
            logger.error(f"读取本地文件失败: {str(e)}")
        
        return None
    
    async def _get_s3_file(self, s3_key: str) -> Optional[bytes]:
        """获取S3文件"""
        if not self.s3_client:
            return None
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.config["bucket"],
                Key=s3_key
            )
            return response['Body'].read()
            
        except ClientError as e:
            logger.error(f"读取S3文件失败: {str(e)}")
            return None
    
    async def _get_gcs_file(self, blob_name: str) -> Optional[bytes]:
        """获取GCS文件"""
        if not self.gcs_client:
            return None
        
        try:
            bucket = self.gcs_client.bucket(self.config["bucket"])
            blob = bucket.blob(blob_name)
            return blob.download_as_bytes()
            
        except Exception as e:
            logger.error(f"读取GCS文件失败: {str(e)}")
            return None
    
    async def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            bool: 是否成功删除
        """
        if self.storage_type == "local":
            return await self._delete_local_file(file_path)
        elif self.storage_type == "s3":
            return await self._delete_s3_file(file_path)
        elif self.storage_type == "gcs":
            return await self._delete_gcs_file(file_path)
        else:
            return False
    
    async def _delete_local_file(self, file_path: str) -> bool:
        """删除本地文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"本地文件已删除: {file_path}")
                return True
        except Exception as e:
            logger.error(f"删除本地文件失败: {str(e)}")
        
        return False
    
    async def _delete_s3_file(self, s3_key: str) -> bool:
        """删除S3文件"""
        if not self.s3_client:
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.config["bucket"],
                Key=s3_key
            )
            logger.info(f"S3文件已删除: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"删除S3文件失败: {str(e)}")
            return False
    
    async def _delete_gcs_file(self, blob_name: str) -> bool:
        """删除GCS文件"""
        if not self.gcs_client:
            return False
        
        try:
            bucket = self.gcs_client.bucket(self.config["bucket"])
            blob = bucket.blob(blob_name)
            blob.delete()
            logger.info(f"GCS文件已删除: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"删除GCS文件失败: {str(e)}")
            return False
    
    def _get_content_type(self, filename: str) -> str:
        """根据文件扩展名获取Content-Type"""
        extension = get_file_extension(filename).lower()
        
        content_types = {
            '.obj': 'application/octet-stream',
            '.glb': 'model/gltf-binary',
            '.gltf': 'model/gltf+json',
            '.ply': 'application/octet-stream',
            '.fbx': 'application/octet-stream',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        
        return content_types.get(extension, 'application/octet-stream')
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        获取存储统计信息
        
        Returns:
            Dict[str, Any]: 存储统计
        """
        stats = {
            "storage_type": self.storage_type,
            "total_files": 0,
            "total_size": 0
        }
        
        if self.storage_type == "local":
            # 统计本地存储
            try:
                for root, dirs, files in os.walk(self.base_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        stats["total_files"] += 1
                        stats["total_size"] += get_file_size(file_path)
            except Exception as e:
                logger.error(f"获取本地存储统计失败: {str(e)}")
        
        # S3和GCS的统计需要调用相应的API，这里简化处理
        
        return stats
