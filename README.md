# 3D 模型浏览平台（基于 Sketchfab 模型库）

## 运行与联调指南（前后端）

### 一、环境要求
- Node.js 18+
- pnpm（推荐）或 npm/yarn
- Python 3.9+

### 二、环境变量配置

- 后端 `backend/.env`（已为本地预置，若不存在可新建）：
  ```env
  DEBUG=true
  HOST=0.0.0.0
  PORT=8000
  # 本地开发固定 API Key（与前端保持一致）
  API_KEY=dev_local_api_key_12345
  # 允许的前端站点（CORS）
  ALLOWED_HOSTS=["http://localhost:5173","http://127.0.0.1:5173","*"]
  # 模型提供商：支持 sketchfab 和 local 模式
  MODEL_PROVIDER=sketchfab
  # Sketchfab API Token（可选，无 token 时使用公开模型）
  SKETCHFAB_API_TOKEN=
  ```

- 前端 `frontend/.env`（已为本地预置，若不存在可新建）：
  ```env
  VITE_BACKEND_BASE_URL=http://localhost:8000/api
  VITE_BACKEND_API_KEY=dev_local_api_key_12345
  ```

### 三、启动后端（FastAPI）

在项目根目录执行以下命令（或逐条手动执行）。首次运行会创建并使用虚拟环境：
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
看到日志中出现 `Uvicorn running on http://0.0.0.0:8000` 即表示后端启动成功。

### 四、启动前端（Vite）

```bash
cd frontend
pnpm install
pnpm dev
```
打开浏览器访问 `http://localhost:5173/`。

### 五、使用方法

#### Sketchfab 模型浏览
1. 点击导航栏的 "Sketchfab" 标签页进入模型库。
2. 使用搜索框输入关键词搜索模型，或点击"浏览热门"查看推荐模型。
3. 通过分类、许可证、排序方式等条件筛选模型。
4. 点击模型卡片选择并预览 3D 模型。
5. 如模型支持下载，可点击"下载模型"按钮获取文件。


### 六、功能特性

- 🔍 **模型搜索**: 支持关键词搜索全球最大 3D 模型库
- 📂 **分类浏览**: 按车辆、建筑、角色等分类浏览
- 🏷️ **许可证筛选**: 支持 CC0、CC BY 等多种许可证类型
- ⬇️ **模型下载**: 下载支持的 3D 模型文件
- 👁️ **实时预览**: 使用 Three.js 进行 3D 模型预览
- 🔥 **热门推荐**: 浏览官方推荐和热门模型

### 七、常见问题（FAQ）
- Q: 前端报错 "Cannot read properties of undefined (reading 'digest')"？
  - A: 已修复 `hashString` 的兼容与回退；请刷新页面再试。
- Q: 前端 404 或 CORS 问题？
  - A: 确认后端运行在 8000 端口；检查 `backend/.env` 中 `ALLOWED_HOSTS` 与前端地址一致；前端 `.env` 的 `VITE_BACKEND_BASE_URL` 指向 `http://localhost:8000/api`。
- Q: Sketchfab 搜索无结果？
  - A: 检查网络连接，尝试不同关键词或分类筛选。
- Q: 模型无法下载？
  - A: 确认模型支持下载且符合许可证要求；部分模型需要 Sketchfab 账户权限。
- Q: 终端提示 `uvicorn: command not found`？
  - A: 使用 `python -m uvicorn app.main:app --reload`，确保在已激活的虚拟环境中运行。

---

## 项目结构（简）

- `frontend/`: React + TypeScript + Vite + Three.js 前端
  - Sketchfab 模型浏览器和预览器
  - 3D 模型渲染和交互
- `backend/`: FastAPI 后端
  - Sketchfab API 集成和代理
  - 模型搜索、详情、下载功能
- `docs+demo/`: 产品说明文档、demo视频

更多细节请查看：
- `frontend/README.md` 与 `frontend/SKETCHFAB_USAGE.md`
- `backend/README.md` 与 `backend/SKETCHFAB_INTEGRATION.md`