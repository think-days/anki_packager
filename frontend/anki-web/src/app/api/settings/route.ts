import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

const projectRoot = 'D:\\Code\\anki_packager';
const configPath = path.join(projectRoot, 'config', 'config.json');

// 获取设置
export async function GET() {
  try {
    // 检查配置文件是否存在
    if (!fs.existsSync(configPath)) {
      return NextResponse.json({ error: '配置文件不存在' }, { status: 404 });
    }
    
    // 读取配置文件
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    
    // 构建设置对象
    const settings = {
      // 基础设置
      basic: {
        cardStyle: 'default',
        language: 'zh_CN',
        autoDownloadAudio: true,
        maxWordsPerDeck: 100,
      },
      // 词典设置
      dictionaries: {
        ecdict: true,
        youdao: true,
        longman: true,
        eudic: configData.EUDIC_TOKEN ? true : false,
        stardict: false
      },
      // AI设置
      ai: {
        enabled: configData.API_KEY ? true : false,
        model: configData.MODEL || 'Pro/deepseek-ai/DeepSeek-V3',
        apiKey: configData.API_KEY ? configData.API_KEY.replace(/^(sk-).{3}(.*)$/, '$1***$2') : '',
        temperature: 0.7,
        maxTokens: 500
      },
      // 音频设置
      audio: {
        source: 'youdao',
        autoCleanup: true,
        maxCacheSize: 100 // MB
      },
      // 导出设置
      export: {
        format: 'apkg',
        includeTags: true,
        includeAudio: true,
        includeImages: true
      },
      // 欧路词典设置
      eudic: {
        token: configData.EUDIC_TOKEN ? configData.EUDIC_TOKEN.replace(/^(.{3})(.*)(.{3})$/, '$1***$3') : '',
        id: configData.EUDIC_ID || '0'
      },
      // 代理设置
      proxy: {
        enabled: configData.PROXY ? true : false,
        url: configData.PROXY || '',
        apiBase: configData.API_BASE || 'https://api.siliconflow.cn'
      },
      // 牌组设置
      deck: {
        name: configData.DECK_NAME || 'anki-packager'
      }
    };
    
    return NextResponse.json(settings);
  } catch (error) {
    console.error('获取设置失败:', error);
    return NextResponse.json({ error: '获取设置失败' }, { status: 500 });
  }
}

// 更新设置
export async function PUT(request: Request) {
  try {
    const body = await request.json();
    
    // 检查配置文件是否存在
    if (!fs.existsSync(configPath)) {
      return NextResponse.json({ error: '配置文件不存在' }, { status: 404 });
    }
    
    // 读取现有配置
    const configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
    
    // 更新配置
    if (body.ai && body.ai.apiKey && !body.ai.apiKey.includes('***')) {
      configData.API_KEY = body.ai.apiKey;
    }
    
    if (body.ai && body.ai.model) {
      configData.MODEL = body.ai.model;
    }
    
    if (body.proxy) {
      if (body.proxy.enabled && body.proxy.url) {
        configData.PROXY = body.proxy.url;
      } else if (!body.proxy.enabled) {
        configData.PROXY = '';
      }
      
      if (body.proxy.apiBase) {
        configData.API_BASE = body.proxy.apiBase;
      }
    }
    
    if (body.eudic) {
      if (body.eudic.token && !body.eudic.token.includes('***')) {
        configData.EUDIC_TOKEN = body.eudic.token;
      }
      
      if (body.eudic.id) {
        configData.EUDIC_ID = body.eudic.id;
      }
    }
    
    if (body.deck && body.deck.name) {
      configData.DECK_NAME = body.deck.name;
    }
    
    // 保存配置
    fs.writeFileSync(configPath, JSON.stringify(configData, null, 2), 'utf-8');
    
    // 返回更新后的设置
    return NextResponse.json({
      success: true,
      message: '设置已更新',
      settings: await GET().then(res => res.json())
    });
  } catch (error) {
    console.error('更新设置失败:', error);
    return NextResponse.json({
      error: '更新设置失败',
      details: (error as Error).message
    }, { status: 500 });
  }
} 