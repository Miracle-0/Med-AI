import React, { useState } from 'react';
import { Layout, Tabs } from 'antd';
import TextbookPanel from './components/TextbookPanel';
import GraphVisualization from './components/GraphVisualization';
import RAGPanel from './components/RAGPanel';
import ChatPanel from './components/ChatPanel';

const { Header, Sider, Content } = Layout;

function App() {
  const [activeTab, setActiveTab] = useState('graph');
  const [selectedTextbook, setSelectedTextbook] = useState(null);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', borderBottom: '1px solid #f0f0f0' }}>
        <h1 style={{ margin: 0, fontSize: '20px' }}>学科知识整合智能体</h1>
      </Header>
      <Layout>
        <Sider width={300} style={{ background: '#fff', borderRight: '1px solid #f0f0f0', padding: '16px' }}>
          <TextbookPanel
            onSelect={setSelectedTextbook}
            selected={selectedTextbook}
          />
        </Sider>
        <Content style={{ padding: '16px' }}>
          <GraphVisualization textbookId={selectedTextbook} />
        </Content>
        <Sider width={400} style={{ background: '#fff', borderLeft: '1px solid #f0f0f0', padding: '16px' }}>
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              { key: 'rag', label: 'RAG问答', children: <RAGPanel /> },
              { key: 'chat', label: '对话', children: <ChatPanel /> },
            ]}
          />
        </Sider>
      </Layout>
    </Layout>
  );
}

export default App;
