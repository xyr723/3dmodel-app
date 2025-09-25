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
		alert('感谢您的反馈！');
	};


	return (
		<div style={{ 
			width: '100%', 
			minHeight: '100vh',
			background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
			padding: '20px',
			boxSizing: 'border-box'
		}} className="sm:p-12">
			<div className="container" style={{ 
				margin: '0 auto',
				display: 'flex',
				flexDirection: 'column',
				gap: '24px'
			}}>
				{/* 页面标题区域 */}
				<div className="surface">
					<h1 className="h1 sm:text-24">
						生成 3D 模型
					</h1>
					<p style={{ 
						marginTop: '12px', 
						marginBottom: 0,
						color: '#6b7280',
						fontSize: '16px',
						lineHeight: '1.5'
					}}>
						左侧为生成设置，右侧为大预览区
					</p>
				</div>

				{/* 主要内容区域 */}
				<div className="grid grid-aside-main gap-24 sm:grid-1">
					{/* 左侧设置面板 */}
					<div className="panel sticky-20">
						<h3 className="h3">生成设置</h3>
						<GenerateForm onResult={setResult} />
					</div>

					{/* 右侧预览区域 */}
					<div className="panel">
						<h3 className="h3">模型预览</h3>
						<div className="preview">
							<ModelViewer url={result?.glbUrl} onMetrics={onMetrics} />
						</div>
						{result && (
							<div style={{ 
								marginTop: '24px', 
								display: 'flex', 
								gap: '12px', 
								alignItems: 'center', 
								flexWrap: 'wrap',
								padding: '16px',
								background: '#f8fafc',
								borderRadius: '8px'
							}}>
								<span style={{ 
									color: '#4b5563', 
									fontWeight: '500',
									fontSize: '16px'
								}}>
									为该模型打分：
								</span>
								<div style={{ display: 'flex', gap: '8px' }}>
									{[1,2,3,4,5].map((r) => (
										<button 
											key={r} 
											onClick={() => onRate(r as any)} 
											style={{
												width: '40px',
												height: '40px',
												borderRadius: '8px',
												border: 'none',
												background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
												color: 'white',
												fontWeight: '600',
												fontSize: '16px',
												cursor: 'pointer',
												transition: 'all 0.2s ease',
												boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
											}}
											onMouseOver={(e) => {
												e.currentTarget.style.transform = 'scale(1.1)';
												e.currentTarget.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.15)';
											}}
											onMouseOut={(e) => {
												e.currentTarget.style.transform = 'scale(1)';
												e.currentTarget.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
											}}
										>
											{r}
										</button>
									))}
								</div>
							</div>
						)}
					</div>
				</div>
			</div>

			{/* 移除内联媒体查询 */}
		</div>
	);
}