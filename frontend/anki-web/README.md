# Anki Packager Web

Anki Packager 的 Web 前端界面，提供现代化的用户界面来管理单词、生成卡片和配置系统。

## 功能特性

- 🎯 **仪表盘** - 系统状态概览和快速操作
- 📚 **单词管理** - 添加、删除、批量导入单词
- 🎴 **卡片生成** - 一键生成 Anki 卡片包
- 📁 **文件管理** - 上传字典文件和下载生成的包
- ⚙️ **配置设置** - 配置 AI 服务和词典源
- 📱 **响应式设计** - 支持桌面和移动设备
- 🌙 **暗色主题** - 自动适应系统主题

## 技术栈

- **React 19** - 现代化的 React 框架
- **Ant Design 5** - 企业级 UI 组件库
- **Vite** - 快速的构建工具
- **Axios** - HTTP 客户端
- **ESLint** - 代码质量检查

## 开发环境

### 前置要求

- Node.js 18+ 
- npm 或 yarn

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

开发服务器将在 http://localhost:3000 启动。

### 构建生产版本

```bash
npm run build
```

构建文件将输出到 `dist` 目录。

### 代码检查

```bash
npm run lint
```

## 项目结构

```
src/
├── components/          # React 组件
│   ├── Dashboard.jsx    # 仪表盘
│   ├── WordManagement.jsx # 单词管理
│   ├── CardGeneration.jsx # 卡片生成
│   ├── FileManagement.jsx # 文件管理
│   ├── Configuration.jsx  # 配置设置
│   └── ErrorBoundary.jsx  # 错误边界
├── services/           # API 服务
│   └── api.js         # API 接口定义
├── App.jsx            # 主应用组件
├── main.jsx           # 应用入口
└── index.css          # 全局样式
```

## API 接口

前端通过 RESTful API 与后端通信：

### 单词管理
- `GET /api/words` - 获取单词列表
- `POST /api/words` - 添加单词
- `POST /api/words/batch` - 批量添加单词
- `DELETE /api/words/:word` - 删除单词
- `DELETE /api/words` - 清空单词列表
- `POST /api/words/cleanup-audio` - 清理孤立音频

### 卡片生成
- `POST /api/cards/generate` - 生成卡片
- `GET /api/cards/progress` - 获取生成进度
- `GET /api/cards/download` - 下载生成的包

### 文件管理
- `GET /api/files` - 获取文件列表
- `POST /api/files/upload` - 上传文件
- `DELETE /api/files/:filename` - 删除文件
- `GET /api/files/download/:filename` - 下载文件

### 配置管理
- `GET /api/config` - 获取配置
- `POST /api/config` - 保存配置
- `POST /api/config/test` - 测试配置

### 统计信息
- `GET /api/stats` - 获取系统统计

## 开发说明

### 错误处理

项目使用 Error Boundary 来捕获 React 组件错误，并提供友好的错误提示。

### 响应式设计

使用 Ant Design 的栅格系统和媒体查询实现响应式布局，支持各种屏幕尺寸。

### 主题定制

通过 CSS 变量和 Ant Design 的主题配置实现主题定制，支持明暗主题切换。

### API 模拟

在开发环境中，如果后端服务不可用，前端会使用模拟数据，确保开发体验的连续性。

## 部署

### 开发环境

```bash
npm run dev
```

### 生产环境

1. 构建项目：
```bash
npm run build
```

2. 部署 `dist` 目录到 Web 服务器

3. 配置反向代理，将 `/api` 路径代理到后端服务

### Docker 部署

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。
