import { set, get, del } from 'idb-keyval';

const DEFAULT_TTL_MS = 1000 * 60 * 60 * 24; // 24h
const inflight = new Map<string, Promise<any>>();

export async function cacheGet<T>(key: string): Promise<T | undefined> {
	const record = (await get(key)) as { value: T; storedAt: number; ttlMs?: number } | undefined;
	if (!record) return undefined;
	const ttlMs = record.ttlMs ?? DEFAULT_TTL_MS;
	if (Date.now() - record.storedAt > ttlMs) {
		await del(key);
		return undefined;
	}
	return record.value;
}

export async function cacheSet<T>(key: string, value: T, ttlMs?: number): Promise<void> {
	await set(key, { value, storedAt: Date.now(), ttlMs });
}

export function dedupe<T>(key: string, fn: () => Promise<T>): Promise<T> {
	const existing = inflight.get(key) as Promise<T> | undefined;
	if (existing) return existing;
	const p = fn().finally(() => inflight.delete(key));
	inflight.set(key, p);
	return p;
} 