# Sketchfab 功能使用说明

## 概述

本项目已成功集成了 Sketchfab 3D 模型库功能，用户可以通过以下方式使用：

## 功能特性

### 1. Sketchfab 模型搜索和浏览
- **搜索功能**: 支持关键词搜索 Sketchfab 模型
- **分类筛选**: 按模型分类进行筛选
- **高级过滤**: 支持按动画、骨骼绑定、可下载性、官方推荐等条件筛选
- **排序选项**: 按相关性、点赞数、浏览数、最新时间排序
- **分页浏览**: 支持分页浏览搜索结果

### 2. 模型预览
- **3D 预览器**: 使用 Three.js 进行实时 3D 模型预览
- **模型详情**: 显示模型详细信息（作者、面数、许可证等）
- **标签和分类**: 展示模型标签和分类信息
- **下载链接**: 提供模型下载链接（如果可下载）

### 3. 集成到生成流程
- **提供商选择**: 在生成表单中可以选择 Sketchfab 作为提供商
- **统一接口**: Sketchfab 模型与 AI 生成模型使用相同的预览和评估系统

## 使用方法

### 1. 访问 Sketchfab 功能
在应用顶部导航栏点击 "Sketchfab" 标签页。

### 2. 搜索模型
1. 在搜索框中输入关键词
2. 选择分类（可选）
3. 设置排序方式
4. 应用过滤器（动画、骨骼、可下载等）
5. 点击"搜索"按钮

### 3. 浏览模型
- 在模型网格中浏览搜索结果
- 点击任意模型卡片查看详细信息
- 在右侧预览区域查看 3D 模型

### 4. 使用模型
- 点击模型卡片选择模型
- 在预览区域查看 3D 模型
- 如果模型可下载，可以点击"下载模型"按钮

### 5. 独立使用
1. 点击顶部导航的 "Sketchfab" 标签页
2. 页面默认加载完成，显示搜索界面
3. 点击"浏览热门"按钮查看热门模型，或输入关键词后点击"搜索"按钮
4. 使用搜索和过滤功能找到合适的模型
5. 点击模型卡片选择模型
6. 在右侧预览区域查看 3D 模型
7. 可以下载模型或进行评分

### 6. 重要特性
- **默认加载**: 页面加载时不发送任何 API 请求，只显示搜索界面
- **手动搜索**: 只有在点击搜索按钮后才会发送请求到后端
- **参数可选**: 所有搜索参数（分类、许可证等）都是可选的

## API 端点

后端需要实现以下 Sketchfab API 端点：

### 搜索模型
```
GET /api/sketchfab/search
```

### 获取模型详情
```
GET /api/sketchfab/model/{model_uid}
```

### 下载模型
```
POST /api/sketchfab/download
```

### 获取热门模型
```
GET /api/sketchfab/popular
```

### 获取分类列表
```
GET /api/sketchfab/categories
```

## 环境配置

确保后端配置了正确的 Sketchfab API 密钥：

```env
VITE_BACKEND_API_KEY=your_backend_api_key
VITE_BACKEND_BASE_URL=http://localhost:8000/api
```

## 开发模式

如果没有配置 API 密钥，应用会使用模拟数据进行开发测试。

## 文件结构

```
src/
├── components/
│   └── SketchfabBrowser.tsx    # Sketchfab 模型浏览器组件
├── pages/
│   ├── GeneratePage.tsx        # AI 生成页面
│   └── SketchfabPage.tsx       # Sketchfab 模型库页面
├── services/
│   └── sketchfabClient.ts      # Sketchfab API 客户端
└── types/
    └── index.ts                # 更新的类型定义
```

## 技术实现

- **前端框架**: React + TypeScript
- **3D 渲染**: Three.js
- **状态管理**: React Hooks
- **缓存机制**: IndexedDB + 内存缓存
- **API 客户端**: Fetch API with Bearer token 认证

## 注意事项

1. 确保后端正确实现了所有 Sketchfab API 端点
2. 模型下载需要用户有相应的 Sketchfab 账户权限
3. 某些模型可能有使用许可证限制
4. 建议在生产环境中配置适当的缓存策略
5. **许可证设置**: 应用默认使用 "cc0" 许可证，如果后端不支持此许可证，请检查后端 API 配置

## 许可证修复

- 修复了许可证验证错误，将默认许可证从 "cc" 改为 "cc0"
- 添加了完整的许可证选项支持
- 所有 API 请求现在都会发送有效的许可证参数
