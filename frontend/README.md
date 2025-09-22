# Frontend

## Structure

- `src/pages/GeneratePage.tsx`: Text/Image-to-3D generation page
- `src/pages/DashboardPage.tsx`: Evaluation dashboard (feedback + metrics)
- `src/components/GenerateForm.tsx`: Input form for prompts and reference image
- `src/components/ModelViewer.tsx`: Three.js GLTF/GLB/OBJ/STL preview with load metrics
- `src/threejs/`: 3D 封装（`scene.ts`, `loaders.ts`, `controls.ts`，统一加载 `glb/gltf/obj/stl`）
- `src/hooks/`: 通用 hooks（`useAnimationFrame` 等）
- `src/services/meshyClient.ts`: Meshy API client with mock fallback
- `src/services/cache.ts`: IndexedDB cache + in-flight deduplication
- `src/store/evalStore.ts`: Zustand store for feedback and metrics
- `src/utils/hash.ts`: SHA-256 hashing utility
- `src/types/`: Shared TypeScript types

## Development

1. Install deps

```bash
pnpm i
pnpm dev
```

2. Optional: configure environment

Create `.env` in `frontend` with:

```
VITE_MESHY_API_KEY=your_key
VITE_MESHY_BASE_URL=https://api.meshy.ai
```

Without a key, the app uses a mock generator for local development.
