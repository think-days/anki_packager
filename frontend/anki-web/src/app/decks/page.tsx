'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import AppLayout from '@/components/layouts/app-layout';
import { deckApi } from '@/lib/api';

interface Deck {
  id: string;
  name: string;
  wordCount: number;
  createdAt: string;
  lastModified: string;
  size: number;
}

export default function DecksPage() {
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newDeckName, setNewDeckName] = useState('');
  const [generating, setGenerating] = useState(false);

  // 加载牌组列表
  useEffect(() => {
    async function loadDecks() {
      try {
        setLoading(true);
        const decksData = await deckApi.getDecks();
        setDecks(decksData);
        setError(null);
      } catch (err) {
        console.error('加载牌组失败:', err);
        setError('加载牌组失败');
      } finally {
        setLoading(false);
      }
    }

    loadDecks();
  }, []);

  // 删除牌组
  const handleDeleteDeck = async (name: string) => {
    if (!confirm(`确定要删除牌组 "${name}"？`)) {
      return;
    }

    try {
      await deckApi.deleteDeck(name);
      setDecks(prevDecks => prevDecks.filter(deck => deck.name !== name));
    } catch (err) {
      console.error('删除牌组失败:', err);
      alert('删除牌组失败');
    }
  };

  // 生成新牌组
  const handleGenerateDeck = async () => {
    if (!newDeckName.trim()) {
      alert('请输入牌组名称');
      return;
    }

    try {
      setGenerating(true);
      const result = await deckApi.generateDeck(newDeckName);
      
      // 添加新牌组到列表
      setDecks(prevDecks => [...prevDecks, result.deck]);
      
      // 清空输入框
      setNewDeckName('');
      
      alert(`牌组 "${newDeckName}" 已成功生成！`);
    } catch (err) {
      console.error('生成牌组失败:', err);
      alert('生成牌组失败');
    } finally {
      setGenerating(false);
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    
    return parseFloat((bytes / Math.pow(1024, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 格式化日期
  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  return (
    <AppLayout>
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-6">牌组管理</h1>

        {/* 创建新牌组 */}
        <div className="bg-card rounded-lg p-6 mb-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-4">创建新牌组</h2>
          <div className="flex gap-2">
            <Input
              placeholder="输入牌组名称"
              value={newDeckName}
              onChange={(e) => setNewDeckName(e.target.value)}
            />
            <Button
              onClick={handleGenerateDeck}
              disabled={generating || !newDeckName.trim()}
            >
              {generating ? '生成中...' : '生成牌组'}
            </Button>
          </div>
        </div>

        {/* 牌组列表 */}
        <div className="bg-card rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-4">我的牌组</h2>
          
          {loading ? (
            <p className="text-muted-foreground">加载中...</p>
          ) : error ? (
            <p className="text-destructive">{error}</p>
          ) : decks.length === 0 ? (
            <p className="text-muted-foreground">暂无牌组，请创建一个新牌组</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-2">名称</th>
                    <th className="text-left py-3 px-2">单词数量</th>
                    <th className="text-left py-3 px-2">创建时间</th>
                    <th className="text-left py-3 px-2">大小</th>
                    <th className="text-left py-3 px-2">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {decks.map((deck) => (
                    <tr key={deck.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-2">{deck.name}</td>
                      <td className="py-3 px-2">{deck.wordCount}</td>
                      <td className="py-3 px-2">{formatDate(deck.createdAt)}</td>
                      <td className="py-3 px-2">{formatFileSize(deck.size)}</td>
                      <td className="py-3 px-2">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => window.open(`/api/decks/${deck.name}/download`, '_blank')}
                          >
                            下载
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteDeck(deck.name)}
                          >
                            删除
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
} 