import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = util.promisify(exec);
const projectRoot = 'D:\\Code\\anki_packager';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { name, words } = body;
    
    // 验证请求参数
    if (!name) {
      return NextResponse.json({ 
        error: '缺少必要参数: name'
      }, { status: 400 });
    }
    
    // 构建命令
    let command = `python -m anki_packager.cli`;
    
    // 设置牌组名称
    const configPath = path.join(projectRoot, 'config', 'config.json');
    if (fs.existsSync(configPath)) {
      try {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
        config.DECK_NAME = name;
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
      } catch (err) {
        console.error('更新配置文件失败:', err);
      }
    }
    
    // 如果指定了单词列表，创建临时文件
    let tempFile = '';
    if (words && words.length > 0) {
      tempFile = path.join(projectRoot, 'tmp', `temp_words_${Date.now()}.txt`);
      fs.mkdirSync(path.dirname(tempFile), { recursive: true });
      fs.writeFileSync(tempFile, words.join('\n'), 'utf-8');
      command += ` --txt "${tempFile}"`;
    }
    
    // 执行命令生成牌组
    const { stdout, stderr } = await execAsync(command, { cwd: projectRoot });
    
    // 删除临时文件
    if (tempFile && fs.existsSync(tempFile)) {
      fs.unlinkSync(tempFile);
    }
    
    // 检查是否成功生成
    if (stderr && !stderr.includes('INFO:')) {
      return NextResponse.json({
        error: '生成牌组失败',
        details: stderr
      }, { status: 500 });
    }
    
    // 获取生成的牌组文件信息
    const apkgFile = path.join(projectRoot, `${name}.apkg`);
    let fileSize = 0;
    let wordCount = words ? words.length : 0;
    
    if (fs.existsSync(apkgFile)) {
      const stats = fs.statSync(apkgFile);
      fileSize = stats.size;
      
      // 如果没有指定单词列表，尝试从输出中获取单词数量
      if (!words || words.length === 0) {
        const match = stdout.match(/已处理\s+(\d+)\s+个单词/);
        if (match) {
          wordCount = parseInt(match[1]);
        }
      }
    }
    
    return NextResponse.json({
      success: true,
      message: `已生成牌组 ${name}`,
      deck: {
        id: Date.now().toString(),
        name,
        wordCount,
        createdAt: new Date().toISOString(),
        lastModified: new Date().toISOString(),
        size: fileSize
      }
    });
  } catch (error) {
    console.error('生成牌组失败:', error);
    return NextResponse.json({
      error: '生成牌组失败',
      details: (error as Error).message
    }, { status: 500 });
  }
} 