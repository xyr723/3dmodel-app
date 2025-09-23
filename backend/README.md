# 3D模型生成API后端

基于FastAPI的3D模型生成和评估服务后端。

## 功能特性

- 🎨 **多种生成模式**: 支持文本转3D、图片转3D、草图转3D
- 🎯 **多样化风格**: 写实、卡通、低面数、抽象、建筑等风格
- 🚀 **高性能**: 异步处理，支持并发请求
- 💾 **智能缓存**: Redis缓存，避免重复生成
- 📊 **质量评估**: 自动评估模型质量
- 💬 **用户反馈**: 收集和分析用户反馈
- 🔒 **安全认证**: API密钥和JWT认证
- 📁 **多种存储**: 本地存储、AWS S3、Google Cloud Storage
- 🗄️ **灵活数据库**: 支持SQLite、PostgreSQL、MongoDB

## 技术栈

- **Web框架**: FastAPI + Uvicorn
- **数据库**: SQLAlchemy (SQL) / Motor (MongoDB)
- **缓存**: Redis
- **存储**: 本地文件系统 / AWS S3 / Google Cloud Storage
- **3D API**: Meshy AI / 本地模型
- **测试**: Pytest
- **部署**: Docker

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env` 文件并修改配置：

```bash
cp .env.example .env
```

主要配置项：
- `MESHY_API_KEY`: Meshy AI API密钥
- `DATABASE_URL`: 数据库连接URL
- `REDIS_URL`: Redis连接URL
- `STORAGE_TYPE`: 存储类型 (local/s3/gcs)

### 3. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口

### 生成3D模型

```bash
POST /api/generate
Content-Type: application/json
Authorization: Bearer your_api_key

{
  "prompt": "一只可爱的小猫",
  "style": "realistic",
  "mode": "text_to_3d",
  "quality": "medium",
  "output_format": "obj"
}
```

### 查询生成状态

```bash
GET /api/generate/status/{task_id}
Authorization: Bearer your_api_key
```

### 下载模型文件

```bash
GET /api/generate/download/{task_id}?format=obj
Authorization: Bearer your_api_key
```

### 提交用户反馈

```bash
POST /api/feedback
Content-Type: application/json
Authorization: Bearer your_api_key

{
  "task_id": "task_123",
  "rating": 4,
  "comment": "模型质量很好"
}
```

## 目录结构

```
backend/
├── app/
│   ├── main.py               # FastAPI应用入口
│   ├── api/                  # API路由
│   │   ├── generate.py       # 3D生成接口
│   │   └── evaluate.py       # 评估反馈接口
│   ├── core/                 # 核心配置
│   │   ├── config.py         # 应用配置
│   │   └── security.py       # 安全认证
│   ├── services/             # 业务服务
│   │   ├── model_service.py  # 模型生成服务
│   │   ├── cache_service.py  # 缓存服务
│   │   └── storage_service.py# 存储服务
│   ├── models/               # 数据模型
│   │   ├── request.py        # 请求模型
│   │   └── response.py       # 响应模型
│   ├── db/                   # 数据库
│   │   ├── database.py       # 数据库连接
│   │   └── feedback.py       # 反馈数据操作
│   └── utils/                # 工具函数
│       ├── logger.py         # 日志工具
│       └── file_utils.py     # 文件工具
├── tests/                    # 测试文件
├── requirements.txt          # 生产依赖
├── requirements-dev.txt      # 开发依赖
├── Dockerfile               # Docker配置
└── .env                     # 环境变量
```

## 开发指南

### 运行测试

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app tests/

# 运行特定测试文件
pytest tests/test_generate.py
```

### 代码格式化

```bash
# 格式化代码
black app/ tests/
isort app/ tests/

# 检查代码质量
flake8 app/ tests/
mypy app/
```

### Docker部署

```bash
# 构建镜像
docker build -t 3dmodel-api .

# 运行容器
docker run -d \
  --name 3dmodel-api \
  -p 8000:8000 \
  -e MESHY_API_KEY=your_api_key \
  3dmodel-api
```

### 使用Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/3dmodel
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: 3dmodel
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 配置说明

### 数据库配置

支持多种数据库：

```bash
# SQLite (开发)
DATABASE_URL=sqlite+aiosqlite:///./app.db

# PostgreSQL (推荐生产环境)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/3dmodel

# MongoDB
MONGODB_URL=mongodb://localhost:27017/3dmodel
```

### 存储配置

支持多种存储方式：

```bash
# 本地存储
STORAGE_TYPE=local
STORAGE_PATH=./storage

# AWS S3
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_BUCKET_NAME=your_bucket

# Google Cloud Storage
STORAGE_TYPE=gcs
AWS_BUCKET_NAME=your_gcs_bucket  # 复用配置
```

## 监控和日志

### 日志配置

```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/app.log
```

### 健康检查

```bash
GET /health
```

返回服务状态、数据库连接状态、缓存状态等信息。

## 性能优化

1. **缓存策略**: 使用Redis缓存相同参数的生成结果
2. **异步处理**: 所有I/O操作使用异步处理
3. **连接池**: 数据库和Redis使用连接池
4. **文件压缩**: 大文件自动压缩存储
5. **CDN集成**: 支持CDN加速文件下载

## 安全考虑

1. **API密钥认证**: 所有接口需要有效的API密钥
2. **请求限流**: 防止API滥用
3. **输入验证**: 严格的参数验证
4. **文件安全**: 安全的文件路径处理
5. **错误处理**: 不泄露敏感信息

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库URL配置
   - 确认数据库服务运行状态

2. **Redis连接失败**
   - 检查Redis URL配置
   - 确认Redis服务运行状态

3. **Meshy API调用失败**
   - 检查API密钥是否有效
   - 确认网络连接正常

4. **文件存储失败**
   - 检查存储路径权限
   - 确认云存储凭据配置

### 日志分析

查看日志文件定位问题：

```bash
tail -f logs/app.log
tail -f logs/error.log
```
## apikey meshy
- tizzy
- msy_vilZa7D2cNNchyRwOQ6XcEcopA3L5q0oB8AR

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如有问题或建议，请提交 Issue 或联系开发团队。
