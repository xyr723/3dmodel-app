import { useEffect } from 'react';
import { useEvalStore } from '../store/evalStore';

export default function DashboardPage() {
	const { feedbacks, metrics, load } = useEvalStore();
	useEffect(() => { load(); }, []);

	const avgRating = feedbacks.length ? (feedbacks.reduce((s, f) => s + f.rating, 0) / feedbacks.length).toFixed(2) : '-';
	const successRate = metrics.length ? ((metrics.filter(m => m.isDownloadedRenderable).length / metrics.length) * 100).toFixed(0) + '%' : '-';

	return (
		<div style={{ maxWidth: 1000, margin: '0 auto', padding: 16 }}>
			<h2>Evaluation Dashboard</h2>
			<div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
				<div>Avg rating: <b>{avgRating}</b></div>
				<div>Renderable success: <b>{successRate}</b></div>
			</div>
			<div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
				<div>
					<h3>Feedback</h3>
					<ul>
						{feedbacks.map((f, i) => (
							<li key={i}>model {f.modelId.slice(0,8)} rating {f.rating}</li>
						))}
					</ul>
				</div>
				<div>
					<h3>Metrics</h3>
					<ul>
						{metrics.map((m, i) => (
							<li key={i}>model {m.modelId.slice(0,8)} load {m.loadTimeMs ?? '-'}ms</li>
						))}
					</ul>
				</div>
			</div>
		</div>
	);
} 