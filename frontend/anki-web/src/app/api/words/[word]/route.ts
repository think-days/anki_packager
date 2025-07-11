import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = util.promisify(exec);
const projectRoot = 'D:\\Code\\anki_packager';
const vocabularyPath = path.join(projectRoot, 'config', 'vocabulary.txt');
const audioDir = path.join(projectRoot, 'audio');
const cacheDir = path.join(projectRoot, 'config', 'cache');

export async function GET(
  request: Request,
  { params }: { params: { word: string } }
) {
  const word = params.word;
  
  try {
    // 检查单词是否在词汇表中
    const vocabularyExists = fs.existsSync(vocabularyPath);
    if (!vocabularyExists) {
      return NextResponse.json({ error: '词汇表不存在' }, { status: 404 });
    }
    
    const vocabulary = fs.readFileSync(vocabularyPath, 'utf-8')
      .split('\n')
      .map(line => line.trim())
      .filter(line => line);
    
    if (!vocabulary.includes(word)) {
      return NextResponse.json({ error: '单词不存在' }, { status: 404 });
    }
    
    // 检查是否有音频文件
    const audioExists = fs.existsSync(path.join(audioDir, `${word}.mp3`));
    
    // 检查是否有缓存
    const cacheFile = path.join(cacheDir, 'ai_cache.json');
    let hasCache = false;
    if (fs.existsSync(cacheFile)) {
      try {
        const cacheData = JSON.parse(fs.readFileSync(cacheFile, 'utf-8'));
        hasCache = cacheData && cacheData[word];
      } catch (err) {
        console.error('读取缓存文件失败:', err);
      }
    }
    
    // 构建单词详细信息
    const wordDetails = {
      word,
      hasAudio: audioExists,
      hasCache: hasCache,
      lastUpdated: new Date().toISOString().split('T')[0],
      // 以下信息需要从实际词典中获取，这里只是占位
      phonetic: '/未知/',
      definitions: [],
      examples: [],
      synonyms: [],
      antonyms: []
    };
    
    return NextResponse.json(wordDetails);
  } catch (error) {
    console.error(`获取单词 ${word} 详情失败:`, error);
    return NextResponse.json({ error: '获取单词详情失败' }, { status: 500 });
  }
}

export async function DELETE(
  request: Request,
  { params }: { params: { word: string } }
) {
  const word = params.word;
  
  try {
    // 执行Python命令删除单词及其所有资源
    const { stdout } = await execAsync(`python -m anki_packager.cli --delete-word-completely "${word}"`, { cwd: projectRoot });
    
    // 检查是否成功删除
    if (stdout.includes('成功删除') || stdout.includes('已删除')) {
      return NextResponse.json({ 
        success: true,
        message: `已删除单词 ${word} 及其所有资源`,
        word
      });
    } else {
      return NextResponse.json({ error: '单词不存在或删除失败' }, { status: 404 });
    }
  } catch (error) {
    console.error(`删除单词 ${word} 失败:`, error);
    return NextResponse.json({ error: '删除单词失败' }, { status: 500 });
  }
} 