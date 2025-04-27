import React from 'react';
import { Card, Typography, Tag, Space, Button, Popconfirm, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';
import { DeleteOutlined } from '@ant-design/icons';
import exampleService from '../../services/exampleService';
import config from '../../config';

const { Title, Text } = Typography;

const tagColors = {
  'data_analysis': 'blue',
  'data_cleaning': 'green',
  'data_visualization': 'purple',
  'statistical_analysis': 'orange',
  'machine_learning': 'red',
  'natural_language': 'cyan'
};

const tagLabels = {
  'data_analysis': '数据分析',
  'data_cleaning': '数据清洗',
  'data_visualization': '数据可视化',
  'statistical_analysis': '统计分析',
  'machine_learning': '机器学习',
  'natural_language': '自然语言处理'
};

const ExampleCard = ({ example, onDelete }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    const basePath = config.NAVIGATION.BASE_PATH;
    const examplePath = basePath === '/' ? `/examples/${example.id}` : `${basePath}/examples/${example.id}`;
    navigate(examplePath);
  };

  const handleDelete = async (e) => {
    e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击
    try {
      await exampleService.deleteExample(example.id);
      message.success('示例删除成功');
      onDelete(example.id);
    } catch (error) {
      message.error('删除示例失败: ' + error.message);
    }
  };

  return (
    <Card
      hoverable
      onClick={handleClick}
      style={{ height: '100%' }}
      cover={
        <div style={{ 
          height: 160, 
          background: '#f0f2f5',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Text type="secondary">示例预览图</Text>
        </div>
      }
      actions={[
        <Popconfirm
          title="确定要删除这个示例吗？"
          onConfirm={handleDelete}
          onCancel={(e) => e.stopPropagation()}
          okText="确定"
          cancelText="取消"
        >
          <Button 
            type="text" 
            danger 
            icon={<DeleteOutlined />}
            onClick={(e) => e.stopPropagation()}
          >
            删除
          </Button>
        </Popconfirm>
      ]}
    >
      <Card.Meta
        title={
          <Title level={4} ellipsis={{ rows: 1 }}>
            {example.name}
          </Title>
        }
        description={
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <Text type="secondary" ellipsis={{ rows: 2 }}>
              {example.description}
            </Text>
            <Space wrap>
              {(example.tags || []).map(tag => (
                <Tag key={tag} color={tagColors[tag] || 'blue'}>
                  {tagLabels[tag] || tag}
                </Tag>
              ))}
            </Space>
            <Text type="secondary">
              {formatDistanceToNow(new Date(example.createdAt), { 
                addSuffix: true,
                locale: zhCN 
              })}
            </Text>
          </Space>
        }
      />
    </Card>
  );
};

export default ExampleCard; 