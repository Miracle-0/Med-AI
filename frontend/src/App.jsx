import React, { useState, useCallback } from 'react';
import { Layout, Tabs, message } from 'antd';
import TextbookPanel from './components/TextbookPanel';
import GraphVisualization from './components/GraphVisualization';
import RAGPanel from './components/RAGPanel';
import ChatPanel from './components/ChatPanel';
import { demoAPI } from './services/api';

const { Header, Sider, Content } = Layout;

function App() {
  const [activeTab, setActiveTab] = useState('graph');
  const [selectedTextbook, setSelectedTextbook] = useState(null);
  const [demoLoading, setDemoLoading] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleLoadDemo = useCallback(async () => {
    setDemoLoading(true);
    try {
      const res = await demoAPI.load();
      message.success(res.data.message);
      setSelectedTextbook(res.data.textbook_id);
      setRefreshKey(k => k + 1);
    } catch (err) {
      message.error('加载演示数据失败');
    }
    setDemoLoading(false);
  }, []);

  return (
    <Layout style={{ height: '100vh', background: 'transparent' }}>
      {/* Header */}
      <Header style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 28px', height: 56, borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(10, 14, 26, 0.9)',
        backdropFilter: 'blur(20px)',
        position: 'relative', zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'linear-gradient(135deg, var(--accent), var(--accent-dim))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 16, boxShadow: '0 2px 12px rgba(240,160,48,0.3)',
          }}>
            <span style={{ filter: 'brightness(0) invert(0.1)' }}>🧠</span>
          </div>
          <h1 style={{
            margin: 0, fontSize: 17, fontWeight: 600,
            fontFamily: 'var(--font-display)',
            color: 'var(--text-primary)',
            letterSpacing: 2,
          }}>
            学科知识整合智能体
          </h1>
          <span style={{
            fontSize: 10, color: 'var(--text-muted)',
            fontFamily: 'var(--font-mono)',
            padding: '2px 8px', borderRadius: 4,
            border: '1px solid rgba(255,255,255,0.06)',
            letterSpacing: 1,
          }}>
            Knowledge Weaver
          </span>
        </div>

        <button
          onClick={handleLoadDemo}
          disabled={demoLoading}
          style={{
            background: demoLoading ? 'var(--bg-glass)' : 'linear-gradient(135deg, rgba(240,160,48,0.15), rgba(240,160,48,0.05))',
            border: '1px solid rgba(240,160,48,0.3)',
            color: 'var(--accent)',
            padding: '6px 18px', borderRadius: 8,
            cursor: demoLoading ? 'wait' : 'pointer',
            fontFamily: 'var(--font-display)',
            fontSize: 13, fontWeight: 600,
            letterSpacing: 1,
            transition: 'all 0.3s',
          }}
          onMouseEnter={e => { if (!demoLoading) e.target.style.borderColor = 'var(--accent)'; }}
          onMouseLeave={e => { e.target.style.borderColor = 'rgba(240,160,48,0.3)'; }}
        >
          {demoLoading ? '加载中...' : '✦ 加载演示数据'}
        </button>
      </Header>

      {/* Main Layout */}
      <Layout style={{ background: 'transparent' }}>
        {/* Left Sider - Textbook Panel */}
        <Sider width={300} style={{
          background: 'var(--bg-base)',
          borderRight: '1px solid var(--border-subtle)',
          overflow: 'auto', animation: 'slideInLeft 0.5s ease',
        }}>
          <TextbookPanel
            onSelect={setSelectedTextbook}
            selected={selectedTextbook}
            refreshKey={refreshKey}
          />
        </Sider>

        {/* Center - Graph */}
        <Content style={{
          position: 'relative', overflow: 'hidden',
          animation: 'fadeIn 0.6s ease',
        }}>
          {/* Ambient glow */}
          <div style={{
            position: 'absolute', top: '30%', left: '50%',
            width: 600, height: 600,
            background: 'radial-gradient(circle, rgba(240,160,48,0.06) 0%, transparent 70%)',
            transform: 'translate(-50%, -50%)', pointerEvents: 'none',
          }} />
          <GraphVisualization
            textbookId={selectedTextbook}
            refreshKey={refreshKey}
          />
        </Content>

        {/* Right Sider - RAG & Chat */}
        <Sider width={400} style={{
          background: 'var(--bg-base)',
          borderLeft: '1px solid var(--border-subtle)',
          overflow: 'auto', animation: 'slideInRight 0.5s ease',
        }}>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            centered
            style={{ height: '100%' }}
            items={[
              { key: 'rag', label: 'RAG 问答', children: <RAGPanel /> },
              { key: 'chat', label: '对话', children: <ChatPanel /> },
            ]}
          />
        </Sider>
      </Layout>
    </Layout>
  );
}

export default App;
