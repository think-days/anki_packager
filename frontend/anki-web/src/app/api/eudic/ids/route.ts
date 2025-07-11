import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = util.promisify(exec);
const projectRoot = 'D:\\Code\\anki_packager';
const configPath = path.join(projectRoot, 'config', 'config.json');

// 获取欧路词典生词本ID列表
export async function GET() {
  try {
    // 检查配置文件是否存在
    if (!fs.existsSync(configPath)) {
      return NextResponse.json({ error: '配置文件不存在' }, { status: 404 });
    }
    
    // 读取配置文件，检查是否有欧路词典令牌
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    
    if (!configData.EUDIC_TOKEN) {
      return NextResponse.json({ error: '未配置欧路词典令牌' }, { status: 400 });
    }
    
    // 执行Python命令获取欧路词典生词本ID列表
    const { stdout, stderr } = await execAsync('python -m anki_packager.cli --eudicid', { cwd: projectRoot });
    
    if (stderr && !stderr.includes('INFO:')) {
      return NextResponse.json({
        error: '获取欧路词典生词本ID列表失败',
        details: stderr
      }, { status: 500 });
    }
    
    // 解析输出
    const lines = stdout.trim().split('\n');
    const eudicIds = [];
    
    for (const line of lines) {
      // 格式可能是：ID: 123456, 名称: 英语四级词汇, 单词数: 2500
      const match = line.match(/ID:\s+(\d+),\s+名称:\s+(.+?),\s+单词数:\s+(\d+)/);
      if (match) {
        eudicIds.push({
          id: match[1],
          name: match[2],
          wordCount: parseInt(match[3]),
          lastUpdated: new Date().toISOString() // 无法从命令行输出获取更新时间
        });
      }
    }
    
    return NextResponse.json(eudicIds);
  } catch (error) {
    console.error('获取欧路词典生词本ID列表失败:', error);
    return NextResponse.json({ error: '获取欧路词典生词本ID列表失败' }, { status: 500 });
  }
} 