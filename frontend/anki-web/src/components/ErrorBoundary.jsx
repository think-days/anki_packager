import React from 'react';
import { Result, Button } from 'antd';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // 可以在这里记录错误到日志服务
    console.error('Error caught by boundary:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <Result
          status="error"
          title="页面出现错误"
          subTitle="抱歉，页面遇到了一个错误。请尝试刷新页面或联系管理员。"
          extra={[
            <Button type="primary" key="reload" onClick={this.handleReload}>
              刷新页面
            </Button>,
          ]}
        >
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ whiteSpace: 'pre-wrap', marginTop: 16 }}>
              <summary>错误详情 (仅开发环境)</summary>
              <div style={{ 
                background: '#f5f5f5', 
                padding: 16, 
                borderRadius: 4,
                marginTop: 8,
                fontSize: '12px',
                fontFamily: 'monospace'
              }}>
                {this.state.error && this.state.error.toString()}
                <br />
                {this.state.errorInfo.componentStack}
              </div>
            </details>
          )}
        </Result>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 