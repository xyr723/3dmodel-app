# 3D 模型生成网页（文本/图片 → 单体 3D 模型）

## 1. 面向用户与痛点、用户故事

- **独立/小型游戏美术**: 需要快速产出占位或风格统一的单体模型（例如马、椅子、宝箱）。痛点是预算与时间有限、迭代快。
- **3D 原型设计师/产品设计**: 用于快速可视化概念。痛点是工具学习成本高、传统建模流程慢。
- **教育/创客**: 希望把文字或一张参考图变成可预览、可下载的 3D。痛点是缺工具、文件兼容问题。

用户故事：
- 作为美术，我输入“低多边形马”，几分钟内得到可预览的 GLB，并能下载复用。
- 作为设计师，我上传参考图并输入补充描述，得到接近风格的单体模型用于评审。
- 作为学生，我可以评价生成效果，帮助系统持续改进推荐参数与提示词。

## 2. 功能列表与优先级

- **高**: 文本/图片生成单体 3D 模型；生成进度轮询；3D 预览（gltf/glb）；基本下载；基础缓存与请求去重；用户评分反馈；本地指标记录（可渲染率、加载时长）。
- **中**: 历史记录列表；输入模板与风格预设；简单后处理（重新缩放、简化）。
- **低**: 账号体系与云端同步；团队协作与共享；多提供商路由与成本仪表盘。

本次开发交付：高优先级功能全部实现；中/低优先级留作后续。

## 3. 第三方 API 选择与对比

对比对象：
- **Meshy**: 成熟的 Text/Image→3D API，支持 glTF/GLB 输出，质量稳定，开发文档与商业化清晰。
- **Tripo AI / Luma**: 亦提供 3D 生成，部分在重建和纹理质量上有优势，但定价、队列与 SDK 完整度差异化较大。
- **开源管线(如 OpenLRM + 重建)**: 成本低但集成复杂、算力与维护成本高，不适合首版上线。

选择：**Meshy**。
- 原因：API 简单、文档完善、输出格式直接可用、质量稳定；后续可平滑扩展为多提供商策略。

## 4. 评估指标与评估系统设计

关键指标（KPI）：
- **可渲染率**: 模型能否在浏览器中成功加载与显示。
- **加载时长**: 首次可见的时间（ms）。
- **主观评分**: 用户 1-5 分主观质量打分。
- 次级指标：文件大小、三角面数（估计/解析）。

评估系统：
- 前端在加载模型时自动记录“可渲染率/加载时长/大小等”并与用户评分一起保存到本地（IndexedDB）。
- 仪表盘展示平均评分、可渲染成功率、加载时长分布等，辅助调参与提示词模板改进。
- 后续可加后端存储与 A/B 测试：不同提示词模板、风格参数的转化差异。

## 5. 降低第三方 API 调用次数的策略

备选思路：
- **输入去重（强烈推荐）**: 对输入（文本+图+参数）做哈希，命中则直接返回缓存。
- **结果缓存（本地/边缘）**: 成功结果保存一段时间，避免重复调用。
- **请求合并与在途去重**: 相同输入的并发请求合并为一次。
- **参数与提示词模板化**: 通过模板减少无效“试错”请求。
- **Mock/本地占位**: 开发与回归阶段使用 mock，避免真实计费。

本次落地：已实现“输入去重 + 结果缓存 + 在途请求去重 + Mock 开发模式”。

---

## 前端项目结构（已更新）

```
frontend/
  src/
    pages/
      GeneratePage.tsx         # 生成页：输入表单 + 3D 预览 + 评分
      DashboardPage.tsx        # 评估仪表盘：反馈与指标
    components/
      GenerateForm.tsx         # 文本/图片输入
      ModelViewer.tsx          # three.js 预览与加载指标（支持 glb/gltf/obj/stl）
    threejs/
      scene.ts                 # 场景初始化（相机、渲染器、光照、resize）
      loaders.ts               # 统一加载器：GLTF/OBJ/STL
      controls.ts              # 轨道控制封装
    hooks/
      useAnimationFrame.ts     # 动画循环 hook（可选）
    services/
      meshyClient.ts           # Meshy 客户端 + 轮询 + mock
      cache.ts                 # IndexedDB 缓存 + 在途去重
    store/
      evalStore.ts             # 反馈与指标的本地存储（Zustand）
    utils/
      hash.ts                  # 输入哈希（SHA-256）
    types/
      index.ts                 # 共享类型
  README.md                    # 前端使用说明
```

## 后端项目结构（已更新）

```
backend/
├── app/
│   ├── main.py               # 程序入口 (FastAPI 实例)
│   ├── api/                  # 路由层
│   │   ├── __init__.py
│   │   ├── generate.py       # /generate 接口：调用第三方3D API 或本地模型
│   │   └── evaluate.py       # /evaluate 接口：用户反馈
│   ├── core/                 # 核心配置
│   │   ├── config.py         # 配置（API key、模型参数）
│   │   └── security.py       # API Key 校验、鉴权
│   ├── services/             # 业务逻辑
│   │   ├── model_service.py  # 调用第三方3D生成API 或 本地AI模型
│   │   ├── cache_service.py  # 缓存逻辑（Redis）
│   │   └── storage_service.py# 模型文件存储（本地/云端）
│   ├── models/               # 数据模型
│   │   ├── request.py        # Pydantic 请求模型
│   │   └── response.py       # Pydantic 响应模型
│   ├── utils/                # 工具函数
│   │   ├── logger.py         # 日志
│   │   └── file_utils.py     # 文件相关处理
│   └── db/                   # 数据层
│       ├── database.py       # 数据库连接（MongoDB / Postgres）
│       └── feedback.py       # 用户反馈表
│
├── tests/                    # 单元测试
│   ├── test_generate.py
│   └── test_evaluate.py
│
├── requirements.txt          # Python依赖
├── requirements-dev.txt      # 开发依赖（pytest, black, mypy）
├── Dockerfile                # 容器化部署
├── .env                      # 环境变量（API key、DB连接）
└── README.md
```

## 运行方式

- 前端开发：
  - 进入 `frontend`
  - 安装依赖并启动：`pnpm i && pnpm dev`
  - 可选：`.env` 配置 `VITE_MESHY_API_KEY` 与 `VITE_MESHY_BASE_URL`
  - 未配置 key 时走 mock，便于开发调试

---

## 后续迭代建议
- 支持下载 GLB/GLTF 与压缩 Draco。
- 增加历史列表与模型管理。
- 接入后端存储与在线实验平台，做多提供商与 A/B。
- 更丰富的自动指标（真实三角数、纹理分辨率校验、面向目标引擎兼容性）。
