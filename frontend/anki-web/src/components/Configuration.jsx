import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Select, Switch, message, Space, Alert, Divider } from 'antd';
import { SaveOutlined, ExperimentOutlined, ReloadOutlined } from '@ant-design/icons';
import { configAPI } from '../services/api';

const { Option } = Select;

const Configuration = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [configStatus, setConfigStatus] = useState('unknown');
  const [error, setError] = useState(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      setLoading(true);
      setError(null);
      
      try {
        const config = await configAPI.getConfig();
        form.setFieldsValue(config);
        setConfigStatus(config.enableAI ? 'configured' : 'not_configured');
      } catch (apiError) {
        console.warn('API not available, using mock config:', apiError);
        // 使用模拟配置
        form.setFieldsValue({
          apiKey: 'your-api-key-here',
          openRouterApiKey: 'your-openrouter-api-key-here',
          apiBase: 'https://api.siliconflow.cn',
          openRouterApiBase: 'https://openrouter.ai/api/v1',
          model: 'openai/gpt-4.1-nano',
          proxy: '127.0.0.1:7890',
          eudicToken: 'your-eudic-token-here',
          eudicId: '0',
          deckName: 'anki_packager',
          enableAI: true,
        });
        setConfigStatus('configured');
      }
    } catch (err) {
      setError(err.message);
      message.error('加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (values) => {
    try {
      setLoading(true);
      await configAPI.saveConfig(values);
      message.success('配置保存成功');
      setConfigStatus(values.enableAI ? 'configured' : 'not_configured');
    } catch (err) {
      message.error(`保存配置失败: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTest = async () => {
    try {
      setLoading(true);
      await configAPI.testConfig();
      message.success('配置测试成功');
    } catch (err) {
      message.error(`配置测试失败: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return (
      <Alert
        message="加载失败"
        description={error}
        type="error"
        showIcon
        action={
          <Button size="small" danger onClick={loadConfig}>
            重试
          </Button>
        }
      />
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2>配置设置</h2>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={loadConfig}
          loading={loading}
        >
          刷新
        </Button>
      </div>
      
      <Alert
        message="配置说明"
        description="请填写以下配置信息以启用相应功能。API密钥等敏感信息请妥善保管。"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSave}
          disabled={loading}
        >
          <Form.Item
            label="启用AI功能"
            name="enableAI"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Divider orientation="left">SiliconFlow 配置</Divider>

          <Form.Item
            label="SiliconFlow API密钥"
            name="apiKey"
            rules={[{ required: true, message: '请输入API密钥' }]}
          >
            <Input.Password placeholder="请输入SiliconFlow API密钥" />
          </Form.Item>

          <Form.Item
            label="API基础地址"
            name="apiBase"
            rules={[{ required: true, message: '请输入API基础地址' }]}
          >
            <Input placeholder="https://api.siliconflow.cn" />
          </Form.Item>

          <Divider orientation="left">OpenRouter 配置</Divider>

          <Form.Item
            label="OpenRouter API密钥"
            name="openRouterApiKey"
            rules={[{ required: true, message: '请输入OpenRouter API密钥' }]}
          >
            <Input.Password placeholder="请输入OpenRouter API密钥" />
          </Form.Item>

          <Form.Item
            label="OpenRouter API地址"
            name="openRouterApiBase"
            rules={[{ required: true, message: '请输入OpenRouter API地址' }]}
          >
            <Input placeholder="https://openrouter.ai/api/v1" />
          </Form.Item>

          <Form.Item
            label="AI模型"
            name="model"
            rules={[{ required: true, message: '请选择AI模型' }]}
          >
            <Select placeholder="请选择AI模型">
              <Option value="openai/gpt-4.1-nano">GPT-4.1 Nano</Option>
              <Option value="openai/gpt-4.1-mini">GPT-4.1 Mini</Option>
              <Option value="Pro/deepseek-ai/DeepSeek-V3">DeepSeek V3</Option>
              <Option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet</Option>
              <Option value="meta-llama/llama-3.1-8b-instruct">Llama 3.1 8B</Option>
            </Select>
          </Form.Item>

          <Divider orientation="left">网络配置</Divider>

          <Form.Item
            label="代理设置"
            name="proxy"
            extra="格式：127.0.0.1:7890 或 http://127.0.0.1:7890"
          >
            <Input placeholder="127.0.0.1:7890" />
          </Form.Item>

          <Divider orientation="left">词典配置</Divider>

          <Form.Item
            label="欧路词典Token"
            name="eudicToken"
            extra="可选，用于获取欧路词典释义"
          >
            <Input.Password placeholder="请输入欧路词典Token" />
          </Form.Item>

          <Form.Item
            label="欧路词典ID"
            name="eudicId"
            extra="可选，默认为0"
          >
            <Input placeholder="0" />
          </Form.Item>

          <Divider orientation="left">输出配置</Divider>

          <Form.Item
            label="牌组名称"
            name="deckName"
            rules={[{ required: true, message: '请输入牌组名称' }]}
            extra="生成的Anki牌组名称"
          >
            <Input placeholder="anki_packager" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SaveOutlined />}
                loading={loading}
              >
                保存配置
              </Button>
              <Button
                icon={<ExperimentOutlined />}
                onClick={handleTest}
                loading={loading}
              >
                测试配置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Configuration; 