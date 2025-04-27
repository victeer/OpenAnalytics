import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { Card, Typography, message, Layout, Menu } from 'antd';
import { RobotOutlined, BarChartOutlined, BookOutlined } from '@ant-design/icons';
import Analysis from './components/Analysis';
import Examples from './pages/Examples';
import ExampleDetail from './pages/ExampleDetail';
import FileUpload from './components/FileUpload';
import Chat from './components/Chat';
import axios from 'axios';
import config from './config';
import { getSessionId, saveSessionId } from './utils/session';

const { Title } = Typography;
const { Header, Content } = Layout;
const API_BASE_URL = config.API.BASE_URL;

function App() {
  const [fileInfo, setFileInfo] = useState(null);
  const [sessionId, setSessionId] = useState(getSessionId());
  const location = useLocation();
  const navigate = useNavigate();

  // 创建会话
  useEffect(() => {
    const createSession = async () => {
      if (sessionId) {
        console.log('使用已存在的会话:', sessionId);
        return;
      }

      try {
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

  return (
    <Layout className="layout">
      <Header style={{ background: '#fff', padding: '0 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
          <Title level={3} style={{ margin: 0, marginRight: '48px' }}>智能数据分析平台</Title>
          <Menu mode="horizontal" selectedKeys={[location.pathname]}>
            <Menu.Item key={config.NAVIGATION.getPath('')} icon={<BarChartOutlined />}>
              <Link to={config.NAVIGATION.getPath('').replace(/^\/+/, '')} replace>数据分析</Link>
            </Menu.Item>
            <Menu.Item key={config.NAVIGATION.getPath('/chat')} icon={<RobotOutlined />}>
              <Link to={config.NAVIGATION.getPath('/chat').replace(/^\/+/, '')} replace>智能对话</Link>
            </Menu.Item>
            <Menu.Item key={config.NAVIGATION.getPath('/examples')} icon={<BookOutlined />}>
              <Link to={config.NAVIGATION.getPath('/examples').replace(/^\/+/, '')} replace>示例展示</Link>
            </Menu.Item>
          </Menu>
        </div>
      </Header>
      <Content style={{ padding: '24px' }}>
        <Routes>
          <Route path={config.NAVIGATION.getPath('')} element={
            <>
              <Card title="数据文件" style={{ marginBottom: '20px' }}>
                <FileUpload onUploadSuccess={handleUploadSuccess} sessionId={sessionId} />
              </Card>
              {fileInfo && <Analysis fileInfo={fileInfo} externalSessionId={sessionId} />}
            </>
          } />
          <Route path={config.NAVIGATION.getPath('/chat')} element={<Chat />} />
          <Route path={config.NAVIGATION.getPath('/examples')} element={<Examples />} />
          <Route path={config.NAVIGATION.getPath('/examples/:id')} element={<ExampleDetail />} />
        </Routes>
      </Content>
    </Layout>
  );
}

export default App; 