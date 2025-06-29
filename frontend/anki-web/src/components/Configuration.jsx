import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Select, Switch, message, Space, Alert } from 'antd';
import { SaveOutlined, ExperimentOutlined } from '@ant-design/icons';

const { Option } = Select;

const Configuration = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [configStatus, setConfigStatus] = useState('unknown');

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    // 模拟加载配置
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
  };

  const handleSave = async (values) => {
    setLoading(true);
    // 这里将来会调用后端API保存配置
    setTimeout(() => {
      setLoading(false);
      message.success('配置保存成功');
      setConfigStatus('configured');
    }, 1000);
  };

  const handleTest = async () => {
    setLoading(true);
    // 这里将来会调用后端API测试配置
    setTimeout(() => {
      setLoading(false);
      message.success('配置测试成功');
    }, 1000);
  };

  return (
    <div>
      <h2>配置设置</h2>
      
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
        >
          <Form.Item
            label="启用AI功能"
            name="enableAI"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            label="SiliconFlow API密钥"
            name="apiKey"
            rules={[{ required: true, message: '请输入API密钥' }]}
          >
            <Input.Password placeholder="请输入SiliconFlow API密钥" />
          </Form.Item>

          <Form.Item
            label="OpenRouter API密钥"
            name="openRouterApiKey"
            rules={[{ required: true, message: '请输入OpenRouter API密钥' }]}
          >
            <Input.Password placeholder="请输入OpenRouter API密钥" />
          </Form.Item>

          <Form.Item
            label="API基础地址"
            name="apiBase"
            rules={[{ required: true, message: '请输入API基础地址' }]}
          >
            <Input placeholder="https://api.siliconflow.cn" />
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
            </Select>
          </Form.Item>

          <Form.Item
            label="代理设置"
            name="proxy"
          >
            <Input placeholder="127.0.0.1:7890" />
          </Form.Item>

          <Form.Item
            label="欧路词典Token"
            name="eudicToken"
          >
            <Input.Password placeholder="请输入欧路词典Token" />
          </Form.Item>

          <Form.Item
            label="欧路词典ID"
            name="eudicId"
          >
            <Input placeholder="0" />
          </Form.Item>

          <Form.Item
            label="牌组名称"
            name="deckName"
            rules={[{ required: true, message: '请输入牌组名称' }]}
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