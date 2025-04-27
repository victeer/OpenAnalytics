import React, { useState } from 'react';
import { Upload, message, Button, Table, Card, Descriptions } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import axios from 'axios';
import config from '../../config';

// 使用配置文件中的API基础URL
const API_BASE_URL = config.API.BASE_URL;

const FileUpload = ({ onUploadSuccess, sessionId }) => {
  const [loading, setLoading] = useState(false);
  const [dataDetails, setDataDetails] = useState(null);

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('文件上传开始:', file.name);
    console.log('当前会话ID:', sessionId);
    
    setLoading(true);
    try {
      let response;
      let apiPath;
      
      // 根据是否有会话ID选择适当的API
      if (sessionId) {
        // 使用分析会话上传API
        apiPath = `${API_BASE_URL}/analysis/upload/${sessionId}`;
        console.log('使用分析会话上传API:', apiPath);
        
        response = await axios.post(apiPath, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      } else {
        // 使用普通文件上传API
        apiPath = `${API_BASE_URL}/file/upload`;
        console.log('使用普通文件上传API:', apiPath);
        
        response = await axios.post(apiPath, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
      }

      console.log('文件上传响应:', response.data);
      
      if (response.data) {
        message.success('文件上传成功');
        // 处理不同API返回的格式
        let result;
        if (sessionId) {
          // 分析会话API返回格式
          console.log('处理分析会话上传响应:', response.data);
          result = {
            file_name: file.name,
            data_details: response.data.data_details
          };
          setDataDetails(response.data.data_details);
        } else {
          // 普通上传API返回格式
          console.log('处理普通上传响应:', response.data);
          result = response.data;
        }
        onUploadSuccess(result);
      }
    } catch (error) {
      console.error('文件上传错误:', error);
      console.error('错误详情:', error.response?.data || error.message);
      message.error('文件上传失败：' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
    return false; // 阻止自动上传
  };

  return (
    <div>
      <Upload
        beforeUpload={handleUpload}
        accept=".csv,.xlsx"
        showUploadList={false}
      >
        <Button icon={<UploadOutlined />} loading={loading}>
          {sessionId ? '上传分析文件' : '上传文件'}
        </Button>
      </Upload>

      {dataDetails && (
        <div style={{ marginTop: '20px' }}>
          <Card title="数据信息" size="small" style={{ marginBottom: '16px' }}>
            <Descriptions column={2} size="small">
              <Descriptions.Item label="文件名">{dataDetails.file_name}</Descriptions.Item>
              <Descriptions.Item label="数据规模">
                {dataDetails.shape.rows}行 × {dataDetails.shape.columns}列
              </Descriptions.Item>
              <Descriptions.Item label="列名" span={2}>
                <div style={{ maxHeight: '100px', overflowY: 'auto', padding: '8px', background: '#f5f5f5', borderRadius: '4px' }}>
                  {dataDetails.columns.join(', ')}
                </div>
              </Descriptions.Item>
            </Descriptions>
          </Card>

          <Card title="数据预览（前10行）" size="small">
            <Table 
              dataSource={dataDetails.sample_data} 
              columns={dataDetails.columns.map(col => ({
                title: col,
                dataIndex: col,
                key: col,
                ellipsis: true
              }))}
              pagination={false}
              size="small"
              scroll={{ x: 'max-content' }}
              style={{ marginTop: '8px' }}
            />
          </Card>
        </div>
      )}
    </div>
  );
};

export default FileUpload; 