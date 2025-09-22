import { useEffect, useState } from 'react';
import { GenerateForm } from '../components/GenerateForm';
import { ModelViewer } from '../components/ModelViewer';
import type { GeneratedModel, EvaluationMetrics, Feedback } from '../types';
import { useEvalStore } from '../store/evalStore';

export default function GeneratePage() {
	const [result, setResult] = useState<GeneratedModel | undefined>();
	const addMetrics = useEvalStore((s) => s.addMetrics);
	const addFeedback = useEvalStore((s) => s.addFeedback);
	const load = useEvalStore((s) => s.load);

	useEffect(() => { load(); }, []);

	const onMetrics = async (m: Partial<EvaluationMetrics>) => {
		if (!result) return;
		await addMetrics({
			inputHash: result.inputHash,
			modelId: result.id,
			isDownloadedRenderable: !!m.isDownloadedRenderable,
			fileSizeBytes: m.fileSizeBytes,
			loadTimeMs: m.loadTimeMs,
			triangleCountEstimate: m.triangleCountEstimate,
		});
	};

	const onRate = async (rating: 1 | 2 | 3 | 4 | 5) => {
		if (!result) return;
		const fb: Feedback = {
			modelId: result.id,
			inputHash: result.inputHash,
			rating,
			timestamp: Date.now(),
		};
		await addFeedback(fb);
		alert('Thanks for your feedback!');
	};

	return (
		<div style={{ maxWidth: 1000, margin: '0 auto', padding: 16 }}>
			<h2>Generate 3D Model</h2>
			<GenerateForm onResult={setResult} />
			<div style={{ height: 16 }} />
			<ModelViewer url={result?.glbUrl} onMetrics={onMetrics} />
			{result && (
				<div style={{ marginTop: 12, display: 'flex', gap: 8, alignItems: 'center' }}>
					<span>Rate quality:</span>
					{[1,2,3,4,5].map((r) => (
						<button key={r} onClick={() => onRate(r as any)}>{r}</button>
					))}
				</div>
			)}
		</div>
	);
} 