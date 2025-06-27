import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  List, 
  Tag, 
  Space, 
  Modal, 
  message, 
  Popconfirm,
  Upload,
  Table,
  Tooltip
} from 'antd';
import { 
  PlusOutlined, 
  DeleteOutlined, 
  AudioOutlined,
  UploadOutlined,
  DownloadOutlined,
  ClearOutlined
} from '@ant-design/icons';

const { TextArea } = Input;

const WordManagement = () => {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [newWord, setNewWord] = useState('');
  const [batchWords, setBatchWords] = useState('');

  // 模拟获取单词列表
  useEffect(() => {
    fetchWords();
  }, []);

  const fetchWords = async () => {
    setLoading(true);
    // 这里将来会调用后端API
    setTimeout(() => {
      setWords([
        { word: 'hello', hasAudio: true },
        { word: 'world', hasAudio: true },
        { word: 'beautiful', hasAudio: true },
        { word: 'wonderful', hasAudio: true },
        { word: 'excellent', hasAudio: true },
        { word: 'test', hasAudio: false },
      ]);
      setLoading(false);
    }, 1000);
  };

  const handleAddWord = async () => {
    if (!newWord.trim()) {
      message.error('请输入单词');
      return;
    }
    
    // 这里将来会调用后端API
    setWords(prev => [...prev, { word: newWord.trim(), hasAudio: false }]);
    setNewWord('');
    setAddModalVisible(false);
    message.success('单词添加成功');
  };

  const handleAddBatchWords = async () => {
    if (!batchWords.trim()) {
      message.error('请输入单词');
      return;
    }
    
    const wordList = batchWords.split('\n').map(w => w.trim()).filter(w => w);
    // 这里将来会调用后端API
    setWords(prev => [...prev, ...wordList.map(word => ({ word, hasAudio: false }))]);
    setBatchWords('');
    setAddModalVisible(false);
    message.success(`成功添加 ${wordList.length} 个单词`);
  };

  const handleDeleteWord = async (word) => {
    // 这里将来会调用后端API
    setWords(prev => prev.filter(w => w.word !== word));
    message.success('单词删除成功');
  };

  const handleClearWords = async () => {
    // 这里将来会调用后端API
    setWords([]);
    message.success('单词列表已清空');
  };

  const handleCleanupAudio = async () => {
    // 这里将来会调用后端API
    message.success('孤立音频文件清理完成');
  };

  const columns = [
    {
      title: '单词',
      dataIndex: 'word',
      key: 'word',
      render: (word) => <Tag color="blue">{word}</Tag>,
    },
    {
      title: '音频状态',
      dataIndex: 'hasAudio',
      key: 'hasAudio',
      render: (hasAudio) => (
        <Tag color={hasAudio ? 'green' : 'red'}>
          {hasAudio ? '已生成' : '未生成'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Tooltip title="删除单词">
            <Popconfirm
              title="确定要删除这个单词吗？"
              onConfirm={() => handleDeleteWord(record.word)}
              okText="确定"
              cancelText="取消"
            >
              <Button 
                type="text" 
                danger 
                icon={<DeleteOutlined />}
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <h2>单词管理</h2>
      
      {/* 操作按钮 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={() => setAddModalVisible(true)}
          >
            添加单词
          </Button>
          <Button 
            icon={<UploadOutlined />}
            onClick={() => setAddModalVisible(true)}
          >
            批量添加
          </Button>
          <Button 
            icon={<ClearOutlined />}
            onClick={handleCleanupAudio}
          >
            清理孤立音频
          </Button>
          <Popconfirm
            title="确定要清空所有单词吗？"
            onConfirm={handleClearWords}
            okText="确定"
            cancelText="取消"
          >
            <Button danger icon={<ClearOutlined />}>
              清空单词
            </Button>
          </Popconfirm>
        </Space>
      </Card>

      {/* 单词列表 */}
      <Card title={`单词列表 (${words.length})`}>
        <Table
          columns={columns}
          dataSource={words}
          loading={loading}
          rowKey="word"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 个单词`,
          }}
        />
      </Card>

      {/* 添加单词模态框 */}
      <Modal
        title="添加单词"
        open={addModalVisible}
        onOk={newWord ? handleAddWord : handleAddBatchWords}
        onCancel={() => {
          setAddModalVisible(false);
          setNewWord('');
          setBatchWords('');
        }}
        okText="添加"
        cancelText="取消"
        width={600}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <h4>单个添加</h4>
            <Input
              placeholder="请输入单词"
              value={newWord}
              onChange={(e) => setNewWord(e.target.value)}
              onPressEnter={handleAddWord}
            />
          </div>
          <div>
            <h4>批量添加</h4>
            <TextArea
              placeholder="请输入单词，每行一个"
              value={batchWords}
              onChange={(e) => setBatchWords(e.target.value)}
              rows={6}
            />
          </div>
        </Space>
      </Modal>
    </div>
  );
};

export default WordManagement; 