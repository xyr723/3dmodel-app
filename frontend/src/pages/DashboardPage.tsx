import { useEffect } from 'react';
import { useEvalStore } from '../store/evalStore';

export default function DashboardPage() {
	const { feedbacks, metrics, load } = useEvalStore();
	useEffect(() => { load(); }, []);

	const avgRating = feedbacks.length ? (feedbacks.reduce((s, f) => s + f.rating, 0) / feedbacks.length).toFixed(2) : '-';
	const successRate = metrics.length ? ((metrics.filter(m => m.isDownloadedRenderable).length / metrics.length) * 100).toFixed(0) + '%' : '-';

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
				{/* 标题区，与 GeneratePage 保持一致 */}
				<div style={{ 
					background: 'rgba(255, 255, 255, 0.9)', 
					borderRadius: '12px',
					padding: '24px',
					boxShadow: '0 4px 6px rgba(0, 0, 0, 0.05)',
					backdropFilter: 'blur(10px)'
				}}>
					<h2 style={{ 
						margin: 0, 
						fontSize: 28, 
						lineHeight: '32px',
						background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
						WebkitBackgroundClip: 'text',
						WebkitTextFillColor: 'transparent',
						fontWeight: 700
					}}>
						评测面板
					</h2>
					<p style={{ marginTop: 12, marginBottom: 0, color: '#6b7280', fontSize: 16, lineHeight: 1.5 }}>
						查看 3D 模型生成与渲染的质量与性能数据
					</p>
				</div>

				{/* KPI 区域 */}
				<div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 24 }}>
					<div style={{ 
						background: 'rgba(255, 255, 255, 0.95)',
						borderRadius: '12px',
						padding: '24px',
						boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
						backdropFilter: 'blur(10px)',
						border: '1px solid rgba(255, 255, 255, 0.2)'
					}}>
						<div className="kpi-badge">平均评分</div>
						<div style={{ fontSize: 24, fontWeight: 600, marginTop: 8 }}>{avgRating}</div>
					</div>
					<div style={{ 
						background: 'rgba(255, 255, 255, 0.95)',
						borderRadius: '12px',
						padding: '24px',
						boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
						backdropFilter: 'blur(10px)',
						border: '1px solid rgba(255, 255, 255, 0.2)'
					}}>
						<div className="kpi-badge">可渲染成功率</div>
						<div style={{ fontSize: 24, fontWeight: 600, marginTop: 8 }}>{successRate}</div>
					</div>
				</div>

				{/* 列表区块 */}
				<div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 24 }}>
					<div style={{ 
						background: 'rgba(255, 255, 255, 0.95)',
						borderRadius: '12px',
						padding: '24px',
						boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
						backdropFilter: 'blur(10px)',
						border: '1px solid rgba(255, 255, 255, 0.2)'
					}}>
						<h3 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: '#1f2937' }}>用户反馈</h3>
						<p style={{ marginTop: 6, marginBottom: 8, color: '#6b7280' }}>用户对生成模型质量的打分记录</p>
						<ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
							{feedbacks.map((f, i) => (
								<li key={i} style={{ padding: '12px 8px', borderTop: i === 0 ? 'none' : '1px solid #f3f4f6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
									<span style={{ color: '#374151' }}>模型 {f.modelId.slice(0,8)}</span>
									<span style={{ color: '#111827', fontWeight: 600 }}>评分 {f.rating}</span>
								</li>
							))}
						</ul>
					</div>
					<div style={{ 
						background: 'rgba(255, 255, 255, 0.95)',
						borderRadius: '12px',
						padding: '24px',
						boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
						backdropFilter: 'blur(10px)',
						border: '1px solid rgba(255, 255, 255, 0.2)'
					}}>
						<h3 style={{ margin: 0, fontSize: 18, fontWeight: 600, color: '#1f2937' }}>性能指标</h3>
						<p style={{ marginTop: 6, marginBottom: 8, color: '#6b7280' }}>模型下载与渲染性能统计</p>
						<ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
							{metrics.map((m, i) => (
								<li key={i} style={{ padding: '12px 8px', borderTop: i === 0 ? 'none' : '1px solid #f3f4f6', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
									<span style={{ color: '#374151' }}>模型 {m.modelId.slice(0,8)}</span>
									<span style={{ color: '#6b7280' }}>加载耗时</span>
									<span style={{ color: '#111827', fontWeight: 600 }}>{m.loadTimeMs ?? '-'} ms</span>
								</li>
							))}
						</ul>
					</div>
				</div>
			</div>
		</div>
	);
} 