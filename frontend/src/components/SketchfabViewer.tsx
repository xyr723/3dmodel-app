import { useEffect, useRef } from 'react';
import type { SketchfabModel } from '../types';

interface SketchfabViewerProps {
  model: SketchfabModel | null;
  onMetrics?: (metrics: any) => void;
}

export function SketchfabViewer({ model, onMetrics }: SketchfabViewerProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (model && onMetrics) {
      // 记录模型预览指标
      onMetrics({
        isDownloadedRenderable: true,
        loadTimeMs: 0, // Sketchfab处理加载
        triangleCountEstimate: model.face_count || 0
      });
    }
  }, [model, onMetrics]);

  if (!model) {
    return (
      <div style={{ 
        width: '100%', 
        height: '50vh', 
        minHeight: 400, 
        maxHeight: 800, 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: 8,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: 18,
        fontWeight: 'bold'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🎨</div>
          <div>选择一个模型开始预览</div>
          <div style={{ fontSize: 14, marginTop: 8, opacity: 0.8 }}>
            浏览左侧的模型库或进行搜索
          </div>
        </div>
      </div>
    );
  }

  // 检查是否为演示模型
  const isDemoModel = model.uid.startsWith('demo-');
  
  // 构建Sketchfab嵌入URL
  const embedUrl = model.embed_url || `https://sketchfab.com/models/${model.uid}/embed?autostart=1&ui_theme=dark&ui_controls=1&ui_infos=0&ui_inspector=0&ui_stop=0&ui_watermark=0`;

  return (
    <div style={{ 
      width: '100%', 
      height: '50vh', 
      minHeight: 400, 
      maxHeight: 800, 
      borderRadius: 8,
      overflow: 'hidden',
      position: 'relative',
      backgroundColor: '#000'
    }}>
      {isDemoModel ? (
        // 演示模型显示信息卡片
        <div style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          textAlign: 'center',
          borderRadius: 8
        }}>
          <div>
            <div style={{ fontSize: 64, marginBottom: 16 }}>🎨</div>
            <div style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 8 }}>{model.name}</div>
            <div style={{ fontSize: 16, marginBottom: 16, opacity: 0.9 }}>{model.description}</div>
            <div style={{ fontSize: 14, opacity: 0.8 }}>
              <div>👤 作者: {model.author}</div>
              <div>🔺 面数: {model.face_count?.toLocaleString()}</div>
              <div>📄 许可证: {model.license_label}</div>
            </div>
            <div style={{ 
              marginTop: 24, 
              padding: '12px 24px', 
              background: 'rgba(255, 255, 255, 0.2)', 
              borderRadius: 24,
              display: 'inline-block'
            }}>
              🔧 演示模式 - 配置API密钥查看真实模型
            </div>
          </div>
        </div>
      ) : (
        <iframe
          ref={iframeRef}
          src={embedUrl}
          style={{
            width: '100%',
            height: '100%',
            border: 'none',
            borderRadius: 8
          }}
          allow="autoplay; fullscreen; vr"
          allowFullScreen
          loading="lazy"
          title={`Sketchfab model: ${model.name}`}
        />
      )}
      
      {/* 模型信息叠加层 - 只在非演示模式下显示 */}
      {!isDemoModel && (
        <>
          <div style={{
            position: 'absolute',
            top: 12,
            left: 12,
            right: 12,
            background: 'rgba(0, 0, 0, 0.7)',
            color: 'white',
            padding: '8px 12px',
            borderRadius: 6,
            fontSize: 12,
            zIndex: 10,
            backdropFilter: 'blur(4px)'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: 4 }}>{model.name}</div>
            <div style={{ display: 'flex', gap: 12, fontSize: 11, opacity: 0.9 }}>
              <span>👤 {model.author}</span>
              {model.face_count && <span>🔺 {model.face_count.toLocaleString()} faces</span>}
              <span>👁 {model.view_count?.toLocaleString() || 0}</span>
              <span>❤️ {model.like_count?.toLocaleString() || 0}</span>
            </div>
          </div>

          {/* 许可证信息 */}
          {model.license_label && (
            <div style={{
              position: 'absolute',
              bottom: 12,
              right: 12,
              background: model.license === 'CC0' ? 'rgba(40, 167, 69, 0.9)' : 'rgba(23, 162, 184, 0.9)',
              color: 'white',
              padding: '4px 8px',
              borderRadius: 4,
              fontSize: 10,
              fontWeight: 'bold',
              zIndex: 10
            }}>
              {model.license_label}
            </div>
          )}
        </>
      )}
    </div>
  );
}
