import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = util.promisify(exec);
const projectRoot = 'D:\\Code\\anki_packager';

// 系统重置
export async function POST() {
  try {
    // 执行Python命令重置系统
    const { stdout, stderr } = await execAsync('python -m anki_packager.cli --reset-all', { cwd: projectRoot });
    
    if (stderr && !stderr.includes('INFO:')) {
      return NextResponse.json({
        error: '系统重置失败',
        details: stderr
      }, { status: 500 });
    }
    
    // 解析输出以获取重置结果
    const resetItems = {
      words: stdout.includes('已清空词汇表'),
      audio: stdout.includes('已删除所有音频文件'),
      cache: stdout.includes('已清空AI缓存'),
      decks: false // 默认为false，因为后端可能没有直接提示删除牌组
    };
    
    // 检查是否删除了牌组文件
    const files = fs.readdirSync(projectRoot);
    const apkgFiles = files.filter(file => file.endsWith('.apkg'));
    
    if (apkgFiles.length === 0) {
      resetItems.decks = true;
    } else {
      // 尝试删除所有牌组文件
      for (const file of apkgFiles) {
        try {
          fs.unlinkSync(path.join(projectRoot, file));
          resetItems.decks = true;
        } catch (err) {
          console.error(`删除牌组文件 ${file} 失败:`, err);
        }
      }
    }
    
    return NextResponse.json({
      success: true,
      message: '系统已完全重置',
      details: {
        timestamp: new Date().toISOString(),
        resetItems
      }
    });
  } catch (error) {
    console.error('系统重置失败:', error);
    return NextResponse.json({
      error: '系统重置失败',
      details: (error as Error).message
    }, { status: 500 });
  }
} 