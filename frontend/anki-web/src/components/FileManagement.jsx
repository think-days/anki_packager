import React, { useState, useEffect } from 'react';
import { Card, Upload, Button, List, Space, message, Progress, Alert } from 'antd';
import { UploadOutlined, DownloadOutlined, DeleteOutlined, FileTextOutlined } from '@ant-design/icons';

const FileManagement = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    // 模拟加载文件列表
    setFiles([
      { name: 'stardict.7z', type: 'dictionary', size: '790MB', status: 'uploaded' },
      { name: '单词释义比例词典.mdx', type: 'dictionary', size: '50MB', status: 'uploaded' },
      { name: 'anki_packager.apkg', type: 'output', size: '2MB', status: 'generated' },
    ]);
  };

  const handleUpload = async (file) => {
    setUploading(true);
    setUploadProgress(0);
    
    // 模拟上传过程
    for (let i = 0; i <= 100; i += 10) {
      setUploadProgress(i);
      await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    setUploading(false);
    setUploadProgress(0);
    message.success('文件上传成功');
    loadFiles();
  };

  const handleDownload = (file) => {
    // 模拟下载
    message.success(`开始下载 ${file.name}`);
  };

  const handleDelete = (file) => {
    setFiles(prev => prev.filter(f => f.name !== file.name));
    message.success('文件删除成功');
  };

  const uploadProps = {
    beforeUpload: (file) => {
      handleUpload(file);
      return false; // 阻止自动上传
    },
    showUploadList: false,
  };

  return (
    <div>
      <h2>文件管理</h2>
      
      <Alert
        message="文件说明"
        description="支持上传字典文件(.7z, .mdx)和下载生成的Anki包文件(.apkg)"
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Card title="上传文件" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Upload {...uploadProps}>
            <Button 
              icon={<UploadOutlined />} 
              loading={uploading}
              disabled={uploading}
            >
              选择文件
            </Button>
          </Upload>
          
          {uploading && (
            <Progress percent={uploadProgress} status="active" />
          )}
          
          <div style={{ fontSize: '12px', color: '#666' }}>
            支持格式：.7z, .mdx, .rar
          </div>
        </Space>
      </Card>

      <Card title="文件列表">
        <List
          dataSource={files}
          renderItem={(file) => (
            <List.Item
              actions={[
                <Button
                  key="download"
                  type="link"
                  icon={<DownloadOutlined />}
                  onClick={() => handleDownload(file)}
                  disabled={file.type !== 'output'}
                >
                  下载
                </Button>,
                <Button
                  key="delete"
                  type="link"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleDelete(file)}
                >
                  删除
                </Button>
              ]}
            >
              <List.Item.Meta
                avatar={<FileTextOutlined />}
                title={file.name}
                description={
                  <Space>
                    <span>大小: {file.size}</span>
                    <span>类型: {file.type === 'dictionary' ? '字典文件' : '输出文件'}</span>
                  </Space>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default FileManagement; 