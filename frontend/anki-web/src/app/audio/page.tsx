"use client"

import React, { useState } from 'react'
import AppLayout from "@/components/layouts/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Trash2, RefreshCw, Play, Pause, PlayCircle, CheckCircle2, XCircle } from "lucide-react"
import Link from 'next/link'

// 模拟数据
const AUDIO_DATA = [
  { word: "hello", size: "24 KB", duration: "0.8s", lastUpdated: "2023-07-10", status: "ready" },
  { word: "world", size: "32 KB", duration: "1.0s", lastUpdated: "2023-07-10", status: "ready" },
  { word: "computer", size: "45 KB", duration: "1.2s", lastUpdated: "2023-07-14", status: "ready" },
  { word: "language", size: "38 KB", duration: "1.1s", lastUpdated: "2023-07-15", status: "ready" },
  { word: "programming", size: "52 KB", duration: "1.5s", lastUpdated: "2023-07-16", status: "ready" },
  { word: "algorithm", size: "48 KB", duration: "1.3s", lastUpdated: "2023-07-17", status: "ready" },
  { word: "orphaned1", size: "28 KB", duration: "0.9s", lastUpdated: "2023-07-20", status: "orphaned" },
  { word: "orphaned2", size: "30 KB", duration: "1.0s", lastUpdated: "2023-07-21", status: "orphaned" },
  { word: "orphaned3", size: "35 KB", duration: "1.1s", lastUpdated: "2023-07-22", status: "orphaned" },
  { word: "downloading", size: "—", duration: "—", lastUpdated: "2023-07-25", status: "downloading" },
]

export default function AudioPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedAudio, setSelectedAudio] = useState<string[]>([])
  const [playing, setPlaying] = useState<string | null>(null)
  
  const filteredAudio = AUDIO_DATA.filter(audio => 
    audio.word.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const toggleAudioSelection = (word: string) => {
    if (selectedAudio.includes(word)) {
      setSelectedAudio(selectedAudio.filter(w => w !== word))
    } else {
      setSelectedAudio([...selectedAudio, word])
    }
  }

  const toggleSelectAll = () => {
    if (selectedAudio.length === filteredAudio.length) {
      setSelectedAudio([])
    } else {
      setSelectedAudio(filteredAudio.map(a => a.word))
    }
  }

  const playAudio = (word: string) => {
    // 在实际应用中，这里会播放音频
    setPlaying(word)
    setTimeout(() => setPlaying(null), 1000) // 模拟播放结束
  }
  
  return (
    <AppLayout>
      <div className="p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-foreground mb-4 md:mb-0">音频管理</h1>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <RefreshCw className="w-4 h-4" />
              <span>重新下载</span>
            </Button>
            <Button variant="outline" size="sm" className="gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>清理孤立音频</span>
            </Button>
            <Button variant="destructive" size="sm" className="gap-2">
              <Trash2 className="w-4 h-4" />
              <span>清空音频</span>
            </Button>
          </div>
        </div>
        
        {/* 搜索 */}
        <div className="bg-card rounded-lg border border-border p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="搜索音频..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Button variant="outline" size="sm" className="gap-2">
              <RefreshCw className="w-4 h-4" />
              <span>刷新</span>
            </Button>
          </div>
        </div>
        
        {/* 统计信息 */}
        <div className="bg-card rounded-lg border border-border p-4 mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">总音频数</span>
            <span className="text-2xl font-semibold">{AUDIO_DATA.length}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">总大小</span>
            <span className="text-2xl font-semibold">332 KB</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">孤立音频</span>
            <span className="text-2xl font-semibold text-orange-500">3</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">下载中</span>
            <span className="text-2xl font-semibold text-blue-500">1</span>
          </div>
        </div>
        
        {/* 音频列表 */}
        <div className="bg-card rounded-lg border border-border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/40">
                  <th className="py-3 px-4">
                    <input 
                      type="checkbox" 
                      className="rounded border-gray-300" 
                      checked={selectedAudio.length === filteredAudio.length && filteredAudio.length > 0}
                      onChange={toggleSelectAll}
                    />
                  </th>
                  <th className="text-left py-3 px-4 font-medium">单词</th>
                  <th className="text-center py-3 px-4 font-medium">状态</th>
                  <th className="text-center py-3 px-4 font-medium">大小</th>
                  <th className="text-center py-3 px-4 font-medium">时长</th>
                  <th className="text-center py-3 px-4 font-medium">更新时间</th>
                  <th className="text-right py-3 px-4 font-medium">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredAudio.map((audio, i) => (
                  <tr key={i} className={`border-b border-border ${selectedAudio.includes(audio.word) ? 'bg-primary/5' : ''}`}>
                    <td className="py-3 px-4 text-center">
                      <input 
                        type="checkbox" 
                        className="rounded border-gray-300"
                        checked={selectedAudio.includes(audio.word)}
                        onChange={() => toggleAudioSelection(audio.word)}
                      />
                    </td>
                    <td className="py-3 px-4">
                      <Link href={`/words/${audio.word}`} className="font-medium hover:underline">
                        {audio.word}
                      </Link>
                    </td>
                    <td className="py-3 px-4 text-center">
                      {audio.status === 'ready' && <span className="text-green-500 text-sm">可用</span>}
                      {audio.status === 'orphaned' && <span className="text-orange-500 text-sm">孤立</span>}
                      {audio.status === 'downloading' && <span className="text-blue-500 text-sm">下载中</span>}
                    </td>
                    <td className="py-3 px-4 text-center text-sm text-muted-foreground">
                      {audio.size}
                    </td>
                    <td className="py-3 px-4 text-center text-sm text-muted-foreground">
                      {audio.duration}
                    </td>
                    <td className="py-3 px-4 text-center text-sm text-muted-foreground">
                      {audio.lastUpdated}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex justify-end gap-2">
                        {audio.status === 'ready' && (
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            className="h-8 w-8 p-0"
                            onClick={() => playAudio(audio.word)}
                          >
                            {playing === audio.word ? 
                              <Pause className="h-4 w-4 text-blue-500" /> : 
                              <Play className="h-4 w-4 text-green-500" />
                            }
                          </Button>
                        )}
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* 批量操作 */}
          {selectedAudio.length > 0 && (
            <div className="p-4 border-t border-border bg-muted/40 flex items-center justify-between">
              <div className="text-sm">
                已选择 <span className="font-medium">{selectedAudio.length}</span> 个音频
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="gap-2">
                  <RefreshCw className="w-4 h-4" />
                  <span>重新下载</span>
                </Button>
                <Button variant="destructive" size="sm" className="gap-2">
                  <Trash2 className="w-4 h-4" />
                  <span>批量删除</span>
                </Button>
              </div>
            </div>
          )}
          
          {/* 分页 */}
          <div className="p-4 border-t border-border flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              显示 1-{filteredAudio.length} 共 {filteredAudio.length} 个音频
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled>
                上一页
              </Button>
              <Button variant="outline" size="sm" disabled>
                下一页
              </Button>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  )
} 