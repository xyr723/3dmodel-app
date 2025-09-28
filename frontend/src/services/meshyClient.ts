import { cacheGet, cacheSet, dedupe } from './cache';
import { hashString } from '../utils/hash';
import type { GenerationInput, GeneratedModel } from '../types';

const API_BASE = import.meta.env.VITE_BACKEND_BASE_URL || 'http://localhost:8000/api';
const API_KEY = import.meta.env.VITE_BACKEND_API_KEY || '';

function mapStyleToBackend(style?: string): string | undefined {
	if (!style) return undefined;
	// backend expects enum values like "low_poly", "realistic", etc.
	return style.toLowerCase().replace(/-/g, '_');
}

function inferMode(input: GenerationInput): 'text_to_3d' | 'image_to_3d' {
	return input.referenceImageDataUrl ? 'image_to_3d' : 'text_to_3d';
}

function toAbsoluteUrlMaybe(pathOrUrl?: string): string | undefined {
	if (!pathOrUrl) return undefined;
	try {
		const u = new URL(pathOrUrl);
		return u.toString();
	} catch {
		// not a full URL, treat as relative to backend root (strip trailing /api)
		const backendRoot = API_BASE.replace(/\/?api\/?$/, '');
		if (pathOrUrl.startsWith('/')) return backendRoot + pathOrUrl;
		return `${backendRoot}/${pathOrUrl}`;
	}
}

function resolveProvider(input: GenerationInput): 'meshy' | 'local' | 'sketchfab' {
	const p = (input as any).provider as string | undefined;
	if (p && ['meshy','local','sketchfab'].includes(p.toLowerCase())) return p.toLowerCase() as any;
	// 简便：当 style 传 "sketchfab" 时，走 Sketchfab
	if ((input.style || '').toLowerCase() === 'sketchfab') return 'sketchfab';
	return 'meshy';
}

async function createJob(input: GenerationInput): Promise<{ taskId: string }> {
	if (!API_KEY) {
		// mock path if no backend key provided
		return { taskId: 'mock-' + Math.random().toString(36).slice(2) };
	}
	const body: any = {
		prompt: input.promptText || '',
		style: mapStyleToBackend(input.style) || 'realistic',
		mode: inferMode(input),
	};
	if (input.referenceImageDataUrl) {
		// backend expects image_url; we pass data URL when provided
		body.image_url = input.referenceImageDataUrl;
	}
	const provider = resolveProvider(input);
	const resp = await fetch(`${API_BASE}/generate?provider=${encodeURIComponent(provider)}` , {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${API_KEY}`,
		},
		body: JSON.stringify(body),
	});
	if (!resp.ok) {
		const text = await resp.text().catch(() => '');
		throw new Error(text || 'Failed to create job');
	}
	const data = await resp.json();
	const taskId = data.task_id || data.taskId || data.id;
	if (!taskId) throw new Error('Backend did not return task_id');
	return { taskId };
}

async function getJob(taskId: string): Promise<{ status: string; model_url?: string; preview_image?: string; error?: string; download_url?: string }> {
	if (!API_KEY) {
		// mock status
		return { status: 'succeeded', model_url: 'https://example.com/mock.glb', preview_image: 'https://example.com/mock.jpg' };
	}
	const resp = await fetch(`${API_BASE}/generate/status/${encodeURIComponent(taskId)}`, {
		headers: {
			'Authorization': `Bearer ${API_KEY}`,
		},
	});
	if (!resp.ok) {
		const text = await resp.text().catch(() => '');
		throw new Error(text || 'Failed to get job');
	}
	const j = await resp.json();
	// normalize fields from backend TaskStatusResponse/GenerateResponse
	const raw = ((j.status || j.task_status || '').toString()).toLowerCase();
	let status: 'queued' | 'processing' | 'succeeded' | 'failed' = 'processing';
	if (raw === 'completed' || raw === 'succeeded' || raw === 'success') status = 'succeeded';
	else if (raw === 'failed' || raw === 'error') status = 'failed';
	else if (raw === 'pending' || raw === 'queued') status = 'queued';
	else status = 'processing';
	let model_url = j.model_url || j.download_url || j.file_url;
	let preview_image = j.preview_url || j.preview_image || j.thumbnail_url;
	const error = j.error_details || j.error || (j.message && status === 'failed' ? j.message : undefined);
	model_url = toAbsoluteUrlMaybe(model_url);
	preview_image = toAbsoluteUrlMaybe(preview_image);
	return { status, model_url, preview_image, error, download_url: j.download_url };
}

export async function generateModel(input: GenerationInput): Promise<GeneratedModel> {
	const keySource = JSON.stringify(input);
	const inputHash = await hashString(keySource);
	const cacheKey = `model:${inputHash}`;

	const cached = await cacheGet<GeneratedModel>(cacheKey);
	if (cached) return cached;

	return dedupe(cacheKey, async () => {
		const { taskId } = await createJob(input);
		// poll
		let status = 'queued';
		let modelUrl: string | undefined;
		let preview: string | undefined;
		let error: string | undefined;
		const start = Date.now();
		while (status !== 'succeeded' && status !== 'failed' && Date.now() - start < 1000 * 60 * 5) {
			const j = await getJob(taskId);
			status = j.status;
			modelUrl = j.model_url;
			preview = j.preview_image;
			error = j.error;
			if (status === 'queued' || status === 'processing') {
				await new Promise((r) => setTimeout(r, 1500));
			}
		}
		const result: GeneratedModel = {
			id: taskId,
			inputHash,
			createdAt: Date.now(),
			status: (status as any) === 'succeeded' ? 'succeeded' : (status as any) === 'failed' ? 'failed' : 'failed',
			glbUrl: modelUrl,
			previewImageUrl: preview,
			provider: (resolveProvider(input) as any) || (API_KEY ? 'backend' : 'mock'),
			errorMessage: error,
		};
		await cacheSet(cacheKey, result, 1000 * 60 * 60 * 24 * 7);
		return result;
	});
} 