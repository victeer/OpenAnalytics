import React, { useState, useEffect } from 'react';
import { Layout, Card, List, Typography, Space, Tag, Input, Button } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import ExampleCard from '../components/Examples/ExampleCard';
import exampleService from '../services/exampleService';

const { Header, Content } = Layout;
const { Title } = Typography;
const { Search } = Input;

const Examples = () => {
  const [examples, setExamples] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    fetchExamples();
  }, []);

  const fetchExamples = async () => {
    setLoading(true);
    try {
      const data = await exampleService.getExamples();
      setExamples(data);
    } catch (error) {
      console.error('Failed to fetch examples:', error);
    }
    setLoading(false);
  };

  const handleDelete = (exampleId) => {
    setExamples(examples.filter(example => example.id !== exampleId));
  };

  const filteredExamples = examples.filter(example => {
    if (!example) return false;
    const name = example.name || '';
    const description = example.description || '';
    return name.toLowerCase().includes(searchText.toLowerCase()) ||
           description.toLowerCase().includes(searchText.toLowerCase());
  });

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px' }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Title level={3}>分析示例</Title>
          <Search
            placeholder="搜索示例"
            allowClear
            enterButton={<SearchOutlined />}
            size="large"
            style={{ width: 300 }}
            onChange={e => setSearchText(e.target.value)}
          />
        </Space>
      </Header>
      <Content style={{ padding: '24px' }}>
        <List
          grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 4 }}
          dataSource={filteredExamples}
          loading={loading}
          renderItem={example => (
            <List.Item>
              <ExampleCard example={example} onDelete={handleDelete} />
            </List.Item>
          )}
        />
      </Content>
    </Layout>
  );
};

export default Examples; 