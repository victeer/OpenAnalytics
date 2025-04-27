import React, { useState, useEffect } from 'react';
import { Card, Button, Typography, message, Divider } from 'antd';
import { getSessionId, clearSessionId } from '../../utils/session';
import axios from 'axios';
import config from '../../config';

const { Text, Title, Paragraph } = Typography;
const API_BASE_URL = config.API.BASE_URL;

const SessionInfo = ({ onSessionChange }) => {
  const [sessionId, setSessionId] = useState(getSessionId());
  const [sessionInfo, setSessionInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  // 获取会话信息
  const fetchSessionInfo = async () => {
    if (!sessionId) {
      setSessionInfo(null);
      return;
    }

    setLoading(true);
    try {
      // 尝试获取会话信息
      const response = await axios.get(`${API_BASE_URL}/analysis/sessions/${sessionId}`);
      setSessionInfo(response.data);
    } catch (error) {
      console.error('获取会话信息失败:', error);
      setSessionInfo({ error: '无法获取会话信息' });
    } finally {
      setLoading(false);
    }
  };

  // 创建新会话
  const createNewSession = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/analysis/sessions`);
      if (response.data && response.data.session_id) {
        const newSessionId = response.data.session_id;
        localStorage.setItem('analysis_session_id', newSessionId);
        setSessionId(newSessionId);
        message.success('新会话创建成功: ' + newSessionId);
        if (onSessionChange) {
          onSessionChange(newSessionId);
        }
      } else {
        message.error('创建会话失败');
      }
    } catch (error) {
      console.error('创建会话错误:', error);
      message.error('创建会话失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // 清除会话
  const clearSession = () => {
    clearSessionId();
    setSessionId(null);
    setSessionInfo(null);
    message.info('会话已清除');
    if (onSessionChange) {
      onSessionChange(null);
    }
  };

  useEffect(() => {
    fetchSessionInfo();
  }, [sessionId]);

  return (
    <Card title="会话信息调试" size="small">
      <Typography>
        <Paragraph>
          <Text strong>当前会话ID: </Text>
          {sessionId ? (
            <Text code>{sessionId}</Text>
          ) : (
            <Text type="warning">未设置会话</Text>
          )}
        </Paragraph>

        <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
          <Button size="small" onClick={fetchSessionInfo} loading={loading}>
            刷新信息
          </Button>
          <Button size="small" onClick={createNewSession} loading={loading} type="primary">
            创建新会话
          </Button>
          <Button size="small" onClick={clearSession} danger>
            清除会话
          </Button>
        </div>

        {sessionInfo && (
          <>
            <Divider>会话详情</Divider>
            <pre style={{ maxHeight: '200px', overflow: 'auto' }}>
              {JSON.stringify(sessionInfo, null, 2)}
            </pre>
          </>
        )}
      </Typography>
    </Card>
  );
};

export default SessionInfo; 