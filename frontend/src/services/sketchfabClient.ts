import { cacheGet, cacheSet, dedupe } from './cache';
import { hashString } from '../utils/hash';
import type { 
  SketchfabModel, 
  SketchfabSearchRequest, 
  SketchfabSearchResponse, 
  SketchfabDownloadRequest, 
  SketchfabDownloadResponse,
  SketchfabCategory,
  SketchfabCategoriesResponse 
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
      // Mock response for development with sample models
      const mockModels: SketchfabModel[] = [
        {
          uid: 'demo-car-123',
          name: '演示汽车模型',
          description: '这是一个演示用的汽车3D模型，展示了高质量的建模效果。',
          author: '演示作者',
          author_url: 'https://sketchfab.com/demo',
          face_count: 25000,
          vertex_count: 12500,
          animated: false,
          rigged: false,
          license: 'CC0',
          license_label: 'Creative Commons - Public Domain',
          view_count: 5420,
          like_count: 89,
          comment_count: 12,
          thumbnail_url: 'https://via.placeholder.com/400x300/4285f4/ffffff?text=Demo+Car',
          preview_url: 'https://via.placeholder.com/400x300/4285f4/ffffff?text=Demo+Car',
          embed_url: 'https://sketchfab.com/models/demo-car-123/embed',
          downloadable: true,
          download_url: '#',
          categories: ['cars-vehicles'],
          tags: ['car', 'vehicle', 'demo', '3d'],
          published_at: '2023-10-15T14:30:00Z',
          created_at: '2023-10-15T14:30:00Z'
        },
        {
          uid: 'demo-building-456',
          name: '演示建筑模型',
          description: '现代建筑设计的3D模型，适合建筑可视化项目。',
          author: '建筑师',
          author_url: 'https://sketchfab.com/architect',
          face_count: 45000,
          vertex_count: 22500,
          animated: false,
          rigged: false,
          license: 'CC BY',
          license_label: 'Creative Commons - Attribution',
          view_count: 3200,
          like_count: 67,
          comment_count: 8,
          thumbnail_url: 'https://via.placeholder.com/400x300/34a853/ffffff?text=Demo+Building',
          preview_url: 'https://via.placeholder.com/400x300/34a853/ffffff?text=Demo+Building',
          embed_url: 'https://sketchfab.com/models/demo-building-456/embed',
          downloadable: true,
          download_url: '#',
          categories: ['architecture'],
          tags: ['building', 'architecture', 'modern', 'demo'],
          published_at: '2023-09-20T09:15:00Z',
          created_at: '2023-09-20T09:15:00Z'
        }
      ];

      return {
        query: request.query,
        total_count: mockModels.length,
        page: request.page || 1,
        per_page: request.per_page || 20,
        total_pages: 1,
        models: mockModels.filter(model => 
          !request.query || 
          model.name.toLowerCase().includes(request.query.toLowerCase()) ||
          model.tags.some(tag => tag.toLowerCase().includes(request.query.toLowerCase()))
        ),
        search_time: 0.1,
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
      return [
        {
          uid: 'demo-popular-1',
          name: '热门演示模型',
          description: '这是一个热门的演示3D模型。',
          author: '热门作者',
          author_url: 'https://sketchfab.com/popular',
          face_count: 15000,
          vertex_count: 7500,
          animated: true,
          rigged: true,
          license: 'CC0',
          license_label: 'Creative Commons - Public Domain',
          view_count: 25000,
          like_count: 450,
          comment_count: 78,
          thumbnail_url: 'https://via.placeholder.com/400x300/ff6d01/ffffff?text=Popular+Demo',
          preview_url: 'https://via.placeholder.com/400x300/ff6d01/ffffff?text=Popular+Demo',
          embed_url: 'https://sketchfab.com/models/demo-popular-1/embed',
          downloadable: true,
          download_url: '#',
          categories: ['characters-creatures'],
          tags: ['character', 'popular', 'demo', 'animated'],
          published_at: '2023-08-10T12:00:00Z',
          created_at: '2023-08-10T12:00:00Z'
        }
      ];
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
        { id: '1', name: 'Animals & Pets', slug: 'animals-pets' },
        { id: '2', name: 'Architecture', slug: 'architecture' },
        { id: '3', name: 'Art & Abstract', slug: 'art-abstract' },
        { id: '4', name: 'Cars & Vehicles', slug: 'cars-vehicles' },
        { id: '5', name: 'Characters & Creatures', slug: 'characters-creatures' },
        { id: '6', name: 'Cultural Heritage & History', slug: 'cultural-heritage-history' },
        { id: '7', name: 'Electronics & Gadgets', slug: 'electronics-gadgets' },
        { id: '8', name: 'Fashion & Style', slug: 'fashion-style' },
        { id: '9', name: 'Food & Drink', slug: 'food-drink' },
        { id: '10', name: 'Furniture & Home', slug: 'furniture-home' },
        { id: '11', name: 'Music', slug: 'music' },
        { id: '12', name: 'Nature & Plants', slug: 'nature-plants' },
        { id: '13', name: 'News & Politics', slug: 'news-politics' },
        { id: '14', name: 'People', slug: 'people' },
        { id: '15', name: 'Places & Travel', slug: 'places-travel' },
        { id: '16', name: 'Science & Technology', slug: 'science-technology' },
        { id: '17', name: 'Sports & Fitness', slug: 'sports-fitness' },
        { id: '18', name: 'Weapons & Military', slug: 'weapons-military' }
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

    const data: SketchfabCategoriesResponse = await response.json();
    
    // 将后端返回的字符串数组转换为SketchfabCategory对象数组
    const categories: SketchfabCategory[] = data.categories.map((category, index) => ({
      id: (index + 1).toString(),
      name: category.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
      slug: category
    }));
    
    await cacheSet(cacheKey, categories, 1000 * 60 * 60 * 24); // Cache for 24 hours
    return categories;
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
