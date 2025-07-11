# Anki Packager 前端

这是Anki Packager的前端项目，提供了一个简单的Web界面来管理单词、音频、缓存和牌组。

## 项目结构

- `server.py`: 一个简单的Python HTTP服务器，提供静态文件和API接口
- `anki-web/`: Next.js前端项目（可选，当前使用简化版静态HTML页面）

## 运行方式

### 方法1：使用Python HTTP服务器（推荐）

1. 确保已安装Python 3.6+
2. 在项目根目录下运行：

```bash
cd frontend
python server.py
```

3. 打开浏览器访问 http://localhost:8080

### 方法2：使用Next.js开发服务器

1. 确保已安装Node.js 16+
2. 在项目根目录下运行：

```bash
cd frontend/anki-web
npm install
npm run dev
```

3. 打开浏览器访问 http://localhost:3000

## 功能说明

- **单词管理**: 添加、查看和管理单词
- **音频管理**: 管理单词的音频文件（开发中）
- **AI缓存**: 管理AI生成的内容缓存（开发中）
- **牌组管理**: 生成和管理Anki牌组（开发中）

## API接口

服务器提供以下API接口：

- `GET /api/words`: 获取所有单词
- `POST /api/words`: 添加单词，请求体为 `{ "word": "example" }`
- `GET /api/stats`: 获取系统统计信息

## 注意事项

- 确保项目根目录下存在 `config` 和 `audio` 目录
- 确保 `config` 目录下存在 `vocabulary.txt` 文件
- 确保 `config/cache` 目录存在

## 故障排除

如果遇到问题，请尝试以下步骤：

1. 确保已安装所有依赖：`pip install -r requirements.txt`
2. 检查项目目录结构是否正确
3. 检查日志文件 `anki_packager.log`
4. 确保Python CLI命令可以正常运行：`python -m anki_packager.cli --help` 