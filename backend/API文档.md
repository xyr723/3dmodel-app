# 3D模型应用后端API文档

## 概述

本文档描述了3D模型应用后端的所有API接口和返回数据结构。后端基于FastAPI框架构建，提供Sketchfab平台的3D模型搜索、浏览和下载功能。

## 认证

所有API接口都需要提供有效的API密钥进行认证。

**Header参数：**
```
X-API-Key: your_api_key_here
```

## API接口列表

### 1. 搜索3D模型

#### POST /sketchfab/search

**描述：** 搜索Sketchfab 3D模型（推荐使用）

**请求体：**
```json
{
  "query": "car",
  "category": "vehicles-transportation",
  "license": "cc0",
  "animated": true,
  "rigged": false,
  "downloadable": true,
  "page": 1,
  "per_page": 20,
  "sort_by": "relevance",
  "min_face_count": 1000,
  "max_face_count": 50000,
  "staff_picked": false
}
```

**请求参数说明：**
- `query` (必填): 搜索关键词，1-200字符
- `category` (可选): 模型分类
- `license` (可选): 许可证类型，默认"cc"
- `animated` (可选): 是否包含动画
- `rigged` (可选): 是否有骨骼绑定
- `downloadable` (可选): 是否可下载，默认true
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，1-100，默认20
- `sort_by` (可选): 排序方式（relevance, likes, views, recent），默认"relevance"
- `min_face_count` (可选): 最小面数
- `max_face_count` (可选): 最大面数
- `staff_picked` (可选): 是否为官方推荐

#### GET /sketchfab/search

**描述：** 搜索Sketchfab 3D模型（GET方式，便于测试）

**查询参数：**
- `query` (必填): 搜索关键词
- `category` (可选): 模型分类
- `license` (可选): 许可证类型，默认"cc0"
- `animated` (可选): 是否包含动画
- `rigged` (可选): 是否有骨骼绑定
- `downloadable` (可选): 是否可下载，默认"true"
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，1-100，默认20
- `sort_by` (可选): 排序方式，默认"relevance"
- `min_face_count` (可选): 最小面数
- `max_face_count` (可选): 最大面数
- `staff_picked` (可选): 是否为官方推荐

**响应数据结构：**
```json
{
  "query": "car",
  "total_count": 12450,
  "page": 1,
  "per_page": 20,
  "total_pages": 623,
  "models": [
    {
      "uid": "abc123def456",
      "name": "Sports Car Model",
      "description": "High-detail sports car 3D model",
      "author": "user123",
      "author_url": "https://sketchfab.com/user123",
      "face_count": 25000,
      "vertex_count": 12500,
      "animated": false,
      "rigged": false,
      "license": "CC0",
      "license_label": "Creative Commons - Public Domain",
      "view_count": 5420,
      "like_count": 89,
      "comment_count": 12,
      "thumbnail_url": "https://media.sketchfab.com/models/abc123/thumbnails/image.jpg",
      "preview_url": "https://media.sketchfab.com/models/abc123/preview.jpg",
      "embed_url": "https://sketchfab.com/models/abc123/embed",
      "downloadable": true,
      "download_url": "https://api.sketchfab.com/v3/models/abc123/download",
      "categories": ["vehicles-transportation", "cars"],
      "tags": ["car", "vehicle", "sports", "3d"],
      "published_at": "2023-10-15T14:30:00Z",
      "created_at": "2023-10-15T14:30:00Z"
    }
  ],
  "search_time": 0.45,
  "searched_at": "2024-01-15T10:30:00Z"
}
```

### 2. 获取模型详情

#### GET /sketchfab/model/{model_uid}

**描述：** 获取Sketchfab模型详细信息

**路径参数：**
- `model_uid`: 模型唯一标识符

**响应数据结构：**
```json
{
  "uid": "abc123def456",
  "name": "Sports Car Model",
  "description": "High-detail sports car 3D model with interior details",
  "author": "user123",
  "author_url": "https://sketchfab.com/user123",
  "face_count": 25000,
  "vertex_count": 12500,
  "animated": false,
  "rigged": false,
  "license": "CC0",
  "license_label": "Creative Commons - Public Domain",
  "view_count": 5420,
  "like_count": 89,
  "comment_count": 12,
  "thumbnail_url": "https://media.sketchfab.com/models/abc123/thumbnails/image.jpg",
  "preview_url": "https://media.sketchfab.com/models/abc123/preview.jpg",
  "embed_url": "https://sketchfab.com/models/abc123/embed",
  "downloadable": true,
  "download_url": "https://api.sketchfab.com/v3/models/abc123/download",
  "categories": ["vehicles-transportation", "cars"],
  "tags": ["car", "vehicle", "sports", "3d", "realistic"],
  "published_at": "2023-10-15T14:30:00Z",
  "created_at": "2023-10-15T14:30:00Z"
}
```

