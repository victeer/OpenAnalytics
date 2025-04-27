import React, { useState, useEffect } from 'react';
import { Card, Table, Typography, Switch, Space, message, Input, Button, Spin, Timeline, Alert, Tabs } from 'antd';
import { RobotOutlined, CodeOutlined, CheckCircleOutlined, ClockCircleOutlined, SaveOutlined, StarOutlined } from '@ant-design/icons';
import axios from 'axios';
import './index.css';
import config from '../../config';
import { getSessionId } from '../../utils/session';
import ProcessSteps from './ProcessSteps';
import SaveExampleModal from '../Examples/SaveExampleModal';
import CommonQueries from './CommonQueries';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;

// 使用配置文件中的API基础URL
const API_BASE_URL = config.API.BASE_URL;

const Analysis = ({ fileInfo, externalSessionId }) => {
  const [expertMode, setExpertMode] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [sessionId, setSessionId] = useState(externalSessionId || getSessionId());
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [activeTab, setActiveTab] = useState('1');

  // 当外部会话ID变化时更新
  useEffect(() => {
    if (externalSessionId && externalSessionId !== sessionId) {
      console.log('使用外部提供的会话ID:', externalSessionId);
      setSessionId(externalSessionId);
    }
  }, [externalSessionId]);

  // 只有在没有外部会话ID时才创建新会话
  useEffect(() => {
    // 如果已有会话ID，不创建新会话
    if (sessionId) {
      console.log('使用现有会话ID:', sessionId);
      return;
    }

    const createSession = async () => {
      try {
        const response = await axios.post(`${API_BASE_URL}/analysis/sessions`);
        if (response.data && response.data.session_id) {
          const newSessionId = response.data.session_id;
          setSessionId(newSessionId);
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

    // 组件卸载时不再自动删除会话
  }, []);

  const handleAnalysis = async () => {
    if (!fileInfo) {
      message.warning('请先上传数据文件');
      return;
    }

    if (!query.trim()) {
      message.warning('请输入分析需求');
      return;
    }

    if (!sessionId) {
      message.error('会话未创建，请刷新页面重试');
      return;
    }

    console.log('开始分析:', query.trim());
    console.log('使用会话ID:', sessionId);

    setLoading(true);
    try {
      // 发送分析请求（不需要单独调用load接口，因为文件已在上传时加载）
      const response = await axios.post(`${API_BASE_URL}/analysis/analyze/${sessionId}`, {
        query: query.trim()
      });

      console.log('分析响应:', response.data);

      if (response.data.status === 'success') {
        setAnalysisResult(response.data);
        setAnalysisHistory(prev => [...prev, {
          query: query.trim(),
          result: response.data,
          timestamp: new Date().toLocaleString()
        }]);
        setQuery('');
        // 调用handleAnalysisSuccess保存分析数据
        handleAnalysisSuccess({
          fileInfo: fileInfo,
          query: query.trim(),
          plan: response.data.analysis_plan,
          code: response.data.analysis_code,
          errors: response.data.process_steps?.filter(step => step.type === 'error'),
          finalCode: response.data.analysis_code,
          result: response.data.result,
          charts: response.data.result?.type === 'image' ? [response.data.result] : [],
          process_steps: response.data.process_steps || []
        });
      } else {
        // 即使有错误也显示结果，因为错误信息中包含有用的调试信息
        setAnalysisResult(response.data);
        setAnalysisHistory(prev => [...prev, {
          query: query.trim(),
          result: response.data,
          timestamp: new Date().toLocaleString()
        }]);
        setQuery('');
        message.error('分析失败：' + response.data.message);
      }
    } catch (error) {
      console.error('分析错误:', error);
      console.error('错误详情:', error.response?.data || error.message);
      message.error('分析失败：' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleAnalysisSuccess = (data) => {
    setAnalysisData({
      originalFile: {
        ...data.fileInfo,
        data_details: data.fileInfo.data_details
      },
      userQuery: data.query,
      analysisProcess: {
        plan: data.plan,
        code: data.code,
        errors: data.errors,
        process_steps: data.process_steps || [],
        finalResult: {
          code: data.finalCode,
          output: data.result,
          charts: data.charts
        }
      }
    });
  };

  const handleSaveSuccess = () => {
    setSaveModalVisible(false);
  };

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

  const renderResult = (result) => {
    if (!result) return null;

    // 检查是否有用户通知（多次尝试失败的情况）
    const hasUserNotice = result.user_notice;
    // 检查是否有处理步骤
    const hasProcessSteps = result.process_steps && result.process_steps.length > 0;

    return (
      <div className="analysis-result">
        {/* 显示用户通知（如果有） */}
        {hasUserNotice && (
          <Card title="分析失败通知" style={{ marginBottom: 16 }}>
            <Alert 
              message="多次尝试后仍未成功" 
              description={result.user_notice} 
              type="warning" 
              showIcon 
            />
          </Card>
        )}

        {/* 显示分析计划 */}
        {!expertMode && result.analysis_plan && (
          <Card title="分析计划" style={{ marginBottom: 16 }}>
            <Paragraph>{result.analysis_plan}</Paragraph>
          </Card>
        )}
        
        {/* 专家模式下显示处理步骤 */}
        {expertMode && hasProcessSteps && (
          <ProcessSteps steps={result.process_steps} />
        )}
        
        {/* 专家模式下显示最终代码 */}
        {expertMode && !hasProcessSteps && result.analysis_code && (
          <Card title="生成代码" style={{ marginBottom: 16 }}>
            <pre>{result.analysis_code}</pre>
          </Card>
        )}
        
        {/* 显示分析结果（如果有） */}
        {result.result && (
          <Card title="分析结果">
            {result.result.type === 'dataframe' ? (
              <>
                <Table
                  dataSource={result.result.preview_data}
                  columns={result.result.columns.map(col => ({
                    title: col,
                    dataIndex: col,
                    key: col
                  }))}
                  pagination={{ pageSize: 10 }}
                  scroll={{ x: true }}
                />
                <div style={{ marginTop: 16, textAlign: 'right' }}>
                  <Text type="secondary" style={{ marginRight: 16 }}>
                    共 {result.result.total_rows} 行数据，当前显示前30行
                  </Text>
                  {result.result.download_id && (
                    <Button
                      type="link"
                      href={`${API_BASE_URL}/analysis/download/${result.result.download_id}`}
                      download
                    >
                      下载完整数据
                    </Button>
                  )}
                </div>
              </>
            ) : result.result.type === 'dict' ? (
              <pre>{JSON.stringify(result.result.data, null, 2)}</pre>
            ) : result.result.type === 'table' ? (
              <Table
                dataSource={result.result.data}
                columns={result.result.columns.map(col => ({
                  title: col,
                  dataIndex: col,
                  key: col
                }))}
                pagination={{ pageSize: 10 }}
                scroll={{ x: true }}
              />
            ) : (
              <Paragraph>{result.result.data}</Paragraph>
            )}
          </Card>
        )}
      </div>
    );
  };

  return (
    <div className="analysis-container">
      <Space direction="vertical" style={{ width: '100%' }}>
        <div className="mode-switch">
          <Switch
            checked={expertMode}
            onChange={setExpertMode}
            checkedChildren="专家模式"
            unCheckedChildren="小白模式"
          />
        </div>

        <Card title="分析需求">
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={[
              {
                key: '1',
                label: '新建查询',
                children: (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <TextArea
                      value={query}
                      onChange={e => setQuery(e.target.value)}
                      placeholder="请输入您的分析需求，例如：计算各列的平均值、统计缺失值数量等"
                      autoSize={{ minRows: 3, maxRows: 6 }}
                    />
                    <Button type="primary" onClick={handleAnalysis} loading={loading}>
                      开始分析
                    </Button>
                  </Space>
                )
              },
              {
                key: '2',
                label: '常用查询',
                children: (
                  <CommonQueries
                    sessionId={sessionId}
                    onSelectQuery={(selectedQuery) => {
                      setQuery(selectedQuery);
                      setActiveTab('1');
                    }}
                  />
                )
              }
            ]}
          />
        </Card>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
            <Paragraph style={{ marginTop: 16 }}>正在分析中，请稍候...</Paragraph>
          </div>
        ) : analysisResult ? (
          renderResult(analysisResult)
        ) : null}

        {analysisHistory.length > 0 && (
          <Card title="分析历史">
            <Timeline>
              {analysisHistory.map((item, index) => (
                <Timeline.Item
                  key={index}
                  dot={<ClockCircleOutlined style={{ fontSize: '16px' }} />}
                >
                  <Card size="small">
                    <Paragraph>
                      <Text strong>需求：</Text> {item.query}
                    </Paragraph>
                    <Paragraph>
                      <Text strong>时间：</Text> {item.timestamp}
                    </Paragraph>
                    <Paragraph>
                      <Text strong>状态：</Text> 
                      {item.result.status === 'success' ? 
                        <Text type="success">成功</Text> : 
                        <Text type="danger">失败</Text>
                      }
                    </Paragraph>
                    <Button
                      type="link"
                      onClick={() => setAnalysisResult(item.result)}
                    >
                      查看详情
                    </Button>
                  </Card>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        )}

        {analysisData && (
          <Space style={{ marginTop: 16 }}>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={() => setSaveModalVisible(true)}
            >
              保存为示例
            </Button>
          </Space>
        )}
      </Space>

      <SaveExampleModal
        visible={saveModalVisible}
        onCancel={() => setSaveModalVisible(false)}
        onSuccess={handleSaveSuccess}
        analysisData={analysisData}
        sessionId={sessionId}
      />
    </div>
  );
};

export default Analysis; 