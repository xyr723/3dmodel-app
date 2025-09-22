import { create } from 'zustand';
import { cacheGet, cacheSet } from '../services/cache';
import type { Feedback, EvaluationMetrics } from '../types';

export type EvalState = {
	feedbacks: Feedback[];
	metrics: EvaluationMetrics[];
	addFeedback: (f: Feedback) => Promise<void>;
	addMetrics: (m: EvaluationMetrics) => Promise<void>;
	load: () => Promise<void>;
};

const FEEDBACK_KEY = 'eval:feedbacks';
const METRICS_KEY = 'eval:metrics';

export const useEvalStore = create<EvalState>((set, get) => ({
	feedbacks: [],
	metrics: [],
	addFeedback: async (f) => {
		const current = get().feedbacks;
		const next = [...current, f];
		set({ feedbacks: next });
		await cacheSet(FEEDBACK_KEY, next, 1000 * 60 * 60 * 24 * 365);
	},
	addMetrics: async (m) => {
		const current = get().metrics;
		const next = [...current, m];
		set({ metrics: next });
		await cacheSet(METRICS_KEY, next, 1000 * 60 * 60 * 24 * 365);
	},
	load: async () => {
		const f = (await cacheGet<Feedback[]>(FEEDBACK_KEY)) ?? [];
		const m = (await cacheGet<EvaluationMetrics[]>(METRICS_KEY)) ?? [];
		set({ feedbacks: f, metrics: m });
	},
})); 