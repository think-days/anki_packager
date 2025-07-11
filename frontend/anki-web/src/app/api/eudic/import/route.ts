import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = util.promisify(exec);
const projectRoot = 'D:\\Code\\anki_packager';
const configPath = path.join(projectRoot, 'config', 'config.json');
const vocabularyPath = path.join(projectRoot, 'config', 'vocabulary.txt');

// 从欧路词典导入生词
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { id } = body;
    
    // 验证请求参数
    if (!id) {
      return NextResponse.json({ 
        error: '缺少必要参数: id'
      }, { status: 400 });
    }
    
    // 检查配置文件是否存在
    if (!fs.existsSync(configPath)) {
      return NextResponse.json({ error: '配置文件不存在' }, { status: 404 });
    }
    
    // 读取配置文件，检查是否有欧路词典令牌
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    
    if (!configData.EUDIC_TOKEN) {
      return NextResponse.json({ error: '未配置欧路词典令牌' }, { status: 400 });
    }
    
    // 更新配置文件中的欧路词典ID
    configData.EUDIC_ID = id;
    fs.writeFileSync(configPath, JSON.stringify(configData, null, 2), 'utf-8');
    
    // 执行Python命令从欧路词典导入生词
    const { stdout, stderr } = await execAsync('python -m anki_packager.cli --eudic', { cwd: projectRoot });
    
    if (stderr && !stderr.includes('INFO:')) {
      return NextResponse.json({
        error: '从欧路词典导入生词失败',
        details: stderr
      }, { status: 500 });
    }
    
    // 解析输出以获取导入的单词数量
    const match = stdout.match(/已导入\s+(\d+)\s+个单词/);
    const importedWords = match ? parseInt(match[1]) : 0;
    
    // 读取词汇表，获取实际单词数量
    let wordCount = 0;
    if (fs.existsSync(vocabularyPath)) {
      const vocabulary = fs.readFileSync(vocabularyPath, 'utf-8')
        .split('\n')
        .map(line => line.trim())
        .filter(line => line);
      wordCount = vocabulary.length;
    }
    
    return NextResponse.json({
      success: true,
      message: `已从欧路词典导入 ${importedWords} 个单词`,
      details: {
        id,
        importedWords,
        totalWords: wordCount,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('导入生词失败:', error);
    return NextResponse.json({
      error: '导入生词失败',
      details: (error as Error).message
    }, { status: 500 });
  }
} 