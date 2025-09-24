# Sketchfab API 集成文档

## 概述

本项目已成功集成Sketchfab API，为用户提供搜索和下载全球最大3D模型库的功能。用户现在可以：

- 🔍 **搜索模型**: 根据关键词、分类、许可证等条件搜索3D模型
- 📋 **获取详情**: 查看模型的详细信息、作者、许可证等
- ⬇️ **下载模型**: 下载可用的3D模型文件
- 🔥 **热门推荐**: 获取热门和官方推荐的模型
- 📂 **分类浏览**: 按分类浏览模型库

## 新增文件

### API路由
- `app/api/sketchfab.py` - Sketchfab API端点定义

### 服务层
- `app/services/sketchfab_service.py` - Sketchfab API调用服务

### 数据模型
- `app/models/request.py` - 新增Sketchfab请求模型
- `app/models/response.py` - 新增Sketchfab响应模型

### 测试文件
- `tests/test_sketchfab.py` - Sketchfab功能单元测试
- `test_sketchfab_standalone.py` - 独立测试脚本

### 示例代码
- `examples/sketchfab_example.py` - API使用示例

## API端点

### 搜索模型
```
GET  /api/sketchfab/search
POST /api/sketchfab/search
```

**参数:**
- `query`: 搜索关键词 (必需)
- `category`: 模型分类 (可选)
- `license`: 许可证类型 (默认: cc)
- `downloadable`: 是否可下载 (默认: true)
- `page`: 页码 (默认: 1)
- `per_page`: 每页数量 (默认: 20)
- `sort_by`: 排序方式 (relevance/likes/views/recent)
- `min_face_count`: 最小面数 (可选)
- `max_face_count`: 最大面数 (可选)
- `staff_picked`: 是否官方推荐 (可选)

**响应:**
```json
{
  "query": "car",
  "total_count": 1500,
  "page": 1,
  "per_page": 20,
  "total_pages": 75,
  "models": [
    {
      "uid": "abc123",
      "name": "Sports Car",
      "author": "3D Artist",
      "thumbnail_url": "https://...",
      "downloadable": true,
      "face_count": 5000,
      "license": "cc-by"
    }
  ],
  "search_time": 0.5,
  "searched_at": "2023-12-01T10:00:00Z"
}
```

### 获取模型详情
```
GET /api/sketchfab/model/{model_uid}
```

**响应:**
```json
{
  "uid": "abc123",
  "name": "Sports Car",
  "description": "A detailed sports car model...",
  "author": "3D Artist",
  "author_url": "https://sketchfab.com/artist",
  "face_count": 5000,
  "vertex_count": 2500,
  "animated": false,
  "rigged": false,
  "license": "cc-by",
  "license_label": "Creative Commons - Attribution",
  "view_count": 1000,
  "like_count": 50,
  "thumbnail_url": "https://...",
  "downloadable": true,
  "categories": ["Vehicles"],
  "tags": ["car", "sports", "vehicle"],
  "published_at": "2023-01-01T00:00:00Z"
}
```

### 下载模型
```
GET  /api/sketchfab/download/{model_uid}
POST /api/sketchfab/download
```

**参数:**
- `model_uid`: 模型唯一标识符 (必需)
- `format`: 下载格式 (默认: original)
- `user_id`: 用户ID (可选)

**响应:**
```json
{
  "model_uid": "abc123",
  "download_id": "dl_123456",
  "status": "success",
  "message": "下载链接生成成功",
  "download_url": "https://...",
  "file_format": "original",
  "model_name": "Sports Car",
  "author": "3D Artist",
  "license": "cc-by",
  "expires_at": "2023-12-02T10:00:00Z",
  "attribution_required": true,
  "commercial_use": true
}
```

### 获取热门模型
```
GET /api/sketchfab/popular
```

**参数:**
- `category`: 模型分类 (可选)
- `limit`: 返回数量 (默认: 20)

### 获取分类列表
```
GET /api/sketchfab/categories
```

**响应:**
```json
{
  "categories": [
    {
      "slug": "vehicles",
      "name": "Vehicles",
      "count": 1500
    }
  ],
  "count": 50
}
```

## 配置

### 环境变量
在 `.env` 文件中添加：

```bash
# Sketchfab API配置 (可选)
SKETCHFAB_API_TOKEN=your_sketchfab_api_token_here
```

**注意:** 
- API token是可选的，没有token时可以访问公开模型
- 有token时可以访问更多功能和更高的请求限制

