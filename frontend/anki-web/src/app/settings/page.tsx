'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AppLayout from '@/components/layouts/app-layout';
import { settingsApi } from '@/lib/api';

interface Settings {
  basic: {
    cardStyle: string;
    language: string;
    autoDownloadAudio: boolean;
    maxWordsPerDeck: number;
  };
  dictionaries: {
    ecdict: boolean;
    youdao: boolean;
    longman: boolean;
    eudic: boolean;
    stardict: boolean;
  };
  ai: {
    enabled: boolean;
    model: string;
    apiKey: string;
    temperature: number;
    maxTokens: number;
  };
  audio: {
    source: string;
    autoCleanup: boolean;
    maxCacheSize: number;
  };
  export: {
    format: string;
    includeTags: boolean;
    includeAudio: boolean;
    includeImages: boolean;
  };
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('basic');

  // 加载设置
  useEffect(() => {
    async function loadSettings() {
      try {
        setLoading(true);
        const settingsData = await settingsApi.getSettings();
        setSettings(settingsData);
        setError(null);
      } catch (err) {
        console.error('加载设置失败:', err);
        setError('加载设置失败');
      } finally {
        setLoading(false);
      }
    }

    loadSettings();
  }, []);

  // 保存设置
  const handleSaveSettings = async () => {
    if (!settings) return;

    try {
      setSaving(true);
      await settingsApi.updateSettings(settings);
      alert('设置已保存');
    } catch (err) {
      console.error('保存设置失败:', err);
      alert('保存设置失败');
    } finally {
      setSaving(false);
    }
  };

