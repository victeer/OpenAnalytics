import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, List, Button, message, Popconfirm } from 'antd';
import { StarOutlined, DeleteOutlined } from '@ant-design/icons';
import axios from 'axios';
import config from '../../config';

const { TextArea } = Input;
const API_BASE_URL = config.API.BASE_URL;

const CommonQueries = ({ sessionId, onSelectQuery }) => {
  const [queries, setQueries] = useState([]);
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (sessionId) {
      loadQueries();
    }
  }, [sessionId]);

  const loadQueries = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/analysis/common-queries/${sessionId}`);
      setQueries(response.data.queries);
    } catch (error) {
      message.error('加载常用查询失败: ' + error.message);
    }
  };

  const handleSaveQuery = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      
      await axios.post(
        `${API_BASE_URL}/analysis/common-queries/${sessionId}?query=${encodeURIComponent(values.query)}&name=${encodeURIComponent(values.name || '')}`
      );
      
      message.success('查询保存成功');
      setSaveModalVisible(false);
      form.resetFields();
      loadQueries();
    } catch (error) {
      message.error('保存查询失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteQuery = async (query) => {
    try {
      await axios.delete(`${API_BASE_URL}/analysis/common-queries/${sessionId}?query=${encodeURIComponent(query)}`);
      message.success('查询删除成功');
      loadQueries();
    } catch (error) {
      message.error('删除查询失败: ' + error.message);
    }
  };

  return (
    <div>
      <Button
        type="primary"
        icon={<StarOutlined />}
        onClick={() => setSaveModalVisible(true)}
        style={{ marginBottom: 16 }}
      >
        保存当前查询
      </Button>

      <List
        dataSource={queries}
        renderItem={item => (
          <List.Item
            actions={[
              <Button type="link" onClick={() => onSelectQuery(item.query)}>
                使用
              </Button>,
              <Popconfirm
                title="确定要删除这个查询吗？"
                onConfirm={() => handleDeleteQuery(item.query)}
                okText="确定"
                cancelText="取消"
              >
                <Button type="link" danger icon={<DeleteOutlined />}>
                  删除
                </Button>
              </Popconfirm>
            ]}
          >
            <List.Item.Meta
              title={item.name}
              description={item.query}
            />
          </List.Item>
        )}
      />

      <Modal
        title="保存常用查询"
        open={saveModalVisible}
        onCancel={() => setSaveModalVisible(false)}
        onOk={handleSaveQuery}
        confirmLoading={loading}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="查询名称"
            rules={[{ required: true, message: '请输入查询名称' }]}
          >
            <Input placeholder="请输入查询名称" />
          </Form.Item>
          <Form.Item
            name="query"
            label="查询内容"
            rules={[{ required: true, message: '请输入查询内容' }]}
          >
            <TextArea rows={4} placeholder="请输入查询内容" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default CommonQueries; 