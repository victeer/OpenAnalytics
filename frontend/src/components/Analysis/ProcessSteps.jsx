import React from 'react';
import { Card, Typography, Timeline, Space, Collapse, Alert } from 'antd';
import { 
  AppstoreOutlined, 
  CodeOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  SearchOutlined,
  BulbOutlined,
  ExperimentOutlined,
  FileTextOutlined,
  WarningOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';

const { Text, Paragraph, Title } = Typography;
const { Panel } = Collapse;

// 步骤类型图标映射
const stepIcons = {
  analysis_plan: <AppstoreOutlined style={{ color: '#1890ff' }} />,
  initial_code: <CodeOutlined style={{ color: '#722ed1' }} />,
  error: <CloseCircleOutlined style={{ color: '#f5222d' }} />,
  error_analysis: <SearchOutlined style={{ color: '#fa8c16' }} />,
  info_code: <ExperimentOutlined style={{ color: '#13c2c2' }} />,
  info_result: <FileTextOutlined style={{ color: '#52c41a' }} />,
  info_error: <WarningOutlined style={{ color: '#faad14' }} />,
  fixed_code: <BulbOutlined style={{ color: '#eb2f96' }} />,
  fixed_code_fallback: <InfoCircleOutlined style={{ color: '#2f54eb' }} />,
  success: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
  user_notice: <WarningOutlined style={{ color: '#faad14' }} />,
  process_error: <CloseCircleOutlined style={{ color: '#f5222d' }} />,
};

// 步骤类型标题映射
const stepTitles = {
  analysis_plan: '分析计划',
  initial_code: '初始分析代码',
  error: '执行错误',
  error_analysis: '错误分析',
  info_code: '获取额外信息代码',
  info_result: '获取信息结果',
  info_error: '获取信息失败',
  fixed_code: '修复后的代码',
  fixed_code_fallback: '回退修复代码',
  success: '执行成功',
  user_notice: '用户通知',
  process_error: '处理错误',
};

const ProcessSteps = ({ steps }) => {
  if (!steps || steps.length === 0) {
    return null;
  }

  const renderStepContent = (step) => {
    switch (step.type) {
      case 'analysis_plan':
      case 'user_notice':
      case 'process_error':
        return <Paragraph style={{ whiteSpace: 'pre-wrap' }}>{step.content}</Paragraph>;
      
      case 'initial_code':
      case 'fixed_code':
      case 'fixed_code_fallback':
      case 'info_code':
        return <pre style={{ backgroundColor: '#f5f5f5', padding: '10px', borderRadius: '4px' }}>{step.content}</pre>;
      
      case 'error':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert message={step.content} type="error" showIcon />
            {step.traceback && (
              <Collapse ghost>
                <Panel header="错误详情" key="1">
                  <pre style={{ backgroundColor: '#fff2f0', padding: '10px', borderRadius: '4px' }}>
                    {step.traceback}
                  </pre>
                </Panel>
              </Collapse>
            )}
          </Space>
        );
      
      case 'error_analysis':
        return (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Alert 
              message={`计划: ${step.content.plan}`} 
              description={`理由: ${step.content.reason}`} 
              type="info" 
              showIcon 
            />
          </Space>
        );
      
      case 'info_result':
        return (
          <div>
            <Text strong>获取到的信息结果:</Text>
            <pre style={{ backgroundColor: '#f6ffed', padding: '10px', borderRadius: '4px' }}>
              {step.content}
            </pre>
          </div>
        );
      
      case 'info_error':
        return <Alert message={step.content} type="warning" showIcon />;
      
      case 'success':
        return <Alert message="执行成功！" type="success" showIcon />;
      
      default:
        return <Text>{JSON.stringify(step.content)}</Text>;
    }
  };

  return (
    <Card title="处理流程" style={{ marginBottom: 16 }}>
      <Timeline>
        {steps.map((step, index) => (
          <Timeline.Item
            key={index}
            dot={stepIcons[step.type] || <InfoCircleOutlined />}
          >
            <div style={{ marginBottom: 16 }}>
              <Title level={5}>
                {stepTitles[step.type] || step.type}
                {step.attempt && <Text type="secondary" style={{ fontSize: '14px', marginLeft: '8px' }}>
                  (尝试 {step.attempt})
                </Text>}
              </Title>
              {renderStepContent(step)}
            </div>
          </Timeline.Item>
        ))}
      </Timeline>
    </Card>
  );
};

export default ProcessSteps; 