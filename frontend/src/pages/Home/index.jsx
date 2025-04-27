import React, { useState, useEffect } from 'react';
import { Layout, Card, Table, Typography, Tabs, message } from 'antd';
import FileUpload from '../../components/FileUpload';
import Chat from '../../components/Chat';
import Analysis from '../../components/Analysis';
import axios from 'axios';
import config from '../../config';
import { getSessionId, saveSessionId } from '../../utils/session';
import './index.css';

const { Header, Content } = Layout;
const { Title } = Typography;
const { TabPane } = Tabs;

// 使用配置文件中的API基础URL
const API_BASE_URL = config.API.BASE_URL;

const Home = () => {
  const [fileInfo, setFileInfo] = useState(null);
  const [sessionId, setSessionId] = useState(getSessionId());

  // 创建会话
  useEffect(() => {
    const createSession = async () => {
      // 如果已有会话ID，则不重新创建
      if (sessionId) {
        console.log('使用已存在的会话:', sessionId);
        return;
      }

      try {
        // 使用正确的创建会话API
        const response = await axios.post(`${API_BASE_URL}/analysis/sessions`);
        if (response.data && response.data.session_id) {
          const newSessionId = response.data.session_id;
          setSessionId(newSessionId);
          saveSessionId(newSessionId);
          console.log('会话创建成功:', newSessionId);
        } else {
          message.error('创建会话失败');
        }
      } catch (error) {
        console.error('创建会话错误:', error);
        message.error('创建会话失败: ' + (error.response?.data?.detail || error.message));
      }
    };
    createSession();
  }, [sessionId]);

  const handleUploadSuccess = (info) => {
    setFileInfo(info);
  };

  const columns = [
    {
      title: '属性',
      dataIndex: 'property',
      key: 'property',
    },
    {
      title: '值',
      dataIndex: 'value',
      key: 'value',
    },
  ];

  const data = fileInfo ? [
    { property: '文件名', value: fileInfo.file_name || '未知' },
    { property: '行数', value: fileInfo.rows || '未知' },
    { property: '列数', value: fileInfo.columns || '未知' },
    { property: '列名', value: (fileInfo.column_names || []).join(', ') },
  ] : [];

  return (
    <Layout className="layout">
      <Header className="header">
        <Title level={3} style={{ color: 'white', margin: 0 }}>智能数据分析平台</Title>
      </Header>
      <Content className="content">
        <Tabs defaultActiveKey="1">
          <TabPane tab="数据分析" key="1">
            <Card title="数据文件" style={{ marginBottom: '20px' }}>
              <FileUpload onUploadSuccess={handleUploadSuccess} sessionId={sessionId} />
              {fileInfo && (
                <Table 
                  columns={columns} 
                  dataSource={data} 
                  pagination={false} 
                  className="info-table"
                  size="small"
                  style={{ marginTop: '20px' }}
                />
              )}
            </Card>
            {fileInfo && <Analysis fileInfo={fileInfo} externalSessionId={sessionId} />}
          </TabPane>
          <TabPane tab="智能对话" key="2">
            <Chat />
          </TabPane>
        </Tabs>
      </Content>
    </Layout>
  );
};

export default Home; 