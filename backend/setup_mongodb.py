#!/usr/bin/env python3
"""
MongoDB数据库设置脚本
"""
import asyncio
import os
import sys
from pymongo import MongoClient
from datetime import datetime

def test_mongodb_connection(connection_string="mongodb://localhost:27017"):
    """测试MongoDB连接"""
    try:
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        # 测试连接
        client.admin.command('ping')
        print("✅ MongoDB连接成功!")
        return client
    except Exception as e:
        print(f"❌ MongoDB连接失败: {str(e)}")
        print("请确保MongoDB服务已启动")
        return None

def create_mongodb_database(client, db_name="3dmodel_db"):
    """创建MongoDB数据库和集合"""
    try:
        # 获取数据库
        db = client[db_name]
        
        print(f"📁 创建数据库: {db_name}")
        
        # 创建集合并添加索引
        collections_config = {
            'tasks': {
                'indexes': [
                    ('user_id', 1),
                    ('status', 1), 
                    ('created_at', -1),
                    ('prompt', 'text')  # 文本索引用于搜索
                ],
                'sample_doc': {
                    'id': 'sample_task_001',
                    'status': 'pending',
                    'prompt': '一只可爱的小猫',
                    'style': 'realistic',
                    'mode': 'text_to_3d',
                    'user_id': 'user_123',
                    'created_at': datetime.utcnow(),
                    'metadata': {}
                }
            },
            'feedback': {
                'indexes': [
                    ('task_id', 1),
                    ('user_id', 1),
                    ('created_at', -1),
                    ('rating', 1)
                ],
                'sample_doc': {
                    'id': 'sample_feedback_001',
                    'task_id': 'sample_task_001',
                    'user_id': 'user_123',
                    'rating': 4,
                    'comment': '模型质量很好',
                    'feedback_type': 'quality',
                    'created_at': datetime.utcnow()
                }
            },
            'evaluations': {
                'indexes': [
                    ('task_id', 1),
                    ('score', -1),
                    ('created_at', -1)
                ],
                'sample_doc': {
                    'id': 'sample_eval_001',
                    'task_id': 'sample_task_001',
                    'score': 85.5,
                    'geometry_score': 90.0,
                    'texture_score': 80.0,
                    'created_at': datetime.utcnow(),
                    'metrics': {'file_size': 25.6, 'polygons': 15000}
                }
            }
        }
        
        for collection_name, config in collections_config.items():
            collection = db[collection_name]
            
            # 创建索引
            for index in config['indexes']:
                if isinstance(index, tuple):
                    collection.create_index([index])
                else:
                    collection.create_index(index)
            
            # 插入示例文档（如果集合为空）
            if collection.count_documents({}) == 0:
                collection.insert_one(config['sample_doc'])
                print(f"📋 已创建集合: {collection_name} (包含示例数据)")
            else:
                print(f"📋 集合已存在: {collection_name}")
        
        print("\n📊 数据库统计:")
        for collection_name in collections_config.keys():
            count = db[collection_name].count_documents({})
            print(f"   - {collection_name}: {count} 个文档")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建MongoDB数据库失败: {str(e)}")
        return False

def create_env_config():
    """创建环境配置文件"""
    env_content = """# MongoDB配置
MONGODB_URL=mongodb://localhost:27017/3dmodel_db

# 基础配置
APP_NAME=3D模型生成API
DEBUG=true
HOST=0.0.0.0
PORT=8000

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
API_KEY=sk_test_api_key_12345678901234567890

# 第三方API配置
MESHY_API_KEY=your_meshy_api_key_here
MODEL_PROVIDER=meshy

# 缓存配置
REDIS_URL=redis://localhost:6379/0

# 存储配置
STORAGE_TYPE=local
STORAGE_PATH=./storage

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
    
    try:
        with open('.env.mongodb', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("📝 已创建 .env.mongodb 配置文件")
        print("💡 提示: 复制到 .env 文件使用")
        return True
    except Exception as e:
        print(f"⚠️ 创建配置文件失败: {str(e)}")
        return False

def show_mongodb_installation_guide():
    """显示MongoDB安装指导"""
    print("\n🔧 MongoDB安装指导:")
    print("=" * 50)
    print("Windows安装:")
    print("1. 访问: https://www.mongodb.com/try/download/community")
    print("2. 下载MongoDB Community Server")
    print("3. 运行安装程序，选择Complete安装")
    print("4. 安装MongoDB Compass (可选的图形界面)")
    print("5. 启动MongoDB服务:")
    print("   - 方法1: 服务管理器中启动 'MongoDB Server'")
    print("   - 方法2: 命令行运行 'net start MongoDB'")
    print()
    print("验证安装:")
    print("1. 打开命令提示符")
    print("2. 运行: mongo --version")
    print("3. 连接数据库: mongo")
    print()

def main():
    """主函数"""
    print("🍃 MongoDB数据库设置向导")
    print("=" * 50)
    
    # 尝试连接MongoDB
    client = test_mongodb_connection()
    
    if client is None:
        print("\n❌ 无法连接到MongoDB")
        show_mongodb_installation_guide()
        
        choice = input("\n是否已安装MongoDB但未启动？(y/n): ").strip().lower()
        if choice == 'y':
            print("\n请启动MongoDB服务后重新运行此脚本")
        else:
            print("\n请先安装并启动MongoDB")
        return
    
    # 创建数据库
    print(f"\n🗄️ 设置MongoDB数据库...")
    if create_mongodb_database(client):
        create_env_config()
        print("\n🎉 MongoDB数据库设置完成!")
        print("\n📋 下一步:")
        print("1. 复制 .env.mongodb 到 .env")
        print("2. 根据需要修改配置")
        print("3. 安装Python依赖: pip install -r requirements.txt")
        print("4. 启动应用: uvicorn app.main:app --reload")
        
        # 显示连接信息
        print(f"\n🔗 数据库连接信息:")
        print(f"   数据库URL: mongodb://localhost:27017/3dmodel_db")
        print(f"   数据库名称: 3dmodel_db")
        print(f"   集合: tasks, feedback, evaluations")
    
    client.close()

if __name__ == "__main__":
    main()