### 3. 下载3D模型

#### POST /sketchfab/download

**描述：** 下载Sketchfab 3D模型

**请求体：**
```json
{
  "model_uid": "abc123def456",
  "format": "original",
  "user_id": "user789"
}
```

**请求参数说明：**
- `model_uid` (必填): Sketchfab模型UID
- `format` (可选): 下载格式，默认"original"
- `user_id` (可选): 用户ID

#### GET /sketchfab/download/{model_uid}

**描述：** 下载Sketchfab 3D模型（GET方式）

**路径参数：**
- `model_uid`: 模型唯一标识符

**查询参数：**
- `format` (可选): 下载格式，默认"original"
- `user_id` (可选): 用户ID

**响应数据结构：**
```json
{
  "model_uid": "abc123def456",
  "download_id": "dl_789xyz",
  "status": "success",
  "message": "模型下载准备完成",
  "download_url": "https://models.sketchfab.com/download/abc123def456.zip",
  "file_format": "zip",
  "file_size": 15728640,
  "model_name": "Sports Car Model",
  "author": "user123",
  "license": "CC0",
  "requested_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-15T22:30:00Z",
  "attribution_required": false,
  "commercial_use": true
}
```

### 4. 获取热门模型

#### GET /sketchfab/popular

**描述：** 获取热门3D模型

**查询参数：**
- `category` (可选): 模型分类
- `limit` (可选): 返回数量，1-100，默认20

**响应数据结构：**
```json
[
  {
    "uid": "popular123",
    "name": "Popular Model 1",
    "description": "A very popular 3D model",
    "author": "top_creator",
    "author_url": "https://sketchfab.com/top_creator",
    "face_count": 30000,
    "vertex_count": 15000,
    "animated": true,
    "rigged": true,
    "license": "CC BY",
    "license_label": "Creative Commons - Attribution",
    "view_count": 25000,
    "like_count": 450,
    "comment_count": 78,
    "thumbnail_url": "https://media.sketchfab.com/models/popular123/thumbnails/image.jpg",
    "preview_url": "https://media.sketchfab.com/models/popular123/preview.jpg",
    "embed_url": "https://sketchfab.com/models/popular123/embed",
    "downloadable": true,
    "download_url": "https://api.sketchfab.com/v3/models/popular123/download",
    "categories": ["characters-creatures", "people"],
    "tags": ["character", "human", "rigged", "animated"],
    "published_at": "2023-09-20T09:15:00Z",
    "created_at": "2023-09-20T09:15:00Z"
  }
]
```

### 5. 获取分类列表

#### GET /sketchfab/categories

**描述：** 获取Sketchfab模型分类列表

**响应数据结构：**
```json
{
  "categories": [
    "animals-pets",
    "architecture",
    "art-abstract",
    "cars-vehicles",
    "characters-creatures",
    "cultural-heritage-history",
    "electronics-gadgets",
    "fashion-style",
    "food-drink",
    "furniture-home",
    "music",
    "nature-plants",
    "news-politics",
    "people",
    "places-travel",
    "science-technology",
    "sports-fitness",
    "weapons-military"
  ],
  "count": 18
}
```

## 数据模型详细说明

### SketchfabModel（模型对象）

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| uid | string | 是 | 模型唯一标识符 |
| name | string | 是 | 模型名称 |
| description | string | 否 | 模型描述 |
| author | string | 是 | 作者名称 |
| author_url | string | 否 | 作者链接 |
| face_count | integer | 否 | 面数 |
| vertex_count | integer | 否 | 顶点数 |
| animated | boolean | 是 | 是否有动画 |
| rigged | boolean | 是 | 是否有骨骼 |
| license | string | 否 | 许可证类型 |
| license_label | string | 否 | 许可证标签 |
| view_count | integer | 否 | 浏览次数 |
| like_count | integer | 否 | 点赞数 |
| comment_count | integer | 否 | 评论数 |
| thumbnail_url | string | 是 | 缩略图URL |
| preview_url | string | 否 | 预览图URL |
| embed_url | string | 否 | 嵌入链接 |
| downloadable | boolean | 是 | 是否可下载 |
| download_url | string | 否 | 下载链接 |
| categories | array[string] | 否 | 分类标签 |
| tags | array[string] | 否 | 标签 |
| published_at | datetime | 否 | 发布时间 |
| created_at | datetime | 否 | 创建时间 |

