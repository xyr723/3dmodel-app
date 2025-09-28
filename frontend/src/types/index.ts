export type GenerationInput = {
  promptText?: string;
  referenceImageDataUrl?: string;
  style?: string;
  provider?: 'meshy' | 'sketchfab' | 'local';
};

export type GenerationStatus = 'queued' | 'processing' | 'succeeded' | 'failed';

export type GeneratedModel = {
  id: string;
  inputHash: string;
  createdAt: number;
  status: GenerationStatus;
  glbUrl?: string;
  previewImageUrl?: string;
  provider: 'meshy' | 'mock' | 'backend' | 'sketchfab';
  errorMessage?: string;
};

export type Feedback = {
  modelId: string;
  inputHash: string;
  rating: 1 | 2 | 3 | 4 | 5;
  notes?: string;
  timestamp: number;
};

export type EvaluationMetrics = {
  inputHash: string;
  modelId: string;
  isDownloadedRenderable: boolean;
  fileSizeBytes?: number;
  loadTimeMs?: number;
  triangleCountEstimate?: number;
};

export type CachedRecord = {
  key: string;
  value: unknown;
  storedAt: number;
  ttlMs?: number;
};

// Sketchfab API Types
export type SketchfabModel = {
  uid: string;
  name: string;
  description: string;
  author: string;
  author_url: string;
  face_count: number;
  vertex_count: number;
  animated: boolean;
  rigged: boolean;
  license: string;
  license_label: string;
  view_count: number;
  like_count: number;
  comment_count: number;
  thumbnail_url: string;
  preview_url: string;
  embed_url: string;
  downloadable: boolean;
  download_url?: string;
  categories: string[];
  tags: string[];
  published_at: string;
  created_at: string;
};

export type SketchfabLicense = 
  | 'cc0'
  | 'cc'
  | 'cc-by'
  | 'cc-by-sa'
  | 'cc-by-nc'
  | 'cc-by-nc-sa'
  | 'all_rights_reserved';

export type SketchfabSearchRequest = {
  query: string;
  category?: string;
  license?: SketchfabLicense;
  animated?: boolean;
  rigged?: boolean;
  downloadable?: boolean;
  page?: number;
  per_page?: number;
  sort_by?: 'relevance' | 'likes' | 'views' | 'recent';
  min_face_count?: number;
  max_face_count?: number;
  staff_picked?: boolean;
};

export type SketchfabSearchResponse = {
  query: string;
  total_count: number;
  page: number;
  per_page: number;
  total_pages: number;
  models: SketchfabModel[];
  search_time: number;
  searched_at: string;
};

export type SketchfabDownloadRequest = {
  model_uid: string;
  format?: string;
  user_id?: string;
};

export type SketchfabDownloadResponse = {
  model_uid: string;
  download_id: string;
  status: string;
  message: string;
  download_url?: string;
  file_format?: string;
  file_size?: number;
  model_name?: string;
  author?: string;
  license?: string;
  requested_at: string;
  expires_at?: string;
  attribution_required: boolean;
  commercial_use: boolean;
};

export type SketchfabCategory = {
  id: string;
  name: string;
  slug: string;
  parent?: string;
};

// Sketchfab 分类响应类型
export type SketchfabCategoriesResponse = {
  categories: string[];
  count: number;
}; 