  // 更新设置字段
  const updateSetting = (section: keyof Settings, field: string, value: any) => {
    if (!settings) return;

    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [field]: value
      }
    });
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="container mx-auto p-4">
          <h1 className="text-2xl font-bold mb-6">设置</h1>
          <p className="text-muted-foreground">加载中...</p>
        </div>
      </AppLayout>
    );
  }

  if (error || !settings) {
    return (
      <AppLayout>
        <div className="container mx-auto p-4">
          <h1 className="text-2xl font-bold mb-6">设置</h1>
          <p className="text-destructive">{error || '加载设置时出错'}</p>
          <Button onClick={() => window.location.reload()}>重试</Button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">设置</h1>
          <Button onClick={handleSaveSettings} disabled={saving}>
            {saving ? '保存中...' : '保存设置'}
          </Button>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList>
            <TabsTrigger value="basic">基础设置</TabsTrigger>
            <TabsTrigger value="dictionaries">词典设置</TabsTrigger>
            <TabsTrigger value="ai">AI设置</TabsTrigger>
            <TabsTrigger value="audio">音频设置</TabsTrigger>
            <TabsTrigger value="export">导出设置</TabsTrigger>
          </TabsList>

          {/* 基础设置 */}
          <TabsContent value="basic" className="space-y-4">
            <div className="grid gap-6">
              <div className="space-y-2">
                <Label htmlFor="cardStyle">卡片样式</Label>
                <Input
                  id="cardStyle"
                  value={settings.basic.cardStyle}
                  onChange={(e) => updateSetting('basic', 'cardStyle', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="language">界面语言</Label>
                <select
                  id="language"
                  className="w-full p-2 border rounded-md"
                  value={settings.basic.language}
                  onChange={(e) => updateSetting('basic', 'language', e.target.value)}
                >
                  <option value="zh_CN">简体中文</option>
                  <option value="en_US">English</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="autoDownloadAudio">自动下载音频</Label>
                <Switch
                  id="autoDownloadAudio"
                  checked={settings.basic.autoDownloadAudio}
                  onCheckedChange={(checked) => updateSetting('basic', 'autoDownloadAudio', checked)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxWordsPerDeck">每个牌组最大单词数</Label>
                <Input
                  id="maxWordsPerDeck"
                  type="number"
                  value={settings.basic.maxWordsPerDeck}
                  onChange={(e) => updateSetting('basic', 'maxWordsPerDeck', parseInt(e.target.value))}
                />
              </div>
            </div>
          </TabsContent>

          {/* 词典设置 */}
          <TabsContent value="dictionaries" className="space-y-4">
            <div className="grid gap-4">
              {Object.entries(settings.dictionaries).map(([dict, enabled]) => (
                <div key={dict} className="flex items-center justify-between">
                  <Label htmlFor={`dict-${dict}`}>启用 {dict}</Label>
                  <Switch
                    id={`dict-${dict}`}
                    checked={enabled}
                    onCheckedChange={(checked) => updateSetting('dictionaries', dict, checked)}
                  />
                </div>
              ))}
            </div>
          </TabsContent>

          {/* AI设置 */}
          <TabsContent value="ai" className="space-y-4">
            <div className="grid gap-6">
              <div className="flex items-center justify-between">
                <Label htmlFor="aiEnabled">启用AI</Label>
                <Switch
                  id="aiEnabled"
                  checked={settings.ai.enabled}
                  onCheckedChange={(checked) => updateSetting('ai', 'enabled', checked)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="aiModel">AI模型</Label>
                <select
                  id="aiModel"
                  className="w-full p-2 border rounded-md"
                  value={settings.ai.model}
                  onChange={(e) => updateSetting('ai', 'model', e.target.value)}
                >
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-4">GPT-4</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="apiKey">API密钥</Label>
                <Input
                  id="apiKey"
                  type="password"
                  value={settings.ai.apiKey}
                  onChange={(e) => updateSetting('ai', 'apiKey', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="temperature">温度 ({settings.ai.temperature})</Label>
                <input
                  id="temperature"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.ai.temperature}
                  onChange={(e) => updateSetting('ai', 'temperature', parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxTokens">最大令牌数</Label>
                <Input
                  id="maxTokens"
                  type="number"
                  value={settings.ai.maxTokens}
                  onChange={(e) => updateSetting('ai', 'maxTokens', parseInt(e.target.value))}
                />
              </div>
            </div>
          </TabsContent>

          {/* 音频设置 */}
          <TabsContent value="audio" className="space-y-4">
            <div className="grid gap-6">
              <div className="space-y-2">
                <Label htmlFor="audioSource">音频来源</Label>
                <select
                  id="audioSource"
                  className="w-full p-2 border rounded-md"
                  value={settings.audio.source}
                  onChange={(e) => updateSetting('audio', 'source', e.target.value)}
                >
                  <option value="youdao">有道</option>
                  <option value="google">Google</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="autoCleanup">自动清理孤立音频</Label>
                <Switch
                  id="autoCleanup"
                  checked={settings.audio.autoCleanup}
                  onCheckedChange={(checked) => updateSetting('audio', 'autoCleanup', checked)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxCacheSize">最大缓存大小 (MB)</Label>
                <Input
                  id="maxCacheSize"
                  type="number"
                  value={settings.audio.maxCacheSize}
                  onChange={(e) => updateSetting('audio', 'maxCacheSize', parseInt(e.target.value))}
                />
              </div>
            </div>
          </TabsContent>

          {/* 导出设置 */}
          <TabsContent value="export" className="space-y-4">
            <div className="grid gap-6">
              <div className="space-y-2">
                <Label htmlFor="exportFormat">导出格式</Label>
                <select
                  id="exportFormat"
                  className="w-full p-2 border rounded-md"
                  value={settings.export.format}
                  onChange={(e) => updateSetting('export', 'format', e.target.value)}
                >
                  <option value="apkg">Anki (.apkg)</option>
                  <option value="csv">CSV 文件 (.csv)</option>
                  <option value="txt">文本文件 (.txt)</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="includeTags">包含标签</Label>
                <Switch
                  id="includeTags"
                  checked={settings.export.includeTags}
                  onCheckedChange={(checked) => updateSetting('export', 'includeTags', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="includeAudio">包含音频</Label>
                <Switch
                  id="includeAudio"
                  checked={settings.export.includeAudio}
                  onCheckedChange={(checked) => updateSetting('export', 'includeAudio', checked)}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="includeImages">包含图片</Label>
                <Switch
                  id="includeImages"
                  checked={settings.export.includeImages}
                  onCheckedChange={(checked) => updateSetting('export', 'includeImages', checked)}
                />
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
} 