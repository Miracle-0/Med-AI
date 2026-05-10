import React, { useState } from 'react';
import { Input, Button, message } from 'antd';
import { SendOutlined, SearchOutlined, BookOutlined, LinkOutlined } from '@ant-design/icons';
import { ragAPI } from '../services/api';

const suggestedQuestions = [
  '细胞膜的结构是什么？',
  '神经冲动如何传导？',
  '特异性免疫包括哪些？',
  '主动运输和被动运输的区别？',
];

const RAGPanel = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleQuery = async (q) => {
    const question = q || query;
    if (!question.trim()) {
      message.warning('请输入问题');
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await ragAPI.query(question);
      setResult(res.data);
    } catch (e) {
      message.error('查询失败');
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '16px 16px 24px', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' }}>
      {/* Input area */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="输入问题，基于教材内容回答..."
            onPressEnter={() => handleQuery()}
            prefix={<SearchOutlined style={{ color: 'var(--text-muted)' }} />}
            style={{ flex: 1 }}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={() => handleQuery()}
            loading={loading}
          >
            提问
          </Button>
        </div>

        {/* Suggested questions */}
        {!result && !loading && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => { setQuery(q); handleQuery(q); }}
                style={{
                  background: 'var(--bg-glass)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-secondary)',
                  padding: '4px 12px', borderRadius: 16,
                  cursor: 'pointer', fontSize: 11,
                  fontFamily: 'var(--font-body)',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={e => {
                  e.target.style.borderColor = 'var(--accent)';
                  e.target.style.color = 'var(--accent)';
                }}
                onMouseLeave={e => {
                  e.target.style.borderColor = 'var(--border-subtle)';
                  e.target.style.color = 'var(--text-secondary)';
                }}
              >
                {q}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Loading state */}
      {loading && (
        <div style={{
          flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexDirection: 'column', gap: 12,
        }}>
          <div style={{
            width: 40, height: 40, borderRadius: 12,
            background: 'var(--accent-glow)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            animation: 'pulse 1.5s infinite',
          }}>
            <SearchOutlined style={{ color: 'var(--accent)', fontSize: 18 }} />
          </div>
          <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-display)', fontSize: 13 }}>
            检索知识库中...
          </span>
        </div>
      )}

      {/* Result */}
      {result && (
        <div style={{ flex: 1, overflow: 'auto', animation: 'fadeIn 0.4s ease' }}>
          {/* Answer */}
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius)',
            padding: '20px', marginBottom: 16,
          }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12,
              paddingBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.04)',
            }}>
              <BookOutlined style={{ color: 'var(--accent)' }} />
              <span style={{
                fontFamily: 'var(--font-display)', fontWeight: 600,
                fontSize: 13, color: 'var(--accent)', letterSpacing: 1,
              }}>
                回答
              </span>
            </div>
            <div style={{
              fontSize: 13, lineHeight: 1.8, color: 'var(--text-primary)',
              whiteSpace: 'pre-wrap',
            }}>
              {result.answer}
            </div>
          </div>

          {/* Citations */}
          {result.citations?.length > 0 && (
            <div style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius)',
              padding: '16px',
            }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12,
                paddingBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.04)',
              }}>
                <LinkOutlined style={{ color: 'var(--text-muted)', fontSize: 12 }} />
                <span style={{
                  fontFamily: 'var(--font-display)', fontSize: 12,
                  color: 'var(--text-muted)', letterSpacing: 1,
                }}>
                  引用来源
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {result.citations.map((c, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '8px 12px', borderRadius: 8,
                    background: 'var(--bg-glass)',
                  }}>
                    <span style={{
                      width: 20, height: 20, borderRadius: 4,
                      background: 'var(--accent-glow)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 10, color: 'var(--accent)',
                      fontFamily: 'var(--font-mono)', fontWeight: 600,
                      flexShrink: 0,
                    }}>
                      {i + 1}
                    </span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{
                        fontSize: 11, color: 'var(--text-secondary)',
                        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                      }}>
                        {c.chapter}
                      </div>
                    </div>
                    <span style={{
                      fontSize: 10, fontFamily: 'var(--font-mono)',
                      color: 'var(--accent)', flexShrink: 0,
                    }}>
                      {(c.relevance_score * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && (
        <div style={{
          flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexDirection: 'column', gap: 12, opacity: 0.4,
        }}>
          <SearchOutlined style={{ fontSize: 28, color: 'var(--text-muted)' }} />
          <span style={{
            fontFamily: 'var(--font-display)', fontSize: 13,
            color: 'var(--text-muted)',
          }}>
            输入问题开始检索
          </span>
        </div>
      )}
    </div>
  );
};

export default RAGPanel;
