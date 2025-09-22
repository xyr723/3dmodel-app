import { cacheGet, cacheSet, dedupe } from './cache';
import { hashString } from '../utils/hash';
import type { GenerationInput, GeneratedModel } from '../types';

const API_BASE = import.meta.env.VITE_MESHY_BASE_URL || 'https://api.meshy.ai';
const API_KEY = import.meta.env.VITE_MESHY_API_KEY || '';

async function createJob(input: GenerationInput): Promise<{ taskId: string }> {
	if (!API_KEY) {
		// mock path
		return { taskId: 'mock-' + Math.random().toString(36).slice(2) };
	}
	const resp = await fetch(`${API_BASE}/v2/text-to-3d`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${API_KEY}`,
		},
		body: JSON.stringify({ prompt: input.promptText, image: input.referenceImageDataUrl, style: input.style }),
	});
	if (!resp.ok) throw new Error('Failed to create job');
	return resp.json();
}

async function getJob(taskId: string): Promise<{ status: string; model_url?: string; preview_image?: string; error?: string }> {
	if (taskId.startsWith('mock-')) {
		// simulate success after short delay
		await new Promise((r) => setTimeout(r, 800));
		return { status: 'succeeded', model_url: 'https://example.com/mock.glb', preview_image: 'https://placehold.co/400x300' };
	}
	const resp = await fetch(`${API_BASE}/v2/text-to-3d/${taskId}`, {
		headers: { 'Authorization': `Bearer ${API_KEY}` },
	});
	if (!resp.ok) throw new Error('Failed to get job');
	return resp.json();
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
		while (status !== 'succeeded' && status !== 'failed' && Date.now() - start < 1000 * 60 * 2) {
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
			provider: API_KEY ? 'meshy' : 'mock',
			errorMessage: error,
		};
		await cacheSet(cacheKey, result, 1000 * 60 * 60 * 24 * 7);
		return result;
	});
} 