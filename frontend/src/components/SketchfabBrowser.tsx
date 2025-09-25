import { useState, useEffect } from 'react';
import type { SketchfabModel, SketchfabSearchRequest, SketchfabCategory, SketchfabLicense } from '../types';
import { searchSketchfabModels, getPopularSketchfabModels } from '../services/sketchfabClient';

interface SketchfabBrowserProps {
  onModelSelect: (model: SketchfabModel) => void;
}

export function SketchfabBrowser({ onModelSelect }: SketchfabBrowserProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [models, setModels] = useState<SketchfabModel[]>([]);
  const [categories, setCategories] = useState<SketchfabCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortBy, setSortBy] = useState<'relevance' | 'likes' | 'views' | 'recent'>('relevance');
  const [filters, setFilters] = useState({
    downloadable: true,
    animated: false,
    rigged: false,
    staff_picked: false
  });
  const [selectedLicense, setSelectedLicense] = useState<SketchfabLicense | ''>('');

  // 许可证选项
  const licenseOptions: { value: SketchfabLicense | ''; label: string }[] = [
    { value: '', label: '所有许可证' },
    { value: 'cc0', label: 'CC0 公共领域' },
    { value: 'public_domain', label: '公共领域' },
    { value: 'attribution', label: '署名 (CC BY)' },
    { value: 'attribution_sharealike', label: '署名-相同方式共享 (CC BY-SA)' },
    { value: 'attribution_noncommercial', label: '署名-非商业性使用 (CC BY-NC)' },
    { value: 'attribution_noncommercial_sharealike', label: '署名-非商业性使用-相同方式共享 (CC BY-NC-SA)' },
    { value: 'attribution_noderivs', label: '署名-禁止演绎 (CC BY-ND)' },
    { value: 'attribution_noncommercial_noderivs', label: '署名-非商业性使用-禁止演绎 (CC BY-NC-ND)' },
    { value: 'all_rights_reserved', label: '保留所有权利' }
  ];

  // 提供默认分类选项，避免自动加载
  useEffect(() => {
    // 设置默认分类，避免发送请求
    setCategories([
      { id: '1', name: 'Characters', slug: 'characters' },
      { id: '2', name: 'Vehicles', slug: 'vehicles' },
      { id: '3', name: 'Architecture', slug: 'architecture' },
      { id: '4', name: 'Nature', slug: 'nature' },
      { id: '5', name: 'Furniture', slug: 'furniture' },
      { id: '6', name: 'Animals', slug: 'animals' },
      { id: '7', name: 'Food', slug: 'food' },
      { id: '8', name: 'Technology', slug: 'technology' }
    ]);
  }, []);

  // 移除自动加载热门模型，用户需要手动搜索

  // 搜索模型
  const handleSearch = async () => {
    setLoading(true);
    setError(undefined);
    
    try {
      if (searchQuery.trim()) {
        // 有搜索关键词时进行搜索
        const searchRequest: SketchfabSearchRequest = {
          query: searchQuery,
          category: selectedCategory || undefined,
          license: selectedLicense || undefined,
          downloadable: filters.downloadable,
          animated: filters.animated,
          rigged: filters.rigged,
          staff_picked: filters.staff_picked,
          page: currentPage,
          per_page: 20,
          sort_by: sortBy
        };
        
        const response = await searchSketchfabModels(searchRequest);
        setModels(response.models);
        setTotalPages(response.total_pages);
      } else {
        // 没有搜索关键词时加载热门模型
        const popular = await getPopularSketchfabModels(selectedCategory || undefined, 20);
        setModels(popular);
        setTotalPages(1);
      }
    } catch (err: any) {
      setError(err?.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  // 重置搜索
  const handleReset = () => {
    setSearchQuery('');
    setCurrentPage(1);
    setSelectedCategory('');
    setSelectedLicense('');
    setFilters({
      downloadable: true,
      animated: false,
      rigged: false,
      staff_picked: false
    });
  };

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      {/* 搜索栏 */}
      <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr auto auto' }}>
        <input
          type="text"
          placeholder="搜索 Sketchfab 模型..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          style={{ padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
        />
        <button 
          onClick={handleSearch} 
          disabled={loading}
          style={{ padding: '8px 16px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: 4 }}
        >
          {loading ? '搜索中...' : searchQuery.trim() ? '搜索' : '浏览热门'}
        </button>
        <button 
          onClick={handleReset}
          style={{ padding: '8px 16px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: 4 }}
        >
          重置
        </button>
      </div>

      {/* 分类、许可证和排序 */}
      <div style={{ display: 'grid', gap: 12, gridTemplateColumns: '1fr 1fr 1fr' }}>
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>分类:</label>
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
          >
            <option value="">所有分类</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.slug}>{cat.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>许可证:</label>
          <select 
            value={selectedLicense} 
            onChange={(e) => setSelectedLicense(e.target.value as SketchfabLicense | '')}
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
          >
            {licenseOptions.map(option => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: 4, fontWeight: 'bold' }}>排序:</label>
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value as any)}
            style={{ width: '100%', padding: 8, borderRadius: 4, border: '1px solid #ccc' }}
          >
            <option value="relevance">相关性</option>
            <option value="likes">点赞数</option>
            <option value="views">浏览数</option>
            <option value="recent">最新</option>
          </select>
        </div>
      </div>

      {/* 过滤器 */}
      <div style={{ display: 'grid', gap: 8, gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input 
            type="checkbox" 
            checked={filters.downloadable}
            onChange={(e) => setFilters(prev => ({ ...prev, downloadable: e.target.checked }))}
          />
          可下载
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input 
            type="checkbox" 
            checked={filters.animated}
            onChange={(e) => setFilters(prev => ({ ...prev, animated: e.target.checked }))}
          />
          有动画
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input 
            type="checkbox" 
            checked={filters.rigged}
            onChange={(e) => setFilters(prev => ({ ...prev, rigged: e.target.checked }))}
          />
          有骨骼
        </label>
        <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <input 
            type="checkbox" 
            checked={filters.staff_picked}
            onChange={(e) => setFilters(prev => ({ ...prev, staff_picked: e.target.checked }))}
          />
          官方推荐
        </label>
      </div>

      {/* 错误信息 */}
      {error && (
        <div style={{ color: 'tomato', padding: 12, backgroundColor: '#ffe6e6', borderRadius: 4 }}>
          {error}
        </div>
      )}

      {/* 模型网格 */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', 
        gap: 16,
        marginTop: 16
      }}>
        {models.map(model => (
          <SketchfabModelCard 
            key={model.uid} 
            model={model} 
            onSelect={() => onModelSelect(model)} 
          />
        ))}
      </div>

      {/* 分页 */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 16 }}>
          <button 
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
            style={{ padding: '8px 16px', border: '1px solid #ccc', borderRadius: 4, backgroundColor: 'white' }}
          >
            上一页
          </button>
          <span style={{ padding: '8px 16px', display: 'flex', alignItems: 'center' }}>
            第 {currentPage} 页，共 {totalPages} 页
          </span>
          <button 
            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
            disabled={currentPage === totalPages}
            style={{ padding: '8px 16px', border: '1px solid #ccc', borderRadius: 4, backgroundColor: 'white' }}
          >
            下一页
          </button>
        </div>
      )}

      {models.length === 0 && !loading && (
        <div style={{ 
          textAlign: 'center', 
          color: '#666', 
          padding: 48,
          backgroundColor: '#f8f9fa',
          borderRadius: 8,
          border: '2px dashed #dee2e6'
        }}>
          <div style={{ fontSize: 18, marginBottom: 16, color: '#495057' }}>
            🔍 欢迎来到 Sketchfab 模型库
          </div>
          <div style={{ fontSize: 14, lineHeight: 1.6 }}>
            {searchQuery.trim() ? 
              '没有找到模型，请尝试其他搜索条件' : 
              '输入关键词进行搜索，或者直接点击"浏览热门"按钮查看热门模型'
            }
          </div>
          <div style={{ marginTop: 16, fontSize: 12, color: '#6c757d' }}>
            💡 提示：所有搜索参数都是可选的，点击搜索按钮后才会发送请求
          </div>
        </div>
      )}
    </div>
  );
}

// 模型卡片组件
function SketchfabModelCard({ model, onSelect }: { model: SketchfabModel; onSelect: () => void }) {
  return (
    <div 
      style={{ 
        border: '1px solid #ddd', 
        borderRadius: 8, 
        overflow: 'hidden',
        backgroundColor: 'white',
        cursor: 'pointer',
        transition: 'box-shadow 0.2s',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}
      onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)'}
      onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)'}
      onClick={onSelect}
    >
      {/* 缩略图 */}
      <div style={{ aspectRatio: '16/9', overflow: 'hidden' }}>
        <img 
          src={model.thumbnail_url} 
          alt={model.name}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          onError={(e) => {
            e.currentTarget.src = 'https://via.placeholder.com/300x200?text=No+Image';
          }}
        />
      </div>
      
      {/* 模型信息 */}
      <div style={{ padding: 12 }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: 14, fontWeight: 'bold', lineHeight: 1.3 }}>
          {model.name}
        </h3>
        
        <p style={{ 
          margin: '0 0 8px 0', 
          fontSize: 12, 
          color: '#666', 
          lineHeight: 1.4,
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden'
        }}>
          {model.description}
        </p>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <span style={{ fontSize: 11, color: '#888' }}>by {model.author}</span>
          <span style={{ fontSize: 11, color: '#888' }}>{model.face_count.toLocaleString()} faces</span>
        </div>
        
        <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
          <span style={{ fontSize: 10, color: '#666' }}>👁 {model.view_count.toLocaleString()}</span>
          <span style={{ fontSize: 10, color: '#666' }}>❤️ {model.like_count.toLocaleString()}</span>
          {model.animated && <span style={{ fontSize: 10, color: '#007bff' }}>🎬 动画</span>}
          {model.rigged && <span style={{ fontSize: 10, color: '#28a745' }}>🦴 骨骼</span>}
        </div>
        
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
          {model.tags.slice(0, 3).map(tag => (
            <span 
              key={tag}
              style={{ 
                fontSize: 9, 
                padding: '2px 6px', 
                backgroundColor: '#f8f9fa', 
                color: '#666',
                borderRadius: 10,
                border: '1px solid #e9ecef'
              }}
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