### 获取API Token
1. 访问 [Sketchfab API页面](https://sketchfab.com/developers/api)
2. 注册账户并申请API访问权限
3. 获取API token并配置到环境变量中

## 功能特性

### 1. 智能缓存
- 搜索结果缓存1小时，避免重复请求
- 模型详情缓存1小时
- 分类列表缓存24小时

### 2. 速率限制
- 自动处理API速率限制
- 请求间隔控制
- 429错误自动重试

### 3. 错误处理
- 完善的异常处理机制
- 友好的错误消息
- 日志记录和监控

### 4. 数据验证
- 严格的请求参数验证
- 响应数据格式化
- 类型安全保证

## 使用示例

### Python客户端示例
```python
import asyncio
import aiohttp

async def search_models():
    url = "http://localhost:8000/api/sketchfab/search"
    headers = {"Authorization": "Bearer your-api-key"}
    params = {
        "query": "car",
        "category": "vehicles",
        "downloadable": True,
        "per_page": 10
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"找到 {data['total_count']} 个模型")
                for model in data['models']:
                    print(f"- {model['name']} by {model['author']}")
            else:
                print(f"请求失败: {response.status}")

# 运行示例
asyncio.run(search_models())
```

### cURL示例
```bash
# 搜索汽车模型
curl -X GET "http://localhost:8000/api/sketchfab/search?query=car&category=vehicles" \
     -H "Authorization: Bearer your-api-key"

# 获取模型详情
curl -X GET "http://localhost:8000/api/sketchfab/model/abc123" \
     -H "Authorization: Bearer your-api-key"

# 下载模型
curl -X GET "http://localhost:8000/api/sketchfab/download/abc123?format=original" \
     -H "Authorization: Bearer your-api-key"
```

## 测试

### 运行测试
```bash
# 运行所有Sketchfab相关测试
pytest tests/test_sketchfab.py -v

# 运行独立测试脚本
python test_sketchfab_standalone.py

# 运行示例代码
python examples/sketchfab_example.py
```

### 测试覆盖
- ✅ 数据模型验证
- ✅ API请求处理
- ✅ 错误处理
- ✅ 缓存机制
- ✅ 速率限制
- ✅ 数据解析

## 许可证和使用条款

### Sketchfab模型许可证
- **CC0**: 公共领域，无需署名，允许商用
- **CC BY**: 需要署名，允许商用
- **CC BY-SA**: 需要署名，允许商用，相同许可证分享
- **CC BY-NC**: 需要署名，不允许商用
- **CC BY-NC-SA**: 需要署名，不允许商用，相同许可证分享

### 使用注意事项
1. 下载前请检查模型的许可证类型
2. 商业使用时确保符合许可证要求
3. 需要署名时请正确标注作者信息
4. 遵守Sketchfab的服务条款

## 性能优化

### 缓存策略
- 搜索结果缓存减少重复请求
- 模型详情缓存提高访问速度
- 分类列表长期缓存

### 请求优化
- 异步HTTP请求
- 连接池复用
- 请求超时控制
- 自动重试机制

## 监控和日志

### 日志记录
- 搜索请求日志
- 下载请求日志
- 错误和异常日志
- 性能指标日志

### 监控指标
- API请求次数
- 响应时间
- 错误率
- 缓存命中率

## 故障排除

### 常见问题

1. **搜索无结果**
   - 检查搜索关键词
   - 尝试不同的分类
   - 确认网络连接

2. **下载失败**
   - 确认模型支持下载
   - 检查许可证限制
   - 验证API token

3. **请求限制**
   - 检查API token配置
   - 等待速率限制重置
   - 减少请求频率

4. **缓存问题**
   - 检查Redis连接
   - 清理过期缓存
   - 重启缓存服务

## 未来扩展

### 计划功能
- [ ] 模型收藏功能
- [ ] 用户上传历史
- [ ] 批量下载
- [ ] 模型预览集成
- [ ] 高级筛选选项

### API增强
- [ ] GraphQL支持
- [ ] Webhook通知
- [ ] 批量操作API
- [ ] 统计分析API

## 贡献指南

欢迎提交Issue和Pull Request来改进Sketchfab集成功能！

### 开发环境
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/test_sketchfab.py

# 代码格式化
black app/services/sketchfab_service.py app/api/sketchfab.py
```

---

**文档版本**: 1.0  
**最后更新**: 2024年12月  
**维护者**: 3D模型生成API团队
