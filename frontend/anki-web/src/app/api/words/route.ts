import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { execPythonCommand, getProjectRoot, ensureConfigDir, formatErrorResponse } from '@/lib/utils';

const projectRoot = getProjectRoot();
const vocabularyPath = path.join(projectRoot, 'config', 'vocabulary.txt');

// 获取所有单词
export async function GET() {
  try {
    // 执行Python命令获取单词列表
    const stdout = await execPythonCommand('python -m anki_packager.cli --list-words');
    
    // 解析输出
    const lines = stdout.trim().split('\n');
    const words = [];
    
    for (const line of lines) {
      if (line.includes('词汇表中共有') || line.includes('词汇表为空')) {
        continue;
      }
      
      const match = line.match(/^\s*\d+\.\s+(.+)$/);
      if (match) {
        const word = match[1].trim();
        words.push({
          word,
          addedAt: new Date().toISOString() // 无法从命令行输出获取添加时间
        });
      }
    }
    
    return NextResponse.json(words);
  } catch (error: unknown) {
    return NextResponse.json(
      formatErrorResponse(error, '获取单词列表失败'),
      { status: 500 }
    );
  }
}

// 添加单词
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { word } = body;
    
    if (!word) {
      return NextResponse.json({ error: '缺少必要参数: word' }, { status: 400 });
    }
    
    // 执行Python命令添加单词
    const stdout = await execPythonCommand(`python -m anki_packager.cli --word "${word}"`);
    
    // 检查是否成功添加
    if (stdout.includes('已添加到生词本') || stdout.includes('添加成功')) {
      return NextResponse.json({
        success: true,
        message: `已添加单词: ${word}`,
        word,
        addedAt: new Date().toISOString()
      });
    } else if (stdout.includes('已存在于生词本')) {
      return NextResponse.json({
        success: false,
        message: `单词 ${word} 已存在于生词本`,
        word
      }, { status: 409 });
    } else {
      return NextResponse.json({
        success: false,
        message: '添加单词失败',
        word
      }, { status: 500 });
    }
  } catch (error: unknown) {
    return NextResponse.json(
      formatErrorResponse(error, '添加单词失败'),
      { status: 500 }
    );
  }
}

// 批量添加单词
export async function PUT(request: Request) {
  try {
    const body = await request.json();
    const { words } = body;
    
    if (!words || !Array.isArray(words) || words.length === 0) {
      return NextResponse.json({ error: '缺少必要参数: words' }, { status: 400 });
    }
    
    // 确保配置目录存在
    ensureConfigDir();
    
    // 读取现有单词
    let existingWords: string[] = [];
    if (fs.existsSync(vocabularyPath)) {
      existingWords = fs.readFileSync(vocabularyPath, 'utf-8')
        .split('\n')
        .map(line => line.trim())
        .filter(line => line);
    }
    
    // 添加新单词
    const newWords = words.filter(word => !existingWords.includes(word));
    const allWords = [...existingWords, ...newWords];
    
    // 写入文件
    fs.writeFileSync(vocabularyPath, allWords.join('\n') + '\n', 'utf-8');
    
    return NextResponse.json({
      success: true,
      message: `已添加 ${newWords.length} 个新单词`,
      addedWords: newWords,
      totalWords: allWords.length
    });
  } catch (error: unknown) {
    return NextResponse.json(
      formatErrorResponse(error, '批量添加单词失败'),
      { status: 500 }
    );
  }
} 