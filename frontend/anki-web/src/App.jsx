import React from 'react';
import { Layout, Menu, theme, ConfigProvider } from 'antd';
import { 
  BookOutlined, 
  SettingOutlined, 
  FileTextOutlined,
  UploadOutlined,
  DownloadOutlined,
  DashboardOutlined
} from '@ant-design/icons';
import WordManagement from './components/WordManagement';
import CardGeneration from './components/CardGeneration';
import Configuration from './components/Configuration';
import FileManagement from './components/FileManagement';
import Dashboard from './components/Dashboard';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

const { Header, Content, Sider } = Layout;

function App() {
  const [selectedKey, setSelectedKey] = React.useState('dashboard');
  const [collapsed, setCollapsed] = React.useState(false);
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: 'words',
      icon: <BookOutlined />,
      label: '单词管理',
    },
    {
      key: 'generation',
      icon: <FileTextOutlined />,
      label: '卡片生成',
    },
    {
      key: 'files',
      icon: <UploadOutlined />,
      label: '文件管理',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '配置设置',
    },
  ];

  const renderContent = () => {
    switch (selectedKey) {
      case 'dashboard':
        return <Dashboard />;
      case 'words':
        return <WordManagement />;
      case 'generation':
        return <CardGeneration />;
      case 'files':
        return <FileManagement />;
      case 'settings':
        return <Configuration />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <ErrorBoundary>
        <Layout style={{ minHeight: '100vh' }}>
          <Header style={{ 
            display: 'flex', 
            alignItems: 'center', 
            background: colorBgContainer,
            padding: '0 24px',
            position: 'sticky',
            top: 0,
            zIndex: 1000,
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <div style={{ 
              fontSize: '20px', 
              fontWeight: 'bold',
              color: '#1890ff',
              flex: 1
            }}>
              Anki Packager Web
            </div>
          </Header>
          <Layout>
            <Sider 
              width={200} 
              style={{ background: colorBgContainer }}
              breakpoint="lg"
              collapsedWidth="0"
              onCollapse={(collapsed) => setCollapsed(collapsed)}
              collapsible
            >
              <Menu
                mode="inline"
                selectedKeys={[selectedKey]}
                style={{ height: '100%', borderRight: 0 }}
                items={menuItems}
                onClick={({ key }) => setSelectedKey(key)}
              />
            </Sider>
            <Layout style={{ padding: '0 24px 24px' }}>
              <Content
                style={{
                  padding: 24,
                  margin: 0,
                  minHeight: 280,
                  background: colorBgContainer,
                  borderRadius: borderRadiusLG,
                }}
              >
                <ErrorBoundary>
                  {renderContent()}
                </ErrorBoundary>
              </Content>
            </Layout>
          </Layout>
        </Layout>
      </ErrorBoundary>
    </ConfigProvider>
  );
}

export default App;
