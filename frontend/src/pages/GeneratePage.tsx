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
		}}>
			<div style={{ 
				maxWidth: '1200px', 
				margin: '0 auto',
				display: 'flex',
				flexDirection: 'column',
				gap: '24px'
			}}>
				{/* 页面标题区域 */}
				<div style={{ 
					background: 'rgba(255, 255, 255, 0.9)', 
					borderRadius: '12px',
					padding: '24px',
					boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
					backdropFilter: 'blur(10px)'
				}}>
					<h1 style={{ 
						margin: 0, 
						fontSize: '32px', 
						lineHeight: '1.2',
						background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
						WebkitBackgroundClip: 'text',
						WebkitTextFillColor: 'transparent',
						fontWeight: '700'
					}}>
						生成 3D 模型
					</h1>
					<p style={{ 
						marginTop: '12px', 
						marginBottom: 0,
						color: '#6b7280',
						fontSize: '16px',
						lineHeight: '1.5'
					}}>
						左侧为生成设置（随滚动粘性固定），右侧为大预览区
					</p>
				</div>

				{/* 主要内容区域 */}
				<div style={{ 
					display: 'grid', 
					gridTemplateColumns: 'minmax(300px, 400px) minmax(0, 1fr)',
					gap: '24px',
					alignItems: 'flex-start'
				}}>
					{/* 左侧设置面板 */}
					<div style={{ 
						position: 'sticky',
						top: '20px',
						background: 'rgba(255, 255, 255, 0.95)',
						borderRadius: '12px',
						padding: '24px',
						boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
						backdropFilter: 'blur(10px)',
						border: '1px solid rgba(255, 255, 255, 0.2)'
					}}>
						<h3 style={{ 
							margin: 0, 
							fontSize: '20px', 
							marginBottom: '20px', 
							color: '#1f2937',
							fontWeight: '600'
						}}>
							生成设置
						</h3>
						<GenerateForm onResult={setResult} />
					</div>

					{/* 右侧预览区域 */}
					<div style={{ 
						background: 'rgba(255, 255, 255, 0.95)',
						borderRadius: '12px',
						padding: '24px',
						boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
						backdropFilter: 'blur(10px)',
						border: '1px solid rgba(255, 255, 255, 0.2)',
						overflow: 'hidden'
					}}>
						<h3 style={{ 
							margin: 0, 
							fontSize: '20px', 
							marginBottom: '20px', 
							color: '#1f2937',
							fontWeight: '600'
						}}>
							模型预览
						</h3>
						<div style={{ 
							borderRadius: '8px', 
							overflow: 'hidden',
							boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
							minHeight: '400px',
							background: '#f8fafc'
						}}>
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

			{/* 响应式媒体查询 */}
			<style>{`
				@media (max-width: 1024px) {
					div > div > div {
						grid-template-columns: 1fr;
					}
					
					.sticky {
						position: relative !important;
						top: 0 !important;
						margin-bottom: 20px;
					}
				}
				
				@media (max-width: 768px) {
					div[style*="padding: 20px"] {
						padding: 12px;
					}
					
					h1 {
						font-size: 24px !important;
					}
				}
			`}</style>
		</div>
	);
}