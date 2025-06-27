# Anki Packager Web 前端

这是 Anki Packager 的 Web 前端界面，基于 React + Vite + Ant Design 构建。

## 功能特性

### 🎯 核心功能
- **仪表盘**: 系统概览、统计信息、快速操作
- **单词管理**: 添加、删除、查看单词列表
- **卡片生成**: 批量生成 Anki 卡片，支持进度显示
- **配置管理**: API 密钥、模型设置等配置
- **文件管理**: 上传字典文件、下载生成的 apkg 文件

### 🎨 界面特点
- 现代化 UI 设计，基于 Ant Design
- 响应式布局，支持移动端
- 直观的操作流程
- 实时进度反馈

## 技术栈

- **前端框架**: React 19
- **构建工具**: Vite
- **UI 组件库**: Ant Design 5
- **HTTP 客户端**: Axios
- **开发语言**: JavaScript/JSX

## 快速开始

### 安装依赖
```bash
cd frontend/anki-web
npm install
```

### 启动开发服务器
```bash
npm run dev
```

访问 http://localhost:5173 查看应用

### 构建生产版本
```bash
npm run build
```

## 项目结构

```
frontend/anki-web/
├── src/
│   ├── components/          # 组件目录
│   │   ├── Dashboard.jsx    # 仪表盘组件
│   │   ├── WordManagement.jsx # 单词管理组件
│   │   ├── CardGeneration.jsx # 卡片生成组件
│   │   ├── Configuration.jsx  # 配置管理组件
│   │   └── FileManagement.jsx # 文件管理组件
│   ├── App.jsx             # 主应用组件
│   ├── main.jsx            # 应用入口
│   ├── App.css             # 应用样式
│   └── index.css           # 全局样式
├── package.json            # 项目配置
└── README.md              # 项目说明
```

## 开发说明

### 组件说明

1. **Dashboard**: 系统概览页面，显示统计信息和快速操作
2. **WordManagement**: 单词管理页面，支持增删改查单词
3. **CardGeneration**: 卡片生成页面，支持批量生成和进度显示
4. **Configuration**: 配置管理页面，管理 API 密钥等设置
5. **FileManagement**: 文件管理页面，处理字典文件和输出文件

### API 集成

目前使用模拟数据，后续需要集成后端 API：

- 单词管理 API
- 卡片生成 API
- 配置管理 API
- 文件上传/下载 API

### 样式定制

- 使用 Ant Design 主题系统
- 自定义 CSS 在 App.css 中
- 响应式设计支持移动端

## 部署说明

### 开发环境
```bash
npm run dev
```

### 生产环境
```bash
npm run build
npm run preview
```

### Docker 部署
```bash
# 构建镜像
docker build -t anki-web .

# 运行容器
docker run -p 80:80 anki-web
```

## 后续计划

- [ ] 集成后端 API
- [ ] 添加用户认证
- [ ] 支持移动端适配
- [ ] 添加更多主题选项
- [ ] 国际化支持
- [ ] 性能优化

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 