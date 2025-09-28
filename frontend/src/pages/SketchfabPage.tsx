import { useState } from 'react';
import { SketchfabBrowser } from '../components/SketchfabBrowser';
import { ModelViewer } from '../components/ModelViewer';
import type { SketchfabModel, GeneratedModel, EvaluationMetrics, Feedback } from '../types';
import { useEvalStore } from '../store/evalStore';
import { sketchfabModelToGeneratedModel, downloadSketchfabModel } from '../services/sketchfabClient';

export default function SketchfabPage() {
  const [selectedModel, setSelectedModel] = useState<SketchfabModel | null>(null);
  const [generatedModel, setGeneratedModel] = useState<GeneratedModel | null>(null);
  const [downloading, setDownloading] = useState(false);
  const addMetrics = useEvalStore((s) => s.addMetrics);
  const addFeedback = useEvalStore((s) => s.addFeedback);

  const handleModelSelect = (model: SketchfabModel) => {
    setSelectedModel(model);
    // 转换为 GeneratedModel 格式以便在 ModelViewer 中使用
    const converted = sketchfabModelToGeneratedModel(model);
    setGeneratedModel(converted);
  };

  const onMetrics = async (m: Partial<EvaluationMetrics>) => {
    if (!generatedModel) return;
    await addMetrics({
      inputHash: generatedModel.inputHash,
      modelId: generatedModel.id,
      isDownloadedRenderable: !!m.isDownloadedRenderable,
      fileSizeBytes: m.fileSizeBytes,
      loadTimeMs: m.loadTimeMs,
      triangleCountEstimate: m.triangleCountEstimate,
    });
  };

  const onRate = async (rating: 1 | 2 | 3 | 4 | 5) => {
    if (!generatedModel) return;
    const fb: Feedback = {
      modelId: generatedModel.id,
      inputHash: generatedModel.inputHash,
      rating,
      timestamp: Date.now(),
    };
    await addFeedback(fb);
    alert('感谢您的反馈！');
  };

  const handleDownload = async () => {
    if (!selectedModel || !selectedModel.downloadable) return;
    
    setDownloading(true);
    try {
      const downloadResponse = await downloadSketchfabModel({
        model_uid: selectedModel.uid,
        format: 'original'
      });
      
      if (downloadResponse.download_url) {
        // 创建临时链接进行下载
        const link = document.createElement('a');
        link.href = downloadResponse.download_url;
        link.download = `${selectedModel.name}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        alert('下载已开始！');
      } else {
        alert('下载链接获取失败，请稍后重试。');
      }
    } catch (error: any) {
      console.error('Download failed:', error);
      alert(`下载失败: ${error.message || '未知错误'}`);
    } finally {
      setDownloading(false);
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
        {/* 页面标题区域 */}
        <div className="surface">
          <h1 className="h1 sm:text-24">
            Sketchfab 3D 模型库
          </h1>
          <p style={{ 
            marginTop: '12px', 
            marginBottom: 0,
            color: '#6b7280',
            fontSize: '16px',
            lineHeight: '1.5'
          }}>
            浏览和搜索 Sketchfab 上的 3D 模型 - 点击搜索按钮开始浏览
          </p>
        </div>

        {/* 主要内容区域 */}
        <div className="grid grid-aside-main gap-24 sm:grid-1">
          {/* 左侧 Sketchfab 浏览器 */}
          <div className="panel sticky-20">
            <h3 className="h3">模型搜索</h3>
            <SketchfabBrowser onModelSelect={handleModelSelect} />
          </div>

          {/* 右侧预览区域 */}
          <div className="panel">
            <h3 className="h3">模型预览</h3>
            <div className="preview">
              <ModelViewer url={generatedModel?.glbUrl} onMetrics={onMetrics} />
            </div>
            
            {selectedModel && (
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

            {/* 模型详情 */}
            {selectedModel && (
              <div style={{ 
                marginTop: '24px',
                padding: '16px',
                backgroundColor: '#f8f9fa',
                borderRadius: '8px'
              }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: 18, fontWeight: 'bold' }}>
                  {selectedModel.name}
                </h4>
                
                <p style={{ margin: '0 0 12px 0', color: '#666', lineHeight: 1.5 }}>
                  {selectedModel.description}
                </p>
                
                <div style={{ display: 'grid', gap: 8, gridTemplateColumns: '1fr 1fr', marginBottom: 12 }}>
                  <div>
                    <strong>作者:</strong> 
                    <a 
                      href={selectedModel.author_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ color: '#007bff', textDecoration: 'none', marginLeft: 4 }}
                    >
                      {selectedModel.author}
                    </a>
                  </div>
                  <div><strong>面数:</strong> {selectedModel.face_count.toLocaleString()}</div>
                  <div><strong>顶点数:</strong> {selectedModel.vertex_count.toLocaleString()}</div>
                  <div><strong>许可证:</strong> {selectedModel.license_label}</div>
                  <div><strong>浏览数:</strong> {selectedModel.view_count.toLocaleString()}</div>
                  <div><strong>点赞数:</strong> {selectedModel.like_count.toLocaleString()}</div>
                </div>
                
                <div style={{ marginBottom: 12 }}>
                  <strong>标签:</strong>
                  <div style={{ marginTop: 4, display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                    {selectedModel.tags.map(tag => (
                      <span 
                        key={tag}
                        style={{ 
                          fontSize: 12, 
                          padding: '4px 8px', 
                          backgroundColor: '#e9ecef', 
                          color: '#495057',
                          borderRadius: 12,
                          border: '1px solid #dee2e6'
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                
                {selectedModel.animated && (
                  <div style={{ marginBottom: 8, color: '#007bff', fontSize: 14 }}>
                    🎬 此模型包含动画
                  </div>
                )}
                
                {selectedModel.rigged && (
                  <div style={{ marginBottom: 8, color: '#28a745', fontSize: 14 }}>
                    🦴 此模型包含骨骼绑定
                  </div>
                )}
                
                {selectedModel.downloadable && (
                  <div style={{ marginTop: 16 }}>
                    <button 
                      onClick={handleDownload}
                      disabled={downloading}
                      style={{
                        display: 'inline-block',
                        padding: '12px 24px',
                        backgroundColor: downloading ? '#6c757d' : '#007bff',
                        color: 'white',
                        border: 'none',
                        borderRadius: 6,
                        fontSize: 14,
                        fontWeight: 'bold',
                        cursor: downloading ? 'not-allowed' : 'pointer',
                        transition: 'background-color 0.2s ease'
                      }}
                    >
                      {downloading ? '下载中...' : '⬇️ 下载模型'}
                    </button>
                    {selectedModel.license_label && (
                      <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                        ⚠️ 下载前请确保遵守许可证要求: {selectedModel.license_label}
                      </div>
                    )}
                  </div>
                )}
                
                <div style={{ marginTop: 12, fontSize: 12, color: '#6c757d' }}>
                  发布时间: {new Date(selectedModel.published_at).toLocaleDateString()}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
