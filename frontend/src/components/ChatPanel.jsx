import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, List, Avatar, Spin, message } from 'antd';
import { SendOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';
import { chatAPI } from '../services/api';

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadHistory = async () => {
    try {
      const res = await chatAPI.getHistory();
      setMessages(res.data);
    } catch (error) {
      console.error('加载历史失败', error);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) {
      message.warning('请输入消息');
      return;
    }
    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);
    try {
      const res = await chatAPI.sendMessage(userMessage);
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (error) {
      message.error('发送失败');
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '500px' }}>
      <h3 style={{ marginBottom: 16 }}>对话</h3>
      <div style={{ flex: 1, overflow: 'auto', marginBottom: 16, padding: '8px', background: '#f5f5f5', borderRadius: '4px' }}>
        <List
          dataSource={messages}
          renderItem={(msg) => (
            <List.Item style={{ border: 'none', padding: '8px 0' }}>
              <List.Item.Meta
                avatar={
                  <Avatar
                    icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{ backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a' }}
                  />
                }
                description={
                  <div style={{
                    background: msg.role === 'user' ? '#e6f7ff' : '#f6ffed',
                    padding: '8px 12px',
                    borderRadius: '8px',
                    maxWidth: '80%'
                  }}>
                    {msg.content}
                  </div>
                }
              />
            </List.Item>
          )}
        />
        {loading && (
          <div style={{ textAlign: 'center', padding: '16px' }}>
            <Spin />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div style={{ display: 'flex' }}>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入消息..."
          onPressEnter={handleSend}
          style={{ marginRight: 8 }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={loading}
        >
          发送
        </Button>
      </div>
    </div>
  );
};

export default ChatPanel;
