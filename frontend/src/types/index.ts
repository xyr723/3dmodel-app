export type GenerationInput = {
  promptText?: string;
  referenceImageDataUrl?: string;
  style?: string;
};

export type GenerationStatus = 'queued' | 'processing' | 'succeeded' | 'failed';

export type GeneratedModel = {
  id: string;
  inputHash: string;
  createdAt: number;
  status: GenerationStatus;
  glbUrl?: string;
  previewImageUrl?: string;
  provider: 'meshy' | 'mock' | 'backend';
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