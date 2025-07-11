import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import path from 'path';
import fs from 'fs';

const execAsync = util.promisify(exec);
const projectRoot = 'D:\\Code\\anki_packager';
const audioDir = path.join(projectRoot, 'audio');

// 获取所有音频
export async function GET() {
  try {
    // 执行Python命令获取音频文件列表
    const { stdout } = await execAsync('python -m anki_packager.cli --list-audio', { cwd: projectRoot });
    
    // 解析输出
    const lines = stdout.trim().split('\n');
    const audioFiles = [];
    
    for (const line of lines) {
      if (line.includes('音频文件列表:') || line.includes('音频文件夹为空')) {
        continue;
      }
      
      const match = line.match(/^\d+\.\s+(.+?)(?:\s+\((\d+)\s*[KB|MB]\))?$/);
      if (match) {
        const word = match[1].trim();
        const filePath = path.join(audioDir, `${word}.mp3`);
        
        let size = 0;
        let createdAt = new Date().toISOString();
        
        // 尝试获取文件的实际大小和创建时间
        try {
          if (fs.existsSync(filePath)) {
            const stats = fs.statSync(filePath);
            size = stats.size;
            createdAt = stats.birthtime.toISOString();
          }
        } catch (err) {
          console.error(`获取文件 ${filePath} 信息失败:`, err);
        }
        
        audioFiles.push({
          word,
          url: `/audio/${word}.mp3`,
          size,
          createdAt
        });
      }
    }
    
    return NextResponse.json(audioFiles);
  } catch (error) {
    console.error('获取音频列表失败:', error);
    return NextResponse.json({ error: '获取音频列表失败' }, { status: 500 });
  }
}

// 删除所有音频
export async function DELETE() {
  try {
    // 执行Python命令删除所有音频文件
    const { stdout } = await execAsync('python -m anki_packager.cli --clear-audio', { cwd: projectRoot });
    
    // 解析输出以获取删除的数量
    const match = stdout.match(/已删除\s+(\d+)\s+个音频文件/);
    const count = match ? parseInt(match[1]) : 0;
    
    return NextResponse.json({ 
      success: true,
      message: '已删除所有音频文件',
      count
    });
  } catch (error) {
    console.error('删除音频文件失败:', error);
    return NextResponse.json({ error: '删除音频文件失败' }, { status: 500 });
  }
}

// 清理孤立音频
export async function POST(request: Request) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action');
  
  if (action === 'cleanup') {
    try {
      // 执行Python命令清理孤立音频文件
      const { stdout } = await execAsync('python -m anki_packager.cli --cleanup-audio', { cwd: projectRoot });
      
      // 解析输出以获取清理的数量
      const match = stdout.match(/已清理\s+(\d+)\s+个孤立音频文件/);
      const cleanedCount = match ? parseInt(match[1]) : 0;
      
      return NextResponse.json({
        success: true,
        message: `已清理 ${cleanedCount} 个孤立音频文件`,
        cleanedCount
      });
    } catch (error) {
      console.error('清理音频文件失败:', error);
      return NextResponse.json({ error: '清理音频文件失败' }, { status: 500 });
    }
  }
  
  return NextResponse.json({ 
    error: '不支持的操作' 
  }, { status: 400 });
} 