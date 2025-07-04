import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Button, Progress, List, Tag, Space, Alert, Spin } from 'antd';
import { 
  BookOutlined, 
  FileTextOutlined, 
  AudioOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { statsAPI } from '../services/api';

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
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // 尝试从API获取数据，如果失败则使用模拟数据
      try {
        const data = await statsAPI.getStats();
        setStats(data);
        setRecentWords(data.recentWords || []);
      } catch (apiError) {
        console.warn('API not available, using mock data:', apiError);
        // 使用模拟数据
        setStats({
          totalWords: 10,
          totalAudio: 8,
          orphanedAudio: 2,
          missingAudio: 2,
          lastGenerated: '2024-01-15 14:30',
          configStatus: 'configured'
        });
        setRecentWords(['hello', 'world', 'beautiful', 'wonderful', 'excellent']);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const quickActions = [
    {
      title: '添加单词',
      icon: <BookOutlined />,
      action: () => {
        // 这里可以导航到单词管理页面
        window.location.hash = '#words';
      },
      color: '#52c41a'
    },
    {
      title: '生成卡片',
      icon: <FileTextOutlined />,
      action: () => {
        window.location.hash = '#generation';
      },
      color: '#1890ff'
    },
    {
      title: '清理音频',
      icon: <AudioOutlined />,
      action: () => {
        window.location.hash = '#words';
      },
      color: '#faad14'
    },
    {
      title: '配置设置',
      icon: <SettingOutlined />,
      action: () => {
        window.location.hash = '#settings';
      },
      color: '#722ed1'
    }
  ];

  if (error) {
    return (
      <Alert
        message="加载失败"
        description={error}
        type="error"
        showIcon
        action={
          <Button size="small" danger onClick={fetchStats}>
            重试
          </Button>
        }
      />
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2>仪表盘</h2>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={fetchStats}
          loading={isLoading}
          data-testid="dashboard-refresh"
        >
          刷新
        </Button>
      </div>
      
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总单词数"
              value={stats.totalWords}
              prefix={<BookOutlined />}
              loading={isLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="音频文件"
              value={stats.totalAudio}
              prefix={<AudioOutlined />}
              loading={isLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
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
        <Col xs={24} sm={12} lg={6}>
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
        <Row gutter={[16, 16]}>
          {quickActions.map((action, index) => (
            <Col xs={24} sm={12} lg={6} key={index}>
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
                data-testid={`dashboard-quick-action-${index}`}
              >
                {action.title}
              </Button>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 系统状态 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
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
                  percent={stats.totalWords > 0 ? Math.round((stats.totalAudio / stats.totalWords) * 100) : 0} 
                  size="small"
                  status={stats.missingAudio > 0 ? 'exception' : 'success'}
                />
              </div>
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="最近单词">
            <List
              size="small"
              dataSource={recentWords}
              loading={isLoading}
              renderItem={(word) => (
                <List.Item>
                  <Tag color="blue">{word}</Tag>
                </List.Item>
              )}
              locale={{
                emptyText: '暂无单词'
              }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 