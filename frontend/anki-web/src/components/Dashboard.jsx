import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Progress, List, Tag, Space } from 'antd';
import { 
  BookOutlined, 
  FileTextOutlined, 
  AudioOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  DownloadOutlined
} from '@ant-design/icons';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalWords: 0,
    totalAudio: 0,
    orphanedAudio: 0,
    missingAudio: 0,
    lastGenerated: null,
    configStatus: 'unknown'
  });

  const [recentWords, setRecentWords] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // 模拟获取统计数据
  useEffect(() => {
    // 这里将来会调用后端API
    setTimeout(() => {
      setStats({
        totalWords: 10,
        totalAudio: 10,
        orphanedAudio: 0,
        missingAudio: 0,
        lastGenerated: '2024-01-15 14:30',
        configStatus: 'configured'
      });
      setRecentWords([
        'hello', 'world', 'beautiful', 'wonderful', 'excellent'
      ]);
      setIsLoading(false);
    }, 1000);
  }, []);

  const quickActions = [
    {
      title: '添加单词',
      icon: <BookOutlined />,
      action: () => console.log('添加单词'),
      color: '#52c41a'
    },
    {
      title: '生成卡片',
      icon: <FileTextOutlined />,
      action: () => console.log('生成卡片'),
      color: '#1890ff'
    },
    {
      title: '清理音频',
      icon: <AudioOutlined />,
      action: () => console.log('清理音频'),
      color: '#faad14'
    },
    {
      title: '配置设置',
      icon: <SettingOutlined />,
      action: () => console.log('配置设置'),
      color: '#722ed1'
    }
  ];

  return (
    <div>
      <h2>仪表盘</h2>
      
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总单词数"
              value={stats.totalWords}
              prefix={<BookOutlined />}
              loading={isLoading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="音频文件"
              value={stats.totalAudio}
              prefix={<AudioOutlined />}
              loading={isLoading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="孤立音频"
              value={stats.orphanedAudio}
              prefix={<AudioOutlined />}
              valueStyle={{ color: stats.orphanedAudio > 0 ? '#cf1322' : '#3f8600' }}
              loading={isLoading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="缺失音频"
              value={stats.missingAudio}
              prefix={<AudioOutlined />}
              valueStyle={{ color: stats.missingAudio > 0 ? '#cf1322' : '#3f8600' }}
              loading={isLoading}
            />
          </Card>
        </Col>
      </Row>

      {/* 快速操作 */}
      <Card title="快速操作" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          {quickActions.map((action, index) => (
            <Col span={6} key={index}>
              <Button
                type="default"
                size="large"
                icon={action.icon}
                onClick={action.action}
                style={{ 
                  width: '100%', 
                  height: 80,
                  borderColor: action.color,
                  color: action.color
                }}
              >
                {action.title}
              </Button>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 系统状态 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card title="系统状态">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <span>配置状态: </span>
                <Tag color={stats.configStatus === 'configured' ? 'green' : 'red'}>
                  {stats.configStatus === 'configured' ? '已配置' : '未配置'}
                </Tag>
              </div>
              <div>
                <span>最后生成: </span>
                <span>{stats.lastGenerated || '从未生成'}</span>
              </div>
              <div>
                <span>音频同步: </span>
                <Progress 
                  percent={stats.totalWords > 0 ? (stats.totalAudio / stats.totalWords) * 100 : 0} 
                  size="small"
                  status={stats.missingAudio > 0 ? 'exception' : 'success'}
                />
              </div>
            </Space>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="最近单词">
            <List
              size="small"
              dataSource={recentWords}
              renderItem={(word) => (
                <List.Item>
                  <Tag color="blue">{word}</Tag>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 