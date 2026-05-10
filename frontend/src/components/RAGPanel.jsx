import React, { useState } from 'react';
import { Input, Button, List, Card, Tag, Spin, message } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { ragAPI } from '../services/api';

const RAGPanel = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleQuery = async () => {
    if (!query.trim()) {
      message.warning('请输入问题');
      return;
    }
    setLoading(true);
    try {
      const res = await ragAPI.query(query);
      setResult(res.data);
    } catch (error) {
      message.error('查询失败');
    }
    setLoading(false);
  };

  return (
    <div>
      <h3 style={{ marginBottom: 16 }}>RAG问答</h3>
      <div style={{ display: 'flex', marginBottom: 16 }}>
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="输入问题..."
          onPressEnter={handleQuery}
          style={{ marginRight: 8 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleQuery}
          loading={loading}
        >
          提问
        </Button>
      </div>
      {result && (
        <div>
          <Card title="回答" style={{ marginBottom: 16 }}>
            <p>{result.answer}</p>
          </Card>
          {result.citations && result.citations.length > 0 && (
            <Card title="引用来源" size="small">
              <List
                dataSource={result.citations}
                renderItem={(citation) => (
                  <List.Item>
                    <Tag color="blue">{citation.textbook}</Tag>
                    <span>{citation.chapter}</span>
                    <span style={{ marginLeft: 8 }}>第{citation.page}页</span>
                    <Tag color="green" style={{ marginLeft: 'auto' }}>
                      相关度: {(citation.relevance_score * 100).toFixed(1)}%
                    </Tag>
                  </List.Item>
                )}
              />
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default RAGPanel;
