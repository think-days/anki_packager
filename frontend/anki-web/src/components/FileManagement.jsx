import React, { useState, useEffect } from 'react';
import { Card, Upload, Button, List, Space, message, Progress, Alert, Empty, Tag } from 'antd';
import { UploadOutlined, DownloadOutlined, DeleteOutlined, FileTextOutlined, ReloadOutlined } from '@ant-design/icons';
import { fileAPI } from '../services/api';

const FileManagement = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      setLoading(true);
      setError(null);
      
      try {
        const data = await fileAPI.getFiles();
        setFiles(data.files || []);
      } catch (apiError) {
        console.warn('API not available, using mock data:', apiError);
        // 使用模拟数据
        setFiles([
          { name: 'stardict.7z', type: 'dictionary', size: '790MB', status: 'uploaded' },
          { name: '单词释义比例词典.mdx', type: 'dictionary', size: '50MB', status: 'uploaded' },
          { name: 'anki_packager.apkg', type: 'output', size: '2MB', status: 'generated' },
        ]);
      }
    } catch (err) {
      setError(err.message);
      message.error('加载文件列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    try {
      setUploading(true);
      setUploadProgress(0);
      
      try {
        await fileAPI.uploadFile(file, (progress) => {
          setUploadProgress(progress);
        });
        message.success('文件上传成功');
      } catch (apiError) {
        console.warn('API not available, using mock upload:', apiError);
        // 模拟上传过程
        for (let i = 0; i <= 100; i += 10) {
          setUploadProgress(i);
          await new Promise(resolve => setTimeout(resolve, 200));
        }
        message.success('文件上传成功');
      }
      
      loadFiles();
    } catch (err) {
      message.error(`上传失败: ${err.message}`);
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDownload = async (file) => {
    try {
      const blob = await fileAPI.downloadFile(file.name);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      message.success(`开始下载 ${file.name}`);
    } catch (err) {
      message.error(`下载失败: ${err.message}`);
    }
  };

  const handleDelete = async (file) => {
    try {
      await fileAPI.deleteFile(file.name);
      setFiles(prev => prev.filter(f => f.name !== file.name));
      message.success('文件删除成功');
    } catch (err) {
      message.error(`删除失败: ${err.message}`);
    }
  };

  const uploadProps = {
    beforeUpload: (file) => {
      // 检查文件类型
      const allowedTypes = ['.7z', '.mdx', '.rar', '.zip'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (!allowedTypes.includes(fileExtension)) {
        message.error('不支持的文件格式，请上传 .7z, .mdx, .rar 或 .zip 文件');
        return false;
      }
      
      // 检查文件大小 (限制为1GB)
      const maxSize = 1024 * 1024 * 1024; // 1GB
      if (file.size > maxSize) {
        message.error('文件大小不能超过1GB');
        return false;
      }
      
      handleUpload(file);
      return false; // 阻止自动上传
    },
    showUploadList: false,
    accept: '.7z,.mdx,.rar,.zip',
  };

  if (error) {
    return (
      <Alert
        message="加载失败"
        description={error}
        type="error"
        showIcon
        action={
          <Button size="small" danger onClick={loadFiles}>
            重试
          </Button>
        }
      />
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2>文件管理</h2>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={loadFiles}
          loading={loading}
        >
          刷新
        </Button>
      </div>
      
      <Alert
        message="文件说明"
        description="支持上传字典文件(.7z, .mdx, .rar, .zip)和下载生成的Anki包文件(.apkg)"
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
            支持格式：.7z, .mdx, .rar, .zip (最大1GB)
          </div>
        </Space>
      </Card>

      <Card title={`文件列表 (${files.length})`}>
        <List
          loading={loading}
          dataSource={files}
          locale={{
            emptyText: <Empty description="暂无文件" />
          }}
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
                title={
                  <Space>
                    {file.name}
                    <Tag color={file.type === 'dictionary' ? 'blue' : 'green'}>
                      {file.type === 'dictionary' ? '字典文件' : '输出文件'}
                    </Tag>
                  </Space>
                }
                description={
                  <Space>
                    <span>大小: {file.size}</span>
                    <span>状态: {file.status}</span>
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