# 3D 模型生成网页（文本/图片 → 单体 3D 模型）

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
  # 模型提供商：本地联调可先用 local；如需真实调用 Meshy，需配置 MESHY_API_KEY
  MODEL_PROVIDER=local
  MESHY_API_KEY=
  MESHY_API_URL=https://api.meshy.ai
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

> 如需调用 Meshy，请将 `MODEL_PROVIDER` 改为 `meshy` 并设置有效的 `MESHY_API_KEY`；否则会报 `Missing API key`。

### 四、启动前端（Vite）

```bash
cd frontend
pnpm install
pnpm dev
```
打开浏览器访问 `http://localhost:5173/`。

### 五、使用方法
1. 在前端界面输入提示词（可选上传参考图片）。
2. 点击生成后，前端会调用后端 `/api/generate`，并轮询 `/api/generate/status/{task_id}` 获取状态。
3. 生成完成后可在页面内预览/下载模型。

### 六、常见问题（FAQ）
- Q: 前端报错 “Cannot read properties of undefined (reading 'digest')”？
  - A: 已修复 `hashString` 的兼容与回退；请刷新页面再试。
- Q: 前端 404 或 CORS 问题？
  - A: 确认后端运行在 8000 端口；检查 `backend/.env` 中 `ALLOWED_HOSTS` 与前端地址一致；前端 `.env` 的 `VITE_BACKEND_BASE_URL` 指向 `http://localhost:8000/api`。
- Q: 后端状态查询返回 `{"detail":"任务不存在"}`？
  - A: 已将 `ModelService` 与 `CacheService` 调整为单例依赖，确保任务跨请求可查询。若仍出现，请确认后端已热重载到最新代码并重新发起生成。
- Q: 后端调用外部 API 报 `Missing API key`？
  - A: 将 `MODEL_PROVIDER=local`（本地联调）或配置 `MESHY_API_KEY` 后再试。
- Q: 终端提示 `uvicorn: command not found`？
  - A: 使用 `python -m uvicorn app.main:app --reload`，确保在已激活的虚拟环境中运行。

---

## 项目结构（简）

- `frontend/`: React + TypeScript + Vite + Three.js 前端
- `backend/`: FastAPI 后端（生成、状态查询、下载、Sketchfab 集成）
- `docs+demo/`: 产品说明文档、demo视频

更多细节请查看 `frontend/README.md` 与 `backend/README.md`。
