import React, { useState } from 'react';
import { Card, Button, Progress, Space, Switch, message, Alert } from 'antd';
import { PlayCircleOutlined, DownloadOutlined, SettingOutlined } from '@ant-design/icons';

const CardGeneration = () => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [enableAI, setEnableAI] = useState(true);
  const [currentWord, setCurrentWord] = useState('');

  const handleGenerate = async () => {
    setIsGenerating(true);
    setProgress(0);
    
    // 模拟生成过程
    const words = ['hello', 'world', 'beautiful', 'wonderful'];
    for (let i = 0; i < words.length; i++) {
      setCurrentWord(words[i]);
      setProgress(((i + 1) / words.length) * 100);
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    setIsGenerating(false);
    setCurrentWord('');
    message.success('卡片生成完成！');
  };

  return (
    <div>
      <h2>卡片生成</h2>
      
      <Card style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <span>启用AI功能：</span>
            <Switch 
              checked={enableAI} 
              onChange={setEnableAI}
              disabled={isGenerating}
            />
          </div>
          
          <Button
            type="primary"
            size="large"
            icon={<PlayCircleOutlined />}
            onClick={handleGenerate}
            loading={isGenerating}
            disabled={isGenerating}
            style={{ width: 200 }}
          >
            {isGenerating ? '生成中...' : '开始生成'}
          </Button>
        </Space>
      </Card>

      {isGenerating && (
        <Card title="生成进度">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Progress percent={progress} status="active" />
            {currentWord && (
              <Alert
                message={`正在处理: ${currentWord}`}
                type="info"
                showIcon
              />
            )}
          </Space>
        </Card>
      )}

      <Card title="生成选项" style={{ marginTop: 16 }}>
        <Space direction="vertical">
          <div>• 自动生成音频文件</div>
          <div>• 包含词典释义</div>
          <div>• 包含AI助记内容</div>
          <div>• 包含例句和短语</div>
        </Space>
      </Card>
    </div>
  );
};

export default CardGeneration; 