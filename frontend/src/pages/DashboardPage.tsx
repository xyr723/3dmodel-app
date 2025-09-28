import { useEffect } from 'react';
import { useSearchStore } from '../store/searchStore';

export default function DashboardPage() {
	const { searchRecords, load, clearHistory } = useSearchStore();
	useEffect(() => { load(); }, []);

	const totalSearches = searchRecords.length;
	const avgSearchTime = searchRecords.length 
		? (searchRecords.reduce((s, r) => s + r.search_time, 0) / searchRecords.length).toFixed(2) + 's'
		: '-';
	const totalModelsFound = searchRecords.reduce((s, r) => s + r.models_found, 0);
	const mostPopularQuery = searchRecords.length 
		? searchRecords.reduce((prev, current) => 
			searchRecords.filter(r => r.query === current.query).length > 
			searchRecords.filter(r => r.query === prev.query).length ? current : prev
		).query
		: '-';

	const handleClearHistory = async () => {
		if (confirm('确定要清空所有搜索记录吗？此操作不可撤销。')) {
			await clearHistory();
		}
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
				{/* 标题区 */}
				<div className="surface">
					<h2 style={{ 
						margin: 0, 
						fontSize: 28, 
						lineHeight: '32px',
						background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
						WebkitBackgroundClip: 'text',
						WebkitTextFillColor: 'transparent',
						fontWeight: 700
					}}>
						Sketchfab 搜索记录
					</h2>
					<p style={{ marginTop: 12, marginBottom: 0, color: '#6b7280', fontSize: 16, lineHeight: 1.5 }}>
						查看您的 Sketchfab 3D 模型搜索历史记录和统计数据
					</p>
					{searchRecords.length > 0 && (
						<button 
							onClick={handleClearHistory}
							style={{
								marginTop: 16,
								padding: '8px 16px',
								backgroundColor: '#ef4444',
								color: 'white',
								border: 'none',
								borderRadius: '6px',
								fontSize: '14px',
								cursor: 'pointer',
								transition: 'background-color 0.2s'
							}}
							onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#dc2626'}
							onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#ef4444'}
						>
							🗑️ 清空搜索记录
						</button>
					)}
				</div>

				{/* KPI 区域 */}
				<div className="grid grid-2 gap-24 sm:grid-1">
					<div className="panel">
						<div className="kpi-badge">总搜索次数</div>
						<div style={{ fontSize: 24, fontWeight: 600, marginTop: 8 }}>{totalSearches}</div>
					</div>
					<div className="panel">
						<div className="kpi-badge">平均搜索耗时</div>
						<div style={{ fontSize: 24, fontWeight: 600, marginTop: 8 }}>{avgSearchTime}</div>
					</div>
				</div>

				<div className="grid grid-2 gap-24 sm:grid-1">
					<div className="panel">
						<div className="kpi-badge">累计找到模型</div>
						<div style={{ fontSize: 24, fontWeight: 600, marginTop: 8 }}>{totalModelsFound.toLocaleString()}</div>
					</div>
					<div className="panel">
						<div className="kpi-badge">最热搜索词</div>
						<div style={{ fontSize: 24, fontWeight: 600, marginTop: 8 }}>{mostPopularQuery}</div>
					</div>
				</div>

				{/* 搜索记录列表 */}
				<div className="panel">
					<h3 className="h3" style={{ marginBottom: 8 }}>搜索历史记录</h3>
					<p className="muted" style={{ marginTop: 0, marginBottom: 16 }}>您最近的 Sketchfab 搜索记录</p>
					
					{searchRecords.length === 0 ? (
						<div style={{ 
							textAlign: 'center', 
							padding: '40px', 
							color: '#6b7280',
							fontSize: '16px'
						}}>
							<div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
							<div>还没有搜索记录</div>
							<div style={{ fontSize: '14px', marginTop: '8px' }}>
								前往 Sketchfab 页面开始搜索 3D 模型吧！
							</div>
						</div>
					) : (
						<div style={{ 
							maxHeight: '600px', 
							overflowY: 'auto',
							border: '1px solid #e5e7eb',
							borderRadius: '8px'
						}}>
							{searchRecords.map((record, i) => (
								<div key={record.id} style={{ 
									padding: '16px', 
									borderBottom: i === searchRecords.length - 1 ? 'none' : '1px solid #f3f4f6',
									display: 'flex',
									justifyContent: 'space-between',
									alignItems: 'flex-start',
									gap: '16px'
								}}>
									<div style={{ flex: 1 }}>
										<div style={{ 
											fontWeight: 600, 
											color: '#111827',
											fontSize: '16px',
											marginBottom: '4px'
										}}>
											"{record.query}"
										</div>
										<div style={{ 
											fontSize: '14px', 
											color: '#6b7280',
											marginBottom: '8px'
										}}>
											{new Date(record.timestamp).toLocaleString('zh-CN')}
										</div>
										<div style={{ 
											display: 'flex', 
											gap: '12px', 
											flexWrap: 'wrap',
											fontSize: '12px',
											color: '#6b7280'
										}}>
											<span>找到 {record.models_found} 个模型</span>
											<span>耗时 {record.search_time.toFixed(2)}s</span>
											{record.category && <span>分类: {record.category}</span>}
											{record.license && <span>许可: {record.license}</span>}
										</div>
										{record.filters_applied && (
											<div style={{ 
												marginTop: '8px',
												display: 'flex',
												gap: '4px',
												flexWrap: 'wrap'
											}}>
												{record.filters_applied.downloadable && (
													<span style={{ 
														fontSize: '10px',
														padding: '2px 6px',
														backgroundColor: '#dbeafe',
														color: '#1e40af',
														borderRadius: '4px'
													}}>可下载</span>
												)}
												{record.filters_applied.animated && (
													<span style={{ 
														fontSize: '10px',
														padding: '2px 6px',
														backgroundColor: '#dcfce7',
														color: '#166534',
														borderRadius: '4px'
													}}>动画</span>
												)}
												{record.filters_applied.rigged && (
													<span style={{ 
														fontSize: '10px',
														padding: '2px 6px',
														backgroundColor: '#fef3c7',
														color: '#92400e',
														borderRadius: '4px'
													}}>骨骼</span>
												)}
												{record.filters_applied.staff_picked && (
													<span style={{ 
														fontSize: '10px',
														padding: '2px 6px',
														backgroundColor: '#fce7f3',
														color: '#be185d',
														borderRadius: '4px'
													}}>官方推荐</span>
												)}
											</div>
										)}
									</div>
								</div>
							))}
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
