import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import path from 'path';
import fs from 'fs';

const execAsync = util.promisify(exec);
const projectRoot = 'D:\\Code\\anki_packager';
const audioDir = path.join(projectRoot, 'audio');

export async function GET(
  request: Request,
  { params }: { params: { word: string } }
) {
  const word = params.word;
  const filePath = path.join(audioDir, `${word}.mp3`);
  
  try {
    // 检查文件是否存在
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: '音频不存在' }, { status: 404 });
    }
    
    // 获取文件信息
    const stats = fs.statSync(filePath);
    
    return NextResponse.json({
      word,
      url: `/audio/${word}.mp3`,
      size: stats.size,
      createdAt: stats.birthtime.toISOString()
    });
  } catch (error) {
    console.error(`获取单词 ${word} 的音频失败:`, error);
    return NextResponse.json({ error: '获取音频失败' }, { status: 500 });
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { word: string } }
) {
  const word = params.word;
  
  try {
    // 执行Python命令删除特定单词的音频
    const { stdout } = await execAsync(`python -m anki_packager.cli --delete-audio "${word}"`, { cwd: projectRoot });
    
    // 检查是否成功删除
    if (stdout.includes('成功删除') || stdout.includes('已删除')) {
      return NextResponse.json({ 
        success: true,
        message: `已删除单词 ${word} 的音频文件`,
        word
      });
    } else {
      return NextResponse.json({ error: '音频不存在或删除失败' }, { status: 404 });
    }
  } catch (error) {
    console.error(`删除单词 ${word} 的音频失败:`, error);
    return NextResponse.json({ error: '删除音频失败' }, { status: 500 });
  }
} 