import http.server
import socketserver
import os
import json
import subprocess
import shutil
import re
import sys
from urllib.parse import parse_qs, urlparse

PORT = 8080
DIRECTORY = "static"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 确保必要的目录存在
def ensure_directories():
    # 创建静态目录
    os.makedirs(DIRECTORY, exist_ok=True)
    
    # 确保config目录存在
    config_dir = os.path.join(PROJECT_ROOT, "config")
    os.makedirs(config_dir, exist_ok=True)
    
    # 确保audio目录存在
    audio_dir = os.path.join(PROJECT_ROOT, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    # 确保cache目录存在
    cache_dir = os.path.join(config_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    # 确保vocabulary.txt存在
    vocab_path = os.path.join(config_dir, "vocabulary.txt")
    if not os.path.exists(vocab_path):
        with open(vocab_path, "w", encoding="utf-8") as f:
            f.write("")

# 执行Python CLI命令
def exec_python_command(command):
    try:
        # 在Windows上使用shell=True可能会导致一些问题，所以我们分别处理
        if sys.platform == 'win32':
            cmd = f"python -m anki_packager.cli {command}"
            # 在Windows上使用subprocess.run时，设置text=True和encoding
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors='replace'  # 处理编码错误
            )
        else:
            # 在类Unix系统上
            cmd = ["python", "-m", "anki_packager.cli"] + command.split()
            result = subprocess.run(
                cmd,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
        
        if result.returncode != 0 and result.stderr:
            print(f"命令执行错误: {result.stderr}")
            return {"error": result.stderr}
        
        return {"output": result.stdout}
    except Exception as e:
        print(f"执行命令时出错: {str(e)}")
        return {"error": str(e)}

# 获取所有单词
def get_words():
    result = exec_python_command("--list-words")
    if "error" in result:
        return {"error": result["error"]}
    
    output = result.get("output", "")
    if not output:
        return []
        
    lines = output.strip().split('\n')
    words = []
    
    for line in lines:
        if "词汇表中共有" in line or "词汇表为空" in line:
            continue
        
        match = re.match(r'^\s*\d+\.\s+(.+)$', line)
        if match:
            word = match.group(1).strip()
            words.append({
                "word": word,
                "addedAt": None  # 无法从命令行输出获取添加时间
            })
    
    return words

# 添加单词
def add_word(word):
    if not word:
        return {"error": "缺少必要参数: word"}
    
    result = exec_python_command(f'--word "{word}"')
    if "error" in result:
        return {"error": result["error"]}
    
    output = result.get("output", "")
    
    if "已添加到生词本" in output or "添加成功" in output:
        return {
            "success": True,
            "message": f"已添加单词: {word}",
            "word": word
        }
    elif "已存在于生词本" in output:
        return {
            "success": False,
            "message": f"单词 {word} 已存在于生词本",
            "word": word
        }
    else:
        return {
            "success": False,
            "message": "添加单词失败",
            "word": word
        }

# 获取统计信息
def get_stats():
    result = exec_python_command("--stats")
    if "error" in result:
        return {"error": result["error"]}
    
    output = result.get("output", "")
    if not output:
        return {"wordCount": 0, "audioCount": 0, "cacheCount": 0}
        
    lines = output.strip().split('\n')
    
    word_count = 0
    audio_count = 0
    cache_count = 0
    
    for line in lines:
        word_match = re.search(r'词汇表中共有\s+(\d+)\s+个单词', line)
        if word_match:
            word_count = int(word_match.group(1))
            continue
        
        audio_match = re.search(r'音频文件夹中共有\s+(\d+)\s+个音频文件', line)
        if audio_match:
            audio_count = int(audio_match.group(1))
            continue
        
        cache_match = re.search(r'AI缓存中共有\s+(\d+)\s+个缓存条目', line)
        if cache_match:
            cache_count = int(cache_match.group(1))
            continue
    
    return {
        "wordCount": word_count,
        "audioCount": audio_count,
        "cacheCount": cache_count
    }

# 创建一个简单的HTML页面
def create_index_html():
    with open(os.path.join(DIRECTORY, "index.html"), "w", encoding="utf-8") as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anki Packager</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2563eb;
            margin-bottom: 20px;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background-color: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .card h2 {
            margin-top: 0;
            color: #1e40af;
        }
        .btn {
            display: inline-block;
            background-color: #2563eb;
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            text-decoration: none;
            margin-right: 10px;
            margin-bottom: 10px;
            cursor: pointer;
        }
        .btn:hover {
            background-color: #1d4ed8;
        }
        .btn-outline {
            background-color: transparent;
            border: 1px solid #2563eb;
            color: #2563eb;
        }
        .btn-outline:hover {
            background-color: #f0f9ff;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
        }
        .input-group {
            margin-bottom: 15px;
        }
        .input-group input {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100%;
            box-sizing: border-box;
        }
        .message {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            display: none;
        }
        .success {
            background-color: #dcfce7;
            color: #166534;
            border: 1px solid #bbf7d0;
        }
        .error {
            background-color: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }
    </style>
</head>
<body>
    <h1>Anki Packager</h1>
    <p>自动生成高质量的英语学习卡片，集成多源词典和AI辅助记忆</p>
    
    <div class="message success" id="successMessage"></div>
    <div class="message error" id="errorMessage"></div>
    
    <div class="card">
        <h2>添加单词</h2>
        <div class="input-group">
            <input type="text" id="wordInput" placeholder="输入单词...">
        </div>
        <button class="btn" onclick="addWord()">添加单词</button>
    </div>
    
    <div class="card">
        <h2>功能概览</h2>
        <div class="grid">
            <div>
                <h3>单词管理</h3>
                <p>添加、删除和管理您的单词列表</p>
                <button class="btn" onclick="showWords()">管理单词</button>
            </div>
            <div>
                <h3>音频管理</h3>
                <p>管理单词的音频文件</p>
                <button class="btn" onclick="alert('功能开发中')">管理音频</button>
            </div>
            <div>
                <h3>AI缓存</h3>
                <p>管理AI生成的内容缓存</p>
                <button class="btn" onclick="alert('功能开发中')">管理缓存</button>
            </div>
            <div>
                <h3>牌组管理</h3>
                <p>生成和管理Anki牌组</p>
                <button class="btn" onclick="alert('功能开发中')">管理牌组</button>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>系统状态</h2>
        <p>单词总数: <span id="wordCount">0</span></p>
        <p>音频文件: <span id="audioCount">0</span></p>
        <p>AI缓存: <span id="cacheCount">0</span></p>
        <button class="btn" onclick="refreshStats()">刷新统计</button>
        <button class="btn btn-outline" onclick="resetSystem()">重置系统</button>
    </div>
    
    <div class="card" id="wordList" style="display: none;">
        <h2>单词列表</h2>
        <div id="wordListContent"></div>
    </div>
    
    <script>
        // 添加单词
        async function addWord() {
            const wordInput = document.getElementById('wordInput');
            const word = wordInput.value.trim();
            
            if (!word) {
                showError('请输入单词');
                return;
            }
            
            try {
                const response = await fetch('/api/words', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ word })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showSuccess(`已添加单词: ${word}`);
                    wordInput.value = '';
                    refreshStats();
                } else {
                    showError(data.message || '添加单词失败');
                }
            } catch (error) {
                showError('请求失败: ' + error.message);
            }
        }
        
        // 显示单词列表
        async function showWords() {
            const wordList = document.getElementById('wordList');
            const wordListContent = document.getElementById('wordListContent');
            
            try {
                const response = await fetch('/api/words');
                const data = await response.json();
                
                if (response.ok) {
                    wordListContent.innerHTML = '';
                    
                    if (data.length === 0) {
                        wordListContent.innerHTML = '<p>词汇表为空</p>';
                    } else {
                        const ul = document.createElement('ul');
                        data.forEach(item => {
                            const li = document.createElement('li');
                            li.textContent = item.word;
                            ul.appendChild(li);
                        });
                        wordListContent.appendChild(ul);
                    }
                    
                    wordList.style.display = 'block';
                } else {
                    showError(data.error || '获取单词列表失败');
                }
            } catch (error) {
                showError('请求失败: ' + error.message);
            }
        }
        
        // 刷新统计
        async function refreshStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('wordCount').textContent = data.wordCount;
                    document.getElementById('audioCount').textContent = data.audioCount;
                    document.getElementById('cacheCount').textContent = data.cacheCount;
                } else {
                    showError(data.error || '获取统计信息失败');
                }
            } catch (error) {
                showError('请求失败: ' + error.message);
            }
        }
        
        // 重置系统
        function resetSystem() {
            if (confirm('确定要重置系统吗？这将清空所有数据。')) {
                alert('重置功能开发中');
            }
        }
        
        // 显示成功消息
        function showSuccess(message) {
            const successMessage = document.getElementById('successMessage');
            successMessage.textContent = message;
            successMessage.style.display = 'block';
            
            setTimeout(() => {
                successMessage.style.display = 'none';
            }, 3000);
        }
        
        // 显示错误消息
        function showError(message) {
            const errorMessage = document.getElementById('errorMessage');
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
            
            setTimeout(() => {
                errorMessage.style.display = 'none';
            }, 3000);
        }
        
        // 初始加载统计数据
        refreshStats();
    </script>
</body>
</html>
""")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        # 解析URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # API路由处理
        if path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {"error": "未知的API路由"}
            
            if path == '/api/words':
                response_data = get_words()
            elif path == '/api/stats':
                response_data = get_stats()
            
            self.wfile.write(json.dumps(response_data).encode())
            return
        
        # 静态文件处理
        return super().do_GET()
    
    def do_POST(self):
        # 解析URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # 读取请求体
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request_data = json.loads(post_data)
        except:
            request_data = {}
        
        # API路由处理
        if path.startswith('/api/'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response_data = {"error": "未知的API路由"}
            
            if path == '/api/words':
                word = request_data.get('word', '')
                response_data = add_word(word)
            
            self.wfile.write(json.dumps(response_data).encode())
            return
        
        # 默认处理
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')

def main():
    try:
        # 确保必要的目录存在
        ensure_directories()
        
        # 创建静态HTML页面
        create_index_html()
        
        # 启动HTTP服务器
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"项目根目录: {PROJECT_ROOT}")
            print(f"服务器运行在: http://localhost:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器错误: {str(e)}")

if __name__ == "__main__":
    main() 