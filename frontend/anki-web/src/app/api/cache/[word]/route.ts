import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import path from 'path';

const execAsync = util.promisify(exec);
const projectRoot = 'D:\\Code\\anki_packager';

export async function GET(
  request: Request,
  { params }: { params: { word: string } }
) {
  const word = params.word;
  
  try {
    // 执行Python命令获取缓存统计信息
    const { stdout } = await execAsync('python -m anki_packager.cli --list-cache', { cwd: projectRoot });
    
    // 解析输出查找特定单词的缓存
    const lines = stdout.trim().split('\n');
    let found = false;
    
    for (const line of lines) {
      if (line.match(new RegExp(`^\\d+\\.\\s+${word}\\b`, 'i'))) {
        found = true;
        break;
      }
    }
    
    if (!found) {
      return NextResponse.json({ error: '缓存不存在' }, { status: 404 });
    }
    
    // 如果找到了缓存，返回基本信息
    return NextResponse.json({
      word,
      source: 'ai',
      size: 0, // 实际大小需要更精确的方法获取
      createdAt: new Date().toISOString(),
      lastAccessed: new Date().toISOString()
    });
  } catch (error) {
    console.error(`获取单词 ${word} 的缓存失败:`, error);
    return NextResponse.json({ error: '获取缓存失败' }, { status: 500 });
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { word: string } }
) {
  const word = params.word;
  
  try {
    // 执行Python命令删除特定单词的缓存
    const { stdout } = await execAsync(`python -m anki_packager.cli --delete-cache "${word}"`, { cwd: projectRoot });
    
    // 检查是否成功删除
    if (stdout.includes('成功删除') || stdout.includes('已删除')) {
      return NextResponse.json({ 
        success: true,
        message: `已删除单词 ${word} 的缓存`,
        word
      });
    } else {
      return NextResponse.json({ error: '缓存不存在或删除失败' }, { status: 404 });
    }
  } catch (error) {
    console.error(`删除单词 ${word} 的缓存失败:`, error);
    return NextResponse.json({ error: '删除缓存失败' }, { status: 500 });
  }
} 