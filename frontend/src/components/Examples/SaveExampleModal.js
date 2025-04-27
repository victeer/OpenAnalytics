import React, { useState } from 'react';
import { Modal, Form, Input, Select, message } from 'antd';
import exampleService from '../../services/exampleService';

const { TextArea } = Input;
const { Option } = Select;

const SaveExampleModal = ({ visible, onCancel, onSuccess, analysisData, sessionId }) => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      // 检查 sessionId
      if (!sessionId) {
        message.error('无法保存示例：缺少会话ID');
        return;
      }

      const values = await form.validateFields();
      setLoading(true);
      
      // 准备保存的数据，确保与后端 ExampleCreate 模型匹配
      const exampleData = {
        name: values.name || '',
        description: values.description || '',
        tags: Array.isArray(values.tags) ? values.tags : [],
        sessionId: sessionId,
        analysisProcess: {
          originalFile: {
            ...analysisData.originalFile,
            data_details: analysisData.originalFile.data_details,
            file_name: analysisData.originalFile.file_name
          },
          userQuery: analysisData.userQuery || '',
          process_steps: Array.isArray(analysisData.analysisProcess.process_steps) 
            ? analysisData.analysisProcess.process_steps 
            : [],
          code: analysisData.analysisProcess.code || '',
          plan: analysisData.analysisProcess.plan || '',
          result: analysisData.analysisProcess.finalResult?.output || '',
          errors: Array.isArray(analysisData.analysisProcess.errors) 
            ? analysisData.analysisProcess.errors 
            : []
        }
      };

      // 添加调试信息
      console.log('准备发送的数据:', JSON.stringify(exampleData, null, 2));
      console.log('sessionId:', sessionId);
      console.log('analysisData:', analysisData);

      await exampleService.saveExample(exampleData);
      message.success('示例保存成功');
      onSuccess();
    } catch (error) {
      console.error('保存示例失败:', error);
      message.error('保存示例失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="保存示例"
      visible={visible}
      onCancel={onCancel}
      onOk={handleSubmit}
      confirmLoading={loading}
    >
      <Form form={form} layout="vertical">
        <Form.Item
          name="name"
          label="示例名称"
          rules={[{ required: true, message: '请输入示例名称' }]}
        >
          <Input placeholder="请输入示例名称" />
        </Form.Item>
        <Form.Item
          name="description"
          label="示例描述"
          rules={[{ required: true, message: '请输入示例描述' }]}
        >
          <TextArea rows={4} placeholder="请输入示例描述" />
        </Form.Item>
        <Form.Item
          name="tags"
          label="示例标签"
          rules={[{ required: true, message: '请选择示例标签' }]}
        >
          <Select
            mode="multiple"
            placeholder="请选择示例标签"
            style={{ width: '100%' }}
          >
            <Option value="data_analysis">数据分析</Option>
            <Option value="data_cleaning">数据清洗</Option>
            <Option value="data_visualization">数据可视化</Option>
            <Option value="statistical_analysis">统计分析</Option>
            <Option value="machine_learning">机器学习</Option>
            <Option value="natural_language">自然语言处理</Option>
          </Select>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default SaveExampleModal; 