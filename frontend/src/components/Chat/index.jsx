import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, List, Avatar, message } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import axios from 'axios';
import './index.css';
import config from '../../config';

const { TextArea } = Input;

// 使用配置文件中的API基础URL
const API_BASE_URL = config.API.BASE_URL;

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [sessionId, setSessionId] = useState(null);

  // 创建聊天会话
  useEffect(() => {
    const createSession = async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/chat/sessions`);
        if (response.data && response.data.session_id) {
          setSessionId(response.data.session_id);
          console.log('聊天会话创建成功:', response.data.session_id);
        } else {
          message.error('创建聊天会话失败');
        }
      } catch (error) {
        console.error('创建聊天会话错误:', error);
        message.error('创建聊天会话失败: ' + (error.response?.data?.detail || error.message));
      }
    };
    createSession();

    return () => {
      if (sessionId) {
        axios.delete(`${API_BASE_URL}/chat/sessions/${sessionId}`).catch(() => {});
      }
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    if (!sessionId) {
      message.error('聊天会话未创建，请刷新页面重试');
      return;
    }

    const userMessage = inputValue.trim();
    setInputValue('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat/send`, {
        message: userMessage,
        session_id: sessionId
      });

      if (response.data.status === 'success') {
        setMessages(prev => [...prev, { role: 'assistant', content: response.data.response }]);
      } else {
        message.error('发送消息失败');
      }
    } catch (error) {
      console.error('发送消息错误:', error);
      message.error('发送消息失败：' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    if (!sessionId) {
      message.error('聊天会话未创建，请刷新页面重试');
      return;
    }

    try {
      await axios.post(`${API_BASE_URL}/chat/clear/${sessionId}`);
      setMessages([]);
      message.success('对话历史已清空');
    } catch (error) {
      console.error('清空历史错误:', error);
      message.error('清空历史失败：' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        <List
          dataSource={messages}
          renderItem={item => (
            <List.Item>
              <List.Item.Meta
                avatar={
                  <Avatar
                    icon={item.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{ backgroundColor: item.role === 'user' ? '#1890ff' : '#52c41a' }}
                  />
                }
                title={item.role === 'user' ? '用户' : 'AI助手'}
                description={item.content}
              />
            </List.Item>
          )}
        />
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input">
        <TextArea
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          placeholder="请输入消息..."
          autoSize={{ minRows: 2, maxRows: 6 }}
          onPressEnter={handleSend}
        />
        <div className="chat-buttons">
          <Button type="primary" onClick={handleSend} loading={loading}>
            发送
          </Button>
          <Button onClick={handleClear}>
            清空历史
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Chat; 