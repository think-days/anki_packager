import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { execPythonCommand, getProjectRoot, formatErrorResponse } from '@/lib/utils';

const projectRoot = getProjectRoot();
const audioDir = path.join(projectRoot, 'audio');
const cacheDir = path.join(projectRoot, 'config', 'cache');

export async function GET() {
  try {
    // 执行Python命令获取统计信息
    const stdout = await execPythonCommand('python -m anki_packager.cli --stats');
    
    // 解析输出
    let wordCount = 0;
    let audioCount = 0;
    let cacheCount = 0;
    let orphanedAudioCount = 0;
    let orphanedCacheCount = 0;
    let missingAudioCount = 0;
    
    const lines = stdout.trim().split('\n');
    for (const line of lines) {
      const wordMatch = line.match(/词汇表中共有\s+(\d+)\s+个单词/);
      if (wordMatch) {
        wordCount = parseInt(wordMatch[1]);
        continue;
      }
      
      const audioMatch = line.match(/音频文件夹中共有\s+(\d+)\s+个音频文件/);
      if (audioMatch) {
        audioCount = parseInt(audioMatch[1]);
        continue;
      }
      
      const cacheMatch = line.match(/AI缓存中共有\s+(\d+)\s+个缓存条目/);
      if (cacheMatch) {
        cacheCount = parseInt(cacheMatch[1]);
        continue;
      }
      
      const orphanedAudioMatch = line.match(/孤立音频文件数量：\s+(\d+)/);
      if (orphanedAudioMatch) {
        orphanedAudioCount = parseInt(orphanedAudioMatch[1]);
        continue;
      }
      
      const orphanedCacheMatch = line.match(/孤立缓存条目数量：\s+(\d+)/);
      if (orphanedCacheMatch) {
        orphanedCacheCount = parseInt(orphanedCacheMatch[1]);
        continue;
      }
      
      const missingAudioMatch = line.match(/缺失音频的单词数量：\s+(\d+)/);
      if (missingAudioMatch) {
        missingAudioCount = parseInt(missingAudioMatch[1]);
        continue;
      }
    }
    
    // 获取文件夹大小
    const getDirectorySize = (dirPath: string): number => {
      if (!fs.existsSync(dirPath)) return 0;
      
      let size = 0;
      const files = fs.readdirSync(dirPath);
      
      for (const file of files) {
        const filePath = path.join(dirPath, file);
        const stats = fs.statSync(filePath);
        
        if (stats.isDirectory()) {
          size += getDirectorySize(filePath);
        } else {
          size += stats.size;
        }
      }
      
      return size;
    };
    
    const audioSize = getDirectorySize(audioDir);
    const cacheSize = getDirectorySize(cacheDir);
    
    // 构建统计信息
    const stats = {
      words: {
        total: wordCount,
        withAudio: wordCount - missingAudioCount,
        withCache: cacheCount - orphanedCacheCount,
        withBoth: wordCount - missingAudioCount - (orphanedCacheCount > 0 ? orphanedCacheCount : 0),
      },
      audio: {
        total: audioCount,
        orphaned: orphanedAudioCount,
        sizeKB: Math.round(audioSize / 1024),
      },
      cache: {
        total: cacheCount,
        orphaned: orphanedCacheCount,
        sizeKB: Math.round(cacheSize / 1024),
      },
      lastUpdated: new Date().toISOString(),
    };
    
    return NextResponse.json(stats);
  } catch (error: unknown) {
    return NextResponse.json(
      formatErrorResponse(error, '获取统计信息失败'),
      { status: 500 }
    );
  }
} 