"use client"

import React, { useState } from 'react'
import AppLayout from "@/components/layouts/app-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Plus, Trash2, Download, Upload, Play, RefreshCw, Filter } from "lucide-react"
import Link from 'next/link'

// 示例数据
const WORDS_DATA = [
  { word: "hello", phonetic: "/həˈləʊ/", hasAudio: true, hasCache: true, lastUpdated: "2023-07-10" },
  { word: "world", phonetic: "/wɜːld/", hasAudio: true, hasCache: true, lastUpdated: "2023-07-10" },
  { word: "example", phonetic: "/ɪɡˈzɑːmpl/", hasAudio: false, hasCache: true, lastUpdated: "2023-07-11" },
  { word: "test", phonetic: "/test/", hasAudio: true, hasCache: false, lastUpdated: "2023-07-12" },
  { word: "sample", phonetic: "/ˈsɑːmpl/", hasAudio: true, hasCache: true, lastUpdated: "2023-07-13" },
  { word: "computer", phonetic: "/kəmˈpjuːtə/", hasAudio: true, hasCache: true, lastUpdated: "2023-07-14" },
  { word: "language", phonetic: "/ˈlæŋɡwɪdʒ/", hasAudio: true, hasCache: true, lastUpdated: "2023-07-15" },
  { word: "programming", phonetic: "/ˈprəʊɡræmɪŋ/", hasAudio: true, hasCache: true, lastUpdated: "2023-07-16" },
  { word: "algorithm", phonetic: "/ˈælɡərɪðəm/", hasAudio: true, hasCache: false, lastUpdated: "2023-07-17" },
  { word: "function", phonetic: "/ˈfʌŋkʃn/", hasAudio: false, hasCache: true, lastUpdated: "2023-07-18" },
]

export default function WordsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedWords, setSelectedWords] = useState<string[]>([])
  
  const filteredWords = WORDS_DATA.filter(word => 
    word.word.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const toggleWordSelection = (word: string) => {
    if (selectedWords.includes(word)) {
      setSelectedWords(selectedWords.filter(w => w !== word))
    } else {
      setSelectedWords([...selectedWords, word])
    }
  }

  const toggleSelectAll = () => {
    if (selectedWords.length === filteredWords.length) {
      setSelectedWords([])
    } else {
      setSelectedWords(filteredWords.map(w => w.word))
    }
  }
  
  return (
    <AppLayout>
      <div className="p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8">
          <h1 className="text-2xl font-bold text-foreground mb-4 md:mb-0">单词管理</h1>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" className="gap-2">
              <Upload className="w-4 h-4" />
              <span>导入单词</span>
            </Button>
            <Button variant="outline" size="sm" className="gap-2">
              <Download className="w-4 h-4" />
              <span>导出单词</span>
            </Button>
            <Button variant="default" size="sm" className="gap-2">
              <Plus className="w-4 h-4" />
              <span>添加单词</span>
            </Button>
          </div>
        </div>
        
        {/* 搜索和过滤 */}
        <div className="bg-card rounded-lg border border-border p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="搜索单词..."
                className="pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="gap-2">
                <Filter className="w-4 h-4" />
                <span>过滤</span>
              </Button>
              <Button variant="outline" size="sm" className="gap-2">
                <RefreshCw className="w-4 h-4" />
                <span>刷新</span>
              </Button>
            </div>
          </div>
        </div>
        
        {/* 单词列表 */}
        <div className="bg-card rounded-lg border border-border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/40">
                  <th className="py-3 px-4">
                    <input 
                      type="checkbox" 
                      className="rounded border-gray-300" 
                      checked={selectedWords.length === filteredWords.length && filteredWords.length > 0}
                      onChange={toggleSelectAll}
                    />
                  </th>
                  <th className="text-left py-3 px-4 font-medium">单词</th>
                  <th className="text-left py-3 px-4 font-medium">音标</th>
                  <th className="text-center py-3 px-4 font-medium">音频</th>
                  <th className="text-center py-3 px-4 font-medium">AI缓存</th>
                  <th className="text-center py-3 px-4 font-medium">更新时间</th>
                  <th className="text-right py-3 px-4 font-medium">操作</th>
                </tr>
              </thead>
              <tbody>
                {filteredWords.map((word, i) => (
                  <tr key={i} className={`border-b border-border ${selectedWords.includes(word.word) ? 'bg-primary/5' : ''}`}>
                    <td className="py-3 px-4 text-center">
                      <input 
                        type="checkbox" 
                        className="rounded border-gray-300"
                        checked={selectedWords.includes(word.word)}
                        onChange={() => toggleWordSelection(word.word)}
                      />
                    </td>
                    <td className="py-3 px-4">
                      <Link href={`/words/${word.word}`} className="font-medium hover:underline">
                        {word.word}
                      </Link>
                    </td>
                    <td className="py-3 px-4 text-muted-foreground">
                      {word.phonetic}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {word.hasAudio ? (
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <Play className="h-4 w-4 text-green-500" />
                        </Button>
                      ) : (
                        <span className="text-orange-500 text-sm">未下载</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {word.hasCache ? (
                        <span className="text-green-500 text-sm">已缓存</span>
                      ) : (
                        <span className="text-orange-500 text-sm">未缓存</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center text-sm text-muted-foreground">
                      {word.lastUpdated}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* 批量操作 */}
          {selectedWords.length > 0 && (
            <div className="p-4 border-t border-border bg-muted/40 flex items-center justify-between">
              <div className="text-sm">
                已选择 <span className="font-medium">{selectedWords.length}</span> 个单词
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="gap-2">
                  <Download className="w-4 h-4" />
                  <span>生成卡片</span>
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
              显示 1-{filteredWords.length} 共 {filteredWords.length} 个单词
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