### SketchfabSearchResponse（搜索响应）

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| query | string | 是 | 搜索关键词 |
| total_count | integer | 是 | 总结果数 |
| page | integer | 是 | 当前页码 |
| per_page | integer | 是 | 每页数量 |
| total_pages | integer | 是 | 总页数 |
| models | array[SketchfabModel] | 是 | 模型列表 |
| search_time | float | 否 | 搜索耗时(秒) |
| searched_at | datetime | 是 | 搜索时间 |

### SketchfabDownloadResponse（下载响应）

| 字段名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| model_uid | string | 是 | 模型UID |
| download_id | string | 是 | 下载ID |
| status | string | 是 | 下载状态 |
| message | string | 是 | 响应消息 |
| download_url | string | 否 | 下载链接 |
| file_format | string | 否 | 文件格式 |
| file_size | integer | 否 | 文件大小(字节) |
| model_name | string | 否 | 模型名称 |
| author | string | 否 | 作者 |
| license | string | 否 | 许可证 |
| requested_at | datetime | 是 | 请求时间 |
| expires_at | datetime | 否 | 链接过期时间 |
| attribution_required | boolean | 是 | 是否需要署名 |
| commercial_use | boolean | 是 | 是否允许商用 |

## 错误响应

所有API在发生错误时会返回统一的错误格式：

```json
{
  "detail": "错误描述信息"
}
```

**常见HTTP状态码：**
- `200`: 请求成功
- `400`: 请求参数错误
- `401`: 认证失败（API密钥无效）
- `404`: 资源不存在
- `500`: 服务器内部错误

## 许可证类型说明

| 许可证代码 | 完整名称 | 商用 | 署名要求 |
|------------|----------|------|----------|
| cc0 | Public Domain | 是 | 否 |
| cc-by | Creative Commons - Attribution | 是 | 是 |
| cc-by-sa | Creative Commons - Attribution ShareAlike | 是 | 是 |
| cc-by-nc | Creative Commons - Attribution NonCommercial | 否 | 是 |
| cc-by-nc-sa | Creative Commons - Attribution NonCommercial ShareAlike | 否 | 是 |

## 使用示例

### JavaScript/前端调用示例

```javascript
// 搜索模型
const searchModels = async (query) => {
  const response = await fetch('/api/sketchfab/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your_api_key'
    },
    body: JSON.stringify({
      query: query,
      page: 1,
      per_page: 20,
      license: 'cc0'
    })
  });
  
  const data = await response.json();
  return data;
};

// 获取模型详情
const getModelDetails = async (modelUid) => {
  const response = await fetch(`/api/sketchfab/model/${modelUid}`, {
    headers: {
      'X-API-Key': 'your_api_key'
    }
  });
  
  const model = await response.json();
  return model;
};

// 下载模型
const downloadModel = async (modelUid) => {
  const response = await fetch(`/api/sketchfab/download/${modelUid}`, {
    headers: {
      'X-API-Key': 'your_api_key'
    }
  });
  
  const downloadInfo = await response.json();
  return downloadInfo;
};
```

### Python调用示例

```python
import requests

API_BASE = "http://localhost:8000/api"
API_KEY = "your_api_key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 搜索模型
def search_models(query):
    response = requests.post(
        f"{API_BASE}/sketchfab/search",
        headers=headers,
        json={
            "query": query,
            "page": 1,
            "per_page": 20,
            "license": "cc0"
        }
    )
    return response.json()

# 获取模型详情
def get_model_details(model_uid):
    response = requests.get(
        f"{API_BASE}/sketchfab/model/{model_uid}",
        headers=headers
    )
    return response.json()

# 下载模型
def download_model(model_uid):
    response = requests.get(
        f"{API_BASE}/sketchfab/download/{model_uid}",
        headers=headers
    )
    return response.json()
```

## 注意事项

1. **API密钥管理**: 请妥善保管您的API密钥，不要在客户端代码中暴露。
2. **请求频率限制**: 请合理控制请求频率，避免对服务器造成过大压力。
3. **许可证遵守**: 下载和使用3D模型时，请遵守相应的许可证要求。
4. **下载链接时效**: 下载链接通常有时效性，请及时使用。
5. **错误处理**: 请在客户端代码中实现适当的错误处理机制。

## 版本信息

- **API版本**: v1.0
- **文档版本**: 1.0.0
- **最后更新**: 2024年1月15日
