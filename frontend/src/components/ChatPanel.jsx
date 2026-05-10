import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, message } from 'antd';
import { SendOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';
import { chatAPI } from '../services/api';

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => { loadHistory(); }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadHistory = async () => {
    try {
      const res = await chatAPI.getHistory();
      setMessages(res.data);
    } catch (e) {}
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);
    try {
      const res = await chatAPI.sendMessage(userMsg);
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
    } catch (e) {
      message.error('发送失败');
    }
    setLoading(false);
  };

  const renderMessage = (msg, idx) => {
    const isUser = msg.role === 'user';
    return (
      <div
        key={idx}
        style={{
          display: 'flex', gap: 10, marginBottom: 16,
          flexDirection: isUser ? 'row-reverse' : 'row',
          animation: 'fadeIn 0.3s ease',
        }}
      >
        {/* Avatar */}
        <div style={{
          width: 30, height: 30, borderRadius: 10, flexShrink: 0,
          background: isUser
            ? 'linear-gradient(135deg, var(--accent), var(--accent-dim))'
            : 'linear-gradient(135deg, rgba(96,165,250,0.2), rgba(96,165,250,0.1))',
          border: isUser ? 'none' : '1px solid rgba(96,165,250,0.2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 13,
        }}>
          {isUser
            ? <UserOutlined style={{ color: 'var(--bg-deep)' }} />
            : <RobotOutlined style={{ color: '#60a5fa' }} />}
        </div>

        {/* Bubble */}
        <div style={{
          maxWidth: '75%', padding: '10px 14px',
          borderRadius: isUser ? '12px 4px 12px 12px' : '4px 12px 12px 12px',
          background: isUser
            ? 'linear-gradient(135deg, rgba(240,160,48,0.2), rgba(240,160,48,0.08))'
            : 'var(--bg-glass)',
          border: `1px solid ${isUser ? 'rgba(240,160,48,0.2)' : 'rgba(255,255,255,0.06)'}`,
          fontSize: 13, lineHeight: 1.7,
          color: 'var(--text-primary)',
          whiteSpace: 'pre-wrap',
        }}>
          {msg.content}
        </div>
      </div>
    );
  };

  return (
    <div style={{
      padding: '16px 16px 24px',
      display: 'flex', flexDirection: 'column',
      height: 'calc(100vh - 120px)',
    }}>
      {/* Messages area */}
      <div style={{
        flex: 1, overflow: 'auto', marginBottom: 16,
        paddingRight: 4,
      }}>
        {messages.length === 0 && !loading && (
          <div style={{
            display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            height: '100%', gap: 12, opacity: 0.4,
          }}>
            <RobotOutlined style={{ fontSize: 28, color: 'var(--text-muted)' }} />
            <span style={{
              fontFamily: 'var(--font-display)', fontSize: 13,
              color: 'var(--text-muted)',
            }}>
              开始对话
            </span>
            <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              我可以回答关于教材内容的问题
            </span>
          </div>
        )}

        {messages.map((msg, idx) => renderMessage(msg, idx))}

        {loading && (
          <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
            <div style={{
              width: 30, height: 30, borderRadius: 10, flexShrink: 0,
              background: 'linear-gradient(135deg, rgba(96,165,250,0.2), rgba(96,165,250,0.1))',
              border: '1px solid rgba(96,165,250,0.2)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <RobotOutlined style={{ color: '#60a5fa' }} />
            </div>
            <div style={{
              padding: '12px 18px', borderRadius: '4px 12px 12px 12px',
              background: 'var(--bg-glass)',
              border: '1px solid rgba(255,255,255,0.06)',
              display: 'flex', gap: 6, alignItems: 'center',
            }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 6, height: 6, borderRadius: 3,
                  background: 'var(--accent)',
                  opacity: 0.4,
                  animation: `pulse 1.2s infinite ${i * 0.2}s`,
                }} />
              ))}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div style={{
        display: 'flex', gap: 8,
        padding: '12px', borderRadius: 'var(--radius)',
        background: 'var(--bg-glass)',
        border: '1px solid var(--border-subtle)',
      }}>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="输入消息..."
          onPressEnter={handleSend}
          bordered={false}
          style={{
            background: 'transparent',
            color: 'var(--text-primary)',
          }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={loading}
          style={{ borderRadius: 8 }}
        />
      </div>
    </div>
  );
};

export default ChatPanel;
