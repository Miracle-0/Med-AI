import React, { useState, useEffect } from 'react';
import { Upload, Button, message, Tag } from 'antd';
import { UploadOutlined, DeleteOutlined, ReloadOutlined, PlayCircleOutlined, FileTextOutlined } from '@ant-design/icons';
import { textbookAPI, graphAPI, ragAPI } from '../services/api';

const TextbookPanel = ({ onSelect, selected, refreshKey }) => {
  const [textbooks, setTextbooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [parsing, setParsing] = useState({});
  const [extracting, setExtracting] = useState({});
  const [progress, setProgress] = useState({});

  useEffect(() => { loadTextbooks(); }, [refreshKey]);

  const loadTextbooks = async () => {
    setLoading(true);
    try {
      const res = await textbookAPI.list();
      setTextbooks(res.data);
    } catch (e) {
      message.error('加载教材列表失败');
    }
    setLoading(false);
  };

  const handleUpload = async (file) => {
    try {
      await textbookAPI.upload(file);
      message.success('上传成功');
      loadTextbooks();
    } catch (e) {
      message.error(`上传失败: ${e.response?.data?.detail || e.message}`);
    }
    return false;
  };

  const handleParse = async (id) => {
    setParsing(p => ({ ...p, [id]: true }));
    try {
      const res = await textbookAPI.parse(id);
      message.success(`解析完成，共 ${res.data.chapters_count} 个章节`);
      loadTextbooks();
    } catch (e) {
      message.error(`解析失败: ${e.response?.data?.detail || e.message}`);
    }
    setParsing(p => ({ ...p, [id]: false }));
  };

  const handleExtract = async (id) => {
    setExtracting(p => ({ ...p, [id]: true }));
    setProgress(p => ({ ...p, [id]: { current: 0, total: 0, phase: 'starting' } }));

    // Start SSE progress listener
    const evtSource = new EventSource(graphAPI.extractProgress(id));
    evtSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setProgress(p => ({ ...p, [id]: data }));
        if (data.status === 'completed' || data.status === 'failed') {
          evtSource.close();
        }
      } catch (e) {}
    };
    evtSource.onerror = () => evtSource.close();

    try {
      await graphAPI.extract(id);
      message.success('知识图谱提取完成');

      // Auto-build RAG index
      await ragAPI.buildIndex(id);
      message.success('RAG 索引构建完成');

      loadTextbooks();
    } catch (e) {
      message.error(`提取失败: ${e.response?.data?.detail || e.message}`);
    }
    setExtracting(p => ({ ...p, [id]: false }));
  };

  const handleDelete = async (id) => {
    try {
      await textbookAPI.delete(id);
      message.success('删除成功');
      loadTextbooks();
      if (selected === id) onSelect(null);
    } catch (e) {
      message.error('删除失败');
    }
  };

  const statusConfig = {
    completed: { color: '#4ade80', bg: 'rgba(74,222,128,0.1)', label: '已完成' },
    parsing:   { color: '#fbbf24', bg: 'rgba(251,191,36,0.1)', label: '解析中' },
    uploaded:  { color: '#60a5fa', bg: 'rgba(96,165,250,0.1)', label: '已上传' },
    failed:    { color: '#f87171', bg: 'rgba(248,113,113,0.1)', label: '失败' },
  };

  const getProgressPercent = (id) => {
    const p = progress[id];
    if (!p || !p.total) return 0;
    return Math.round((p.current / p.total) * 100);
  };

  return (
    <div style={{ padding: '20px 16px' }}>
      {/* Section title */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20,
      }}>
        <div style={{
          width: 3, height: 18, borderRadius: 2,
          background: 'var(--accent)',
        }} />
        <span style={{
          fontFamily: 'var(--font-display)',
          fontSize: 15, fontWeight: 600, color: 'var(--text-primary)',
          letterSpacing: 2,
        }}>
          教材管理
        </span>
      </div>

      {/* Upload & Refresh */}
      <Upload beforeUpload={handleUpload} showUploadList={false} style={{ width: '100%' }}>
        <Button icon={<UploadOutlined />} block style={{ marginBottom: 8, height: 40 }}>
          上传教材文件
        </Button>
      </Upload>
      <Button
        icon={<ReloadOutlined />}
        onClick={loadTextbooks}
        block
        style={{ marginBottom: 20, height: 36 }}
      >
        刷新列表
      </Button>

      {/* Textbook List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {loading && textbooks.length === 0 && (
          <div style={{ textAlign: 'center', padding: 40, color: 'var(--text-muted)' }}>
            加载中...
          </div>
        )}
        {!loading && textbooks.length === 0 && (
          <div style={{
            textAlign: 'center', padding: 40,
            color: 'var(--text-muted)', fontFamily: 'var(--font-display)',
          }}>
            <FileTextOutlined style={{ fontSize: 32, marginBottom: 12, display: 'block', opacity: 0.3 }} />
            <div>暂无教材</div>
            <div style={{ fontSize: 12, marginTop: 4 }}>上传文件或加载演示数据</div>
          </div>
        )}
        {textbooks.map((item, idx) => {
          const isActive = selected === item.textbook_id;
          const st = statusConfig[item.parse_status] || statusConfig.uploaded;
          const prog = progress[item.textbook_id];
          const progPct = getProgressPercent(item.textbook_id);

          return (
            <div
              key={item.textbook_id}
              onClick={() => onSelect(item.textbook_id)}
              style={{
                padding: '12px 14px', borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                background: isActive
                  ? 'linear-gradient(135deg, rgba(240,160,48,0.12), rgba(240,160,48,0.04))'
                  : 'var(--bg-glass)',
                border: `1px solid ${isActive ? 'rgba(240,160,48,0.3)' : 'transparent'}`,
                transition: 'all 0.25s',
                animation: `fadeIn 0.3s ease ${idx * 0.05}s both`,
              }}
              onMouseEnter={e => {
                if (!isActive) e.currentTarget.style.background = 'rgba(255,255,255,0.06)';
              }}
              onMouseLeave={e => {
                if (!isActive) e.currentTarget.style.background = 'var(--bg-glass)';
              }}
            >
              {/* Title & Status */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                <span style={{
                  fontWeight: 500, fontSize: 13, color: isActive ? 'var(--accent)' : 'var(--text-primary)',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 160,
                }}>
                  {item.title}
                </span>
                <span style={{
                  fontSize: 10, fontFamily: 'var(--font-mono)',
                  padding: '2px 8px', borderRadius: 4,
                  color: st.color, background: st.bg,
                }}>
                  {st.label}
                </span>
              </div>

              {/* Filename & chars */}
              <div style={{
                fontSize: 11, color: 'var(--text-muted)',
                fontFamily: 'var(--font-mono)',
                marginBottom: 8,
              }}>
                {item.filename}
                {item.total_chars > 0 && <span style={{ marginLeft: 8 }}>{item.total_chars} 字</span>}
              </div>

              {/* Extraction Progress Bar */}
              {extracting[item.textbook_id] && prog && (
                <div style={{ marginBottom: 8 }}>
                  <div style={{
                    display: 'flex', justifyContent: 'space-between', marginBottom: 4,
                    fontSize: 10, color: 'var(--text-muted)', fontFamily: 'var(--font-mono)',
                  }}>
                    <span>
                      {prog.phase === 'extracting'
                        ? `提取中 ${prog.chapter_name || ''}`
                        : prog.phase === 'saving' ? '保存中...' : '准备中...'}
                    </span>
                    <span>{prog.current}/{prog.total}</span>
                  </div>
                  <div style={{
                    height: 3, borderRadius: 2,
                    background: 'rgba(255,255,255,0.06)',
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      height: '100%', borderRadius: 2,
                      width: `${progPct}%`,
                      background: 'linear-gradient(90deg, var(--accent), var(--accent-dim))',
                      transition: 'width 0.5s ease',
                      boxShadow: '0 0 8px rgba(240,160,48,0.4)',
                    }} />
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: 6 }}>
                {(item.parse_status === 'uploaded' || item.parse_status === 'failed') && (
                  <Button
                    type="text" size="small"
                    icon={<PlayCircleOutlined />}
                    loading={parsing[item.textbook_id]}
                    onClick={(e) => { e.stopPropagation(); handleParse(item.textbook_id); }}
                    style={{ fontSize: 12, color: 'var(--info)' }}
                  >
                    解析
                  </Button>
                )}
                {item.parse_status === 'completed' && (
                  <Button
                    type="text" size="small"
                    icon={<PlayCircleOutlined />}
                    loading={extracting[item.textbook_id]}
                    onClick={(e) => { e.stopPropagation(); handleExtract(item.textbook_id); }}
                    style={{ fontSize: 12, color: 'var(--accent)' }}
                  >
                    提取图谱
                  </Button>
                )}
                <Button
                  type="text" size="small" danger
                  icon={<DeleteOutlined />}
                  onClick={(e) => { e.stopPropagation(); handleDelete(item.textbook_id); }}
                  style={{ fontSize: 12 }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TextbookPanel;
