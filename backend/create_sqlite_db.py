#!/usr/bin/env python3
"""
创建SQLite数据库的脚本
"""
import asyncio
import os
import sys
sys.path.append('.')

from app.db.database import init_db, Base, db_engine
from app.core.config import settings

async def create_sqlite_database():
    """创建SQLite数据库"""
    print("🗄️ 正在创建SQLite数据库...")
    
    # 设置SQLite数据库URL
    os.environ['DATABASE_URL'] = 'sqlite+aiosqlite:///./3dmodel.db'
    
    try:
        # 初始化数据库
        await init_db()
        
        print("✅ SQLite数据库创建成功!")
        print(f"📁 数据库文件位置: {os.path.abspath('./3dmodel.db')}")
        print("📋 已创建的表:")
        print("   - tasks (任务记录表)")
        print("   - feedback (用户反馈表)")  
        print("   - evaluations (模型评估表)")
        
    except Exception as e:
        print(f"❌ 数据库创建失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(create_sqlite_database())
