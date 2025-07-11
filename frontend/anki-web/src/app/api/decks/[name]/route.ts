import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const projectRoot = 'D:\\Code\\anki_packager';

export async function GET(
  request: Request,
  { params }: { params: { name: string } }
) {
  const name = params.name;
  const apkgFile = path.join(projectRoot, `${name}.apkg`);
  
  try {
    // 检查文件是否存在
    if (!fs.existsSync(apkgFile)) {
      return NextResponse.json({ error: '牌组不存在' }, { status: 404 });
    }
    
    // 获取文件信息
    const stats = fs.statSync(apkgFile);
    
    // 估算单词数量（实际情况下无法准确获取，除非解析 .apkg 文件）
    const estimatedWordCount = Math.round(stats.size / 10240); // 假设每个单词平均 10KB
    
    return NextResponse.json({
      id: Buffer.from(name).toString('base64'),
      name,
      wordCount: estimatedWordCount,
      createdAt: stats.birthtime.toISOString(),
      lastModified: stats.mtime.toISOString(),
      size: stats.size
    });
  } catch (error) {
    console.error(`获取牌组 ${name} 详情失败:`, error);
    return NextResponse.json({ error: '获取牌组详情失败' }, { status: 500 });
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { name: string } }
) {
  const name = params.name;
  const apkgFile = path.join(projectRoot, `${name}.apkg`);
  
  try {
    // 检查文件是否存在
    if (!fs.existsSync(apkgFile)) {
      return NextResponse.json({ error: '牌组不存在' }, { status: 404 });
    }
    
    // 删除文件
    fs.unlinkSync(apkgFile);
    
    return NextResponse.json({ 
      success: true,
      message: `已删除牌组 ${name}`,
      name
    });
  } catch (error) {
    console.error(`删除牌组 ${name} 失败:`, error);
    return NextResponse.json({ error: '删除牌组失败' }, { status: 500 });
  }
} 