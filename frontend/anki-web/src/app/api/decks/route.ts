import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const projectRoot = 'D:\\Code\\anki_packager';

// 获取牌组列表
export async function GET() {
  try {
    const decks = [];
    
    // 扫描项目根目录中的 .apkg 文件
    const files = fs.readdirSync(projectRoot);
    
    for (const file of files) {
      if (file.endsWith('.apkg')) {
        const filePath = path.join(projectRoot, file);
        const stats = fs.statSync(filePath);
        
        // 从文件名中提取牌组名称（去掉 .apkg 扩展名）
        const name = file.slice(0, -5);
        
        // 估算单词数量（实际情况下无法准确获取，除非解析 .apkg 文件）
        const estimatedWordCount = Math.round(stats.size / 10240); // 假设每个单词平均 10KB
        
        decks.push({
          id: Buffer.from(name).toString('base64'),
          name,
          wordCount: estimatedWordCount,
          createdAt: stats.birthtime.toISOString(),
          lastModified: stats.mtime.toISOString(),
          size: stats.size
        });
      }
    }
    
    return NextResponse.json(decks);
  } catch (error) {
    console.error('获取牌组列表失败:', error);
    return NextResponse.json({ error: '获取牌组列表失败' }, { status: 500 });
  }
} 