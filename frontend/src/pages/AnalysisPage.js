import React, { useState, useEffect } from 'react';
import { Upload, Button, Input, message, Card, Space } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axios from 'axios';
import AnalysisResult from '../components/AnalysisResult';
import config from '../config';
import { getSessionId, saveSessionId } from '../utils/session';

// 使用配置文件中的API基础URL
const API_BASE_URL = config.API.BASE_URL;

const AnalysisPage = () => {
  const [sessionId, setSessionId] = useState(getSessionId());
  const [fileList, setFileList] = useState([]);
  const [dataInfo, setDataInfo] = useState(null);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [fileUploaded, setFileUploaded] = useState(false);

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

    // 组件卸载时清理工作，但不删除会话（让会话持久存在）
    return () => {
      // 可以选择不删除会话，使其在页面刷新后仍然可用
    };
  }, [sessionId]);

  // 上传文件
  const handleUpload = async (file) => {
    if (!sessionId) {
      message.error('会话未创建，请刷新页面重试');
      return false;
    }

    setUploadLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${API_BASE_URL}/analysis/upload/${sessionId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (response.data.status === 'success') {
        message.success('文件上传成功');
        setFileList([file]);
        // 直接使用上传接口返回的数据信息，不再单独调用load接口
        setDataInfo(response.data.data_info);
        setFileUploaded(true);
      } else {
        message.error(response.data.message || '文件上传失败');
        setFileUploaded(false);
      }
    } catch (error) {
      console.error('文件上传错误:', error);
      message.error('文件上传失败: ' + (error.response?.data?.detail || error.message));
      setFileUploaded(false);
    } finally {
      setUploadLoading(false);
    }
    return false;
  };

  // 执行分析
  const handleAnalyze = async () => {
    if (!sessionId) {
      message.error('会话未创建，请刷新页面重试');
      return;
    }

    if (!fileUploaded) {
      message.warning('请先上传数据文件');
      return;
    }

    if (!query) {
      message.warning('请输入分析需求');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/analysis/analyze/${sessionId}`, {
        query: query
      });
      
      if (response.data.status === 'success') {
        setResult(response.data);
      } else {
        message.error(response.data.message || '分析失败');
      }
    } catch (error) {
      console.error('分析错误:', error);
      message.error('分析失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Card title="数据分析" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Upload
            fileList={fileList}
            beforeUpload={handleUpload}
            onRemove={() => {
              setFileList([]);
              setDataInfo(null);
              setFileUploaded(false);
            }}
          >
            <Button icon={<UploadOutlined />} loading={uploadLoading}>上传数据文件</Button>
          </Upload>

          {dataInfo && (
            <Card title="数据信息" size="small">
              <pre>{dataInfo}</pre>
            </Card>
          )}

          <Input.TextArea
            placeholder="请输入分析需求"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
          />

          <Button
            type="primary"
            onClick={handleAnalyze}
            loading={loading}
            disabled={!fileUploaded}
          >
            开始分析
          </Button>
        </Space>
      </Card>

      {result && <AnalysisResult result={result} />}
    </div>
  );
};

export default AnalysisPage; 