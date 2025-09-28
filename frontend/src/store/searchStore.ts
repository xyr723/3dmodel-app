import { create } from 'zustand';
import { cacheGet, cacheSet } from '../services/cache';
import type { SketchfabSearchRecord } from '../types';

export type SearchState = {
	searchRecords: SketchfabSearchRecord[];
	addSearchRecord: (record: SketchfabSearchRecord) => Promise<void>;
	load: () => Promise<void>;
	clearHistory: () => Promise<void>;
};

const SEARCH_RECORDS_KEY = 'sketchfab:search_records';

export const useSearchStore = create<SearchState>((set, get) => ({
	searchRecords: [],
	addSearchRecord: async (record) => {
		const current = get().searchRecords;
		const next = [record, ...current].slice(0, 100); // 只保留最近100条记录
		set({ searchRecords: next });
		await cacheSet(SEARCH_RECORDS_KEY, next, 1000 * 60 * 60 * 24 * 365); // 保存1年
	},
	load: async () => {
		const records = (await cacheGet<SketchfabSearchRecord[]>(SEARCH_RECORDS_KEY)) ?? [];
		set({ searchRecords: records });
	},
	clearHistory: async () => {
		set({ searchRecords: [] });
		await cacheSet(SEARCH_RECORDS_KEY, [], 1000 * 60 * 60 * 24 * 365);
	},
}));
