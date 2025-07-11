"use client"

import React, { useState } from 'react'
import AppLayout from "@/components/layouts/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Trash2, RefreshCw, Database, CheckCircle2, Eye } from "lucide-react"
import Link from 'next/link'

// 模拟数据
const CACHE_DATA = [
  { word: "hello", size: "2.3 KB", lastUpdated: "2023-07-10", status: "valid" },
  { word: "world", size: "1.8 KB", lastUpdated: "2023-07-10", status: "valid" },
  { word: "example", size: "3.1 KB", lastUpdated: "2023-07-11", status: "valid" },
  { word: "test", size: "1.5 KB", lastUpdated: "2023-07-12", status: "outdated" },
  { word: "sample", size: "2.7 KB", lastUpdated: "2023-07-13", status: "valid" },
  { word: "computer", size: "4.2 KB", lastUpdated: "2023-07-14", status: "valid" },
  { word: "language", size: "3.5 KB", lastUpdated: "2023-07-15", status: "valid" },
  { word: "orphaned1", size: "2.1 KB", lastUpdated: "2023-07-20", status: "orphaned" },
  { word: "orphaned2", size: "1.9 KB", lastUpdated: "2023-07-21", status: "orphaned" },
  { word: "orphaned3", size: "2.4 KB", lastUpdated: "2023-07-22", status: "orphaned" },
]

export default function CachePage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCache, setSelectedCache] = useState<string[]>([])
  
  const filteredCache = CACHE_DATA.filter(cache => 
    cache.word.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const toggleCacheSelection = (word: string) => {
    if (selectedCache.includes(word)) {
      setSelectedCache(selectedCache.filter(w => w !== word))
    } else {
      setSelectedCache([...selectedCache, word])
    }
  }

  const toggleSelectAll = () => {
    if (selectedCache.length === filteredCache.length) {
      setSelectedCache([])
    } else {
      setSelectedCache(filteredCache.map(c => c.word))
    }
  }
  
  return (
    <AppLayout>
      <div className="p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-foreground mb-4 md:mb-0">AI缓存管理</h1>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <RefreshCw className="w-4 h-4" />
              <span>重新生成</span>
            </Button>
            <Button variant="outline" size="sm" className="gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>清理孤立缓存</span>
            </Button>
            <Button variant="destructive" size="sm" className="gap-2">
              <Trash2 className="w-4 h-4" />
              <span>清空缓存</span>
            </Button>
          </div>
        </div>
        
        {/* 搜索 */}
        <div className="bg-card rounded-lg border border-border p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="搜索缓存..."
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
            <span className="text-sm text-muted-foreground">总缓存数</span>
            <span className="text-2xl font-semibold">{CACHE_DATA.length}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">总大小</span>
            <span className="text-2xl font-semibold">25.5 KB</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">孤立缓存</span>
            <span className="text-2xl font-semibold text-orange-500">3</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">过期缓存</span>
            <span className="text-2xl font-semibold text-blue-500">1</span>
          </div>
        </div>
        
        {/* 缓存列表 */}
        <div className="bg-card rounded-lg border border-border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/40">
                  <th className="py-3 px-4">
                    <input 
                      type="checkbox" 
                      className="rounded border-gray-300" 
                      checked={selectedCache.length === filteredCache.length && filteredCache.length > 0}
                      onChange={toggleSelectAll}
                    />
                  </th>
                  <th className="text-left py-3 px-4 font-medium">单词</th>
                  <th className="text-center py-3 px-4 font-medium">状态</th>
                  <th className="text-center py-3 px-4 font-medium">大小</th>
                  <th className="text-center py-3 px-4 font-medium">更新时间</th>
                  <th className="text-right py-3 px-4 font-medium">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredCache.map((cache, i) => (
                  <tr key={i} className={`border-b border-border ${selectedCache.includes(cache.word) ? 'bg-primary/5' : ''}`}>
                    <td className="py-3 px-4 text-center">
                      <input 
                        type="checkbox" 
                        className="rounded border-gray-300"
                        checked={selectedCache.includes(cache.word)}
                        onChange={() => toggleCacheSelection(cache.word)}
                      />
                    </td>
                    <td className="py-3 px-4">
                      <Link href={`/words/${cache.word}`} className="font-medium hover:underline">
                        {cache.word}
                      </Link>
                    </td>
                    <td className="py-3 px-4 text-center">
                      {cache.status === 'valid' && <span className="text-green-500 text-sm">有效</span>}
                      {cache.status === 'outdated' && <span className="text-blue-500 text-sm">过期</span>}
                      {cache.status === 'orphaned' && <span className="text-orange-500 text-sm">孤立</span>}
                    </td>
                    <td className="py-3 px-4 text-center text-sm text-muted-foreground">
                      {cache.size}
                    </td>
                    <td className="py-3 px-4 text-center text-sm text-muted-foreground">
                      {cache.lastUpdated}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex justify-end gap-2">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="h-8 w-8 p-0"
                        >
                          <Eye className="h-4 w-4 text-blue-500" />
                        </Button>
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
          {selectedCache.length > 0 && (
            <div className="p-4 border-t border-border bg-muted/40 flex items-center justify-between">
              <div className="text-sm">
                已选择 <span className="font-medium">{selectedCache.length}</span> 个缓存
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="gap-2">
                  <RefreshCw className="w-4 h-4" />
                  <span>重新生成</span>
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
              显示 1-{filteredCache.length} 共 {filteredCache.length} 个缓存
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