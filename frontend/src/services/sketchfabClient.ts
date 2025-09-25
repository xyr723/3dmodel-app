import { cacheGet, cacheSet, dedupe } from './cache';
import { hashString } from '../utils/hash';
import type { 
  SketchfabModel, 
  SketchfabSearchRequest, 
  SketchfabSearchResponse, 
  SketchfabDownloadRequest, 
  SketchfabDownloadResponse,
  SketchfabCategory 
} from '../types';

const API_BASE = import.meta.env.VITE_BACKEND_BASE_URL || 'http://localhost:8000/api';
const API_KEY = import.meta.env.VITE_BACKEND_API_KEY || '';

// 搜索 Sketchfab 模型
export async function searchSketchfabModels(request: SketchfabSearchRequest): Promise<SketchfabSearchResponse> {
  const cacheKey = `sketchfab:search:${await hashString(JSON.stringify(request))}`;
  
  const cached = await cacheGet<SketchfabSearchResponse>(cacheKey);
  if (cached) return cached;

  return dedupe(cacheKey, async () => {
    if (!API_KEY) {
      // Mock response for development
      return {
        query: request.query,
        total_count: 0,
        page: request.page || 1,
        per_page: request.per_page || 20,
        total_pages: 0,
        models: [],
        search_time: 0,
        filters_applied: {},
        searched_at: new Date().toISOString()
      };
    }

    const searchParams = new URLSearchParams();
    searchParams.append('query', request.query);
    if (request.category) searchParams.append('category', request.category);
    
    if (request.license) searchParams.append('license', request.license);
    if (request.animated !== undefined) searchParams.append('animated', request.animated.toString());
    if (request.rigged !== undefined) searchParams.append('rigged', request.rigged.toString());
    if (request.downloadable !== undefined) searchParams.append('downloadable', request.downloadable.toString());
    if (request.page) searchParams.append('page', request.page.toString());
    if (request.per_page) searchParams.append('per_page', request.per_page.toString());
    if (request.sort_by) searchParams.append('sort_by', request.sort_by);
    if (request.min_face_count) searchParams.append('min_face_count', request.min_face_count.toString());
    if (request.max_face_count) searchParams.append('max_face_count', request.max_face_count.toString());
    if (request.staff_picked !== undefined) searchParams.append('staff_picked', request.staff_picked.toString());

    const response = await fetch(`${API_BASE}/sketchfab/search?${searchParams.toString()}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
      },
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || 'Failed to search Sketchfab models');
    }

    const data = await response.json();
    await cacheSet(cacheKey, data, 1000 * 60 * 60); // Cache for 1 hour
    return data;
  });
}

// 获取 Sketchfab 模型详细信息
export async function getSketchfabModel(modelUid: string): Promise<SketchfabModel> {
  const cacheKey = `sketchfab:model:${modelUid}`;
  
  const cached = await cacheGet<SketchfabModel>(cacheKey);
  if (cached) return cached;

  return dedupe(cacheKey, async () => {
    if (!API_KEY) {
      // Mock response for development
      return {
        uid: modelUid,
        name: 'Mock Model',
        description: 'This is a mock model for development',
        author: 'Mock Author',
        author_url: 'https://sketchfab.com/mock',
        face_count: 1000,
        vertex_count: 500,
        animated: false,
        rigged: false,
        license: 'cc0',
        license_label: 'Creative Commons',
        view_count: 0,
        like_count: 0,
        comment_count: 0,
        thumbnail_url: 'https://via.placeholder.com/300x200',
        preview_url: 'https://via.placeholder.com/300x200',
        embed_url: 'https://sketchfab.com/embed/mock',
        downloadable: true,
        categories: ['mock'],
        tags: ['mock', 'test'],
        published_at: new Date().toISOString(),
        created_at: new Date().toISOString()
      };
    }

    const response = await fetch(`${API_BASE}/sketchfab/model/${encodeURIComponent(modelUid)}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
      },
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || 'Failed to get Sketchfab model');
    }

    const data = await response.json();
    await cacheSet(cacheKey, data, 1000 * 60 * 60 * 24); // Cache for 24 hours
    return data;
  });
}

// 下载 Sketchfab 模型
export async function downloadSketchfabModel(request: SketchfabDownloadRequest): Promise<SketchfabDownloadResponse> {
  if (!API_KEY) {
    // Mock response for development
    return {
      model_uid: request.model_uid,
      download_id: 'mock-download-' + Math.random().toString(36).slice(2),
      status: 'success',
      message: 'Mock download successful',
      download_url: 'https://example.com/mock-model.glb',
      file_format: 'glb',
      file_size: 1024000,
      model_name: 'Mock Model',
      author: 'Mock Author',
      license: 'cc0',
      requested_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      attribution_required: true,
      commercial_use: false
    };
  }

  const response = await fetch(`${API_BASE}/sketchfab/download`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(text || 'Failed to download Sketchfab model');
  }

  return await response.json();
}

// 获取热门模型
export async function getPopularSketchfabModels(category?: string, limit: number = 20): Promise<SketchfabModel[]> {
  const cacheKey = `sketchfab:popular:${category || 'all'}:${limit}`;
  
  const cached = await cacheGet<SketchfabModel[]>(cacheKey);
  if (cached) return cached;

  return dedupe(cacheKey, async () => {
    if (!API_KEY) {
      // Mock response for development
      return [];
    }

    const searchParams = new URLSearchParams();
    if (category) searchParams.append('category', category);
    searchParams.append('limit', limit.toString());
    
    

    const response = await fetch(`${API_BASE}/sketchfab/popular?${searchParams.toString()}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
      },
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || 'Failed to get popular Sketchfab models');
    }

    const data = await response.json();
    await cacheSet(cacheKey, data, 1000 * 60 * 60 * 6); // Cache for 6 hours
    return data;
  });
}

// 获取 Sketchfab 分类列表
export async function getSketchfabCategories(): Promise<SketchfabCategory[]> {
  const cacheKey = 'sketchfab:categories';
  
  const cached = await cacheGet<SketchfabCategory[]>(cacheKey);
  if (cached) return cached;

  return dedupe(cacheKey, async () => {
    if (!API_KEY) {
      // Mock response for development
      return [
        { id: '1', name: 'Characters', slug: 'characters' },
        { id: '2', name: 'Vehicles', slug: 'vehicles' },
        { id: '3', name: 'Architecture', slug: 'architecture' },
        { id: '4', name: 'Nature', slug: 'nature' },
        { id: '5', name: 'Furniture', slug: 'furniture' }
      ];
    }

    const response = await fetch(`${API_BASE}/sketchfab/categories`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
      },
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || 'Failed to get Sketchfab categories');
    }

    const data = await response.json();
    await cacheSet(cacheKey, data, 1000 * 60 * 60 * 24); // Cache for 24 hours
    return data;
  });
}

// �?Sketchfab 模型转换�?GeneratedModel 格式
export function sketchfabModelToGeneratedModel(model: SketchfabModel): {
  id: string;
  inputHash: string;
  createdAt: number;
  status: 'succeeded';
  glbUrl?: string;
  previewImageUrl?: string;
  provider: 'sketchfab';
  errorMessage?: string;
} {
  return {
    id: model.uid,
    inputHash: model.uid, // Use UID as hash for Sketchfab models
    createdAt: new Date(model.created_at).getTime(),
    status: 'succeeded',
    glbUrl: model.download_url,
    previewImageUrl: model.thumbnail_url,
    provider: 'sketchfab',
  };
}
