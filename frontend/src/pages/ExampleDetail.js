import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, message, Spin, Typography, Space, Switch, Table, Descriptions } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import exampleService from '../services/exampleService';
import ProcessSteps from '../components/Analysis/ProcessSteps';
import config from '../config';

const { Title, Paragraph, Text } = Typography;
const API_BASE_URL = config.API.BASE_URL;

const ExampleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [example, setExample] = useState(null);
  const [expertMode, setExpertMode] = useState(false);

  useEffect(() => {
    const fetchExample = async () => {
      try {
        const data = await exampleService.getExample(id);
        setExample(data);
      } catch (error) {
        message.error('获取示例详情失败: ' + error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchExample();
  }, [id]);

  if (loading) {
    return <Spin size="large" />;
  }

  if (!example) {
    return <div>示例不存在</div>;
  }

  const renderDataframeResult = (data, columns) => {
    return (
      <Table
        dataSource={data}
        columns={columns.map(col => ({
          title: col,
          dataIndex: col,
          key: col
        }))}
        pagination={false}
        scroll={{ x: 'max-content' }}
      />
    );
  };

  const handleBack = () => {
    const basePath = config.NAVIGATION.BASE_PATH;
    const examplesPath = basePath === '/' ? '/examples' : `${basePath}/examples`;
    navigate(examplesPath);
  };

  return (
    <div className="analysis-container">
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={handleBack}
          >
            返回示例列表
          </Button>
          <Switch
            checked={expertMode}
            onChange={setExpertMode}
            checkedChildren="专家模式"
            unCheckedChildren="小白模式"
          />
        </Space>

        <Card>
          <Title level={2}>{example.name}</Title>
          <Paragraph>{example.description}</Paragraph>
          <Paragraph type="secondary">
            创建时间: {new Date(example.createdAt).toLocaleString()}
          </Paragraph>
        </Card>

        {/* 显示原始文件信息 */}
        {example.analysisProcess.originalFile && (
          <Card title="数据文件" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Descriptions column={2} size="small">
                <Descriptions.Item label="文件名">
                  <a 
                    href={`${API_BASE_URL}/examples/${example.id}/file/${encodeURIComponent(example.analysisProcess.originalFile.file_name)}`}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {example.analysisProcess.originalFile.file_name}
                  </a>
                </Descriptions.Item>
                <Descriptions.Item label="数据规模">
                  {example.analysisProcess.originalFile.data_details?.shape?.rows}行 × {example.analysisProcess.originalFile.data_details?.shape?.columns}列
                </Descriptions.Item>
                <Descriptions.Item label="列名" span={2}>
                  <div style={{ maxHeight: '100px', overflowY: 'auto', padding: '8px', background: '#f5f5f5', borderRadius: '4px' }}>
                    {example.analysisProcess.originalFile.data_details?.columns?.join(', ')}
                  </div>
                </Descriptions.Item>
              </Descriptions>

              {example.analysisProcess.originalFile.data_details?.sample_data && (
                <Card title="数据预览（前10行）" size="small">
                  <Table 
                    dataSource={example.analysisProcess.originalFile.data_details.sample_data} 
                    columns={example.analysisProcess.originalFile.data_details.columns.map(col => ({
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
              )}
            </Space>
          </Card>
        )}

        {/* 显示用户查询 */}
        {example.analysisProcess.userQuery && (
          <Card title="分析需求" style={{ marginBottom: 16 }}>
            <Paragraph>{example.analysisProcess.userQuery}</Paragraph>
          </Card>
        )}

        {/* 显示分析计划 */}
        {!expertMode && example.analysisProcess.plan && (
          <Card title="分析计划" style={{ marginBottom: 16 }}>
            <Paragraph>{example.analysisProcess.plan}</Paragraph>
          </Card>
        )}
        
        {/* 专家模式下显示处理步骤 */}
        {expertMode && example.analysisProcess.process_steps && example.analysisProcess.process_steps.length > 0 && (
          <ProcessSteps steps={example.analysisProcess.process_steps} />
        )}
        
        {/* 专家模式下显示最终代码 */}
        {expertMode && (!example.analysisProcess.process_steps || example.analysisProcess.process_steps.length === 0) && example.analysisProcess.code && (
          <Card title="生成代码" style={{ marginBottom: 16 }}>
            <pre>{example.analysisProcess.code}</pre>
          </Card>
        )}
        
        {/* 显示分析结果（如果有） */}
        {example.analysisProcess.result && (
          <Card title="分析结果" style={{ marginBottom: 16 }}>
            {example.analysisProcess.result.type === 'dataframe' && (
              renderDataframeResult(example.analysisProcess.result.preview_data, example.analysisProcess.result.columns)
            )}
            {example.analysisProcess.result.type === 'image' && (
              <img 
                src={`data:image/png;base64,${example.analysisProcess.result.data}`} 
                alt="分析结果图表"
                style={{ maxWidth: '100%' }}
              />
            )}
            {example.analysisProcess.result.type === 'dict' && (
              <pre>{JSON.stringify(example.analysisProcess.result.data, null, 2)}</pre>
            )}
            {example.analysisProcess.result.type === 'text' && (
              <Paragraph>{example.analysisProcess.result.data}</Paragraph>
            )}
          </Card>
        )}
      </Space>
    </div>
  );
};

export default ExampleDetail; 