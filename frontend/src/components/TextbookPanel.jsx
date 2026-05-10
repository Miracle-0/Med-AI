import React, { useState, useEffect } from 'react';
import { Upload, List, Button, message, Tag } from 'antd';
import { UploadOutlined, DeleteOutlined, ReloadOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { textbookAPI } from '../services/api';

const TextbookPanel = ({ onSelect, selected }) => {
  const [textbooks, setTextbooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [parsing, setParsing] = useState({});

  useEffect(() => {
    loadTextbooks();
  }, []);

  const loadTextbooks = async () => {
    setLoading(true);
    try {
      const res = await textbookAPI.list();
      setTextbooks(res.data);
    } catch (error) {
      message.error('加载教材列表失败');
    }
    setLoading(false);
  };

  const handleUpload = async (file) => {
    try {
      await textbookAPI.upload(file);
      message.success('上传成功');
      loadTextbooks();
    } catch (error) {
      const detail = error.response?.data?.detail || error.message;
      message.error(`上传失败: ${detail}`);
    }
    return false;
  };

  const handleParse = async (id) => {
    setParsing(prev => ({ ...prev, [id]: true }));
    try {
      const res = await textbookAPI.parse(id);
      message.success(`解析完成，共 ${res.data.chapters_count} 个章节`);
      loadTextbooks();
    } catch (error) {
      const detail = error.response?.data?.detail || error.message;
      message.error(`解析失败: ${detail}`);
    }
    setParsing(prev => ({ ...prev, [id]: false }));
  };

  const handleDelete = async (id) => {
    try {
      await textbookAPI.delete(id);
      message.success('删除成功');
      loadTextbooks();
      if (selected === id) {
        onSelect(null);
      }
    } catch (error) {
      message.error('删除失败');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'parsing': return 'orange';
      case 'uploaded': return 'blue';
      case 'failed': return 'red';
      default: return 'default';
    }
  };

  return (
    <div>
      <h3 style={{ marginBottom: 16 }}>教材管理</h3>
      <Upload beforeUpload={handleUpload} showUploadList={false}>
        <Button icon={<UploadOutlined />} style={{ marginBottom: 16, width: '100%' }}>
          上传教材
        </Button>
      </Upload>
      <Button
        icon={<ReloadOutlined />}
        onClick={loadTextbooks}
        style={{ marginBottom: 16, width: '100%' }}
      >
        刷新列表
      </Button>
      <List
        loading={loading}
        dataSource={textbooks}
        renderItem={(item) => (
          <List.Item
            style={{
              cursor: 'pointer',
              background: selected === item.textbook_id ? '#e6f7ff' : 'transparent',
              padding: '8px',
              borderRadius: '4px'
            }}
            onClick={() => onSelect(item.textbook_id)}
            actions={[
              item.parse_status === 'uploaded' || item.parse_status === 'failed' ? (
                <Button
                  type="text"
                  icon={<PlayCircleOutlined />}
                  loading={parsing[item.textbook_id]}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleParse(item.textbook_id);
                  }}
                >
                  解析
                </Button>
              ) : null,
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(item.textbook_id);
                }}
              />
            ].filter(Boolean)}
          >
            <List.Item.Meta
              title={item.title}
              description={
                <div>
                  <div>{item.filename}</div>
                  <Tag color={getStatusColor(item.parse_status)}>
                    {item.parse_status}
                  </Tag>
                  {item.total_chars > 0 && (
                    <span style={{ marginLeft: 8 }}>{item.total_chars} 字</span>
                  )}
                </div>
              }
            />
          </List.Item>
        )}
      />
    </div>
  );
};

export default TextbookPanel;
