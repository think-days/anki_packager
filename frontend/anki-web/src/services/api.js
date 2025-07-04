import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api', // 强制所有请求都走 /api 前缀，兼容 Vite 代理和后端路由
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error);
    if (error.response) {
      // 服务器返回错误状态码
      const message = error.response.data?.message || `请求失败: ${error.response.status}`;
      throw new Error(message);
    } else if (error.request) {
      // 网络错误
      throw new Error('网络连接失败，请检查网络设置');
    } else {
      // 其他错误
      throw new Error(error.message || '未知错误');
    }
  }
);

// API方法
export const wordAPI = {
  // 获取单词列表
  getWords: () => api.get('/words'),
  
  // 添加单词
  addWord: (word) => api.post('/words', { word }),
  
  // 批量添加单词
  addBatchWords: (words) => api.post('/words/batch', { words }),
  
  // 删除单词
  deleteWord: (word) => api.delete(`/words/${encodeURIComponent(word)}`),
  
  // 清空单词列表
  clearWords: () => api.delete('/words'),
  
  // 清理孤立音频
  cleanupAudio: () => api.post('/words/cleanup-audio'),
};

export const cardAPI = {
  // 生成卡片
  generateCards: (options) => api.post('/cards/generate', options),
  
  // 获取生成进度
  getProgress: () => api.get('/cards/progress'),
  
  // 下载生成的包
  downloadPackage: () => api.get('/cards/download', { responseType: 'blob' }),
};

export const fileAPI = {
  // 上传文件
  uploadFile: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percentCompleted);
        }
      },
    });
  },
  
  // 获取文件列表
  getFiles: () => api.get('/files'),
  
  // 删除文件
  deleteFile: (filename) => api.delete(`/files/${encodeURIComponent(filename)}`),
  
  // 下载文件
  downloadFile: (filename) => api.get(`/files/download/${encodeURIComponent(filename)}`, { 
    responseType: 'blob' 
  }),
};

export const configAPI = {
  // 获取配置
  getConfig: () => api.get('/config'),
  
  // 保存配置
  saveConfig: (config) => api.post('/config', config),
  
  // 测试配置
  testConfig: () => api.post('/config/test'),
};

export const statsAPI = {
  // 获取统计数据
  getStats: () => api.get('/stats'),
};

export default api; 