import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import path from 'path';

const execAsync = util.promisify(exec);
const projectRoot = path.resolve(process.cwd(), '../../..');

// 获取所有缓存
export async function GET() {
  try {
    console.log('Project root:', projectRoot);
    // 执行Python命令获取缓存统计信息
    const { stdout } = await execAsync('python -m anki_packager.cli --list-cache', { cwd: projectRoot });
    
    // 解析输出
    const lines = stdout.trim().split('\n');
    const cacheEntries = [];
    
    let currentWord = '';
    let currentSource = '';
    let currentSize = 0;
    let currentCreatedAt = '';
    
    for (const line of lines) {
      if (line.includes('缓存统计信息:')) {
        continue;
      }
      
      if (line.match(/^\d+\.\s+(\w+)/)) {
        // 这是一个单词行
        const match = line.match(/^\d+\.\s+(\w+)/);
        if (match) {
          currentWord = match[1];
          cacheEntries.push({
            word: currentWord,
            source: 'ai',
            size: 0, // 默认大小，后续可能会更新
            createdAt: new Date().toISOString(),
            lastAccessed: new Date().toISOString()
          });
        }
      }
    }
    
    return NextResponse.json(cacheEntries);
  } catch (error) {
    console.error('获取缓存失败:', error);
    return NextResponse.json({ error: '获取缓存失败' }, { status: 500 });
  }
}

// 删除所有缓存
export async function DELETE() {
  try {
    // 执行Python命令清空所有缓存
    const { stdout } = await execAsync('python -m anki_packager.cli --clear-cache', { cwd: projectRoot });
    
    // 解析输出以获取删除的数量
    const match = stdout.match(/已删除\s+(\d+)\s+个缓存条目/);
    const count = match ? parseInt(match[1]) : 0;
    
    return NextResponse.json({ 
      success: true,
      message: `已删除所有缓存`,
      count
    });
  } catch (error) {
    console.error('删除缓存失败:', error);
    return NextResponse.json({ error: '删除缓存失败' }, { status: 500 });
  }
}

// 清理孤立缓存
export async function POST(request: Request) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action');
  
  if (action === 'cleanup') {
    try {
      // 执行Python命令清理孤立缓存
      const { stdout } = await execAsync('python -m anki_packager.cli --cleanup-cache', { cwd: projectRoot });
      
      // 解析输出以获取清理的数量
      const match = stdout.match(/已清理\s+(\d+)\s+个孤立缓存/);
      const cleanedCount = match ? parseInt(match[1]) : 0;
      
      return NextResponse.json({
        success: true,
        message: `已清理 ${cleanedCount} 个孤立缓存`,
        cleanedCount
      });
    } catch (error) {
      console.error('清理缓存失败:', error);
      return NextResponse.json({ error: '清理缓存失败' }, { status: 500 });
    }
  }
  
  return NextResponse.json({ 
    error: '不支持的操作' 
  }, { status: 400 });
} 