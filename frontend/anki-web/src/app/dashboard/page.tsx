export default function Dashboard() {
  return (
    <div className="container py-10">
      <h1 className="text-3xl font-bold mb-6">控制面板</h1>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border bg-white shadow-sm">
          <div className="flex flex-col space-y-1.5 p-6">
            <h3 className="text-2xl font-semibold leading-none tracking-tight">单词管理</h3>
            <p className="text-sm text-gray-500">管理您的单词列表</p>
          </div>
          <div className="p-6 pt-0">
            <p className="mb-4">添加、删除和查看您的单词列表。</p>
            <a href="/words" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              进入单词管理
            </a>
          </div>
        </div>
        
        <div className="rounded-lg border bg-white shadow-sm">
          <div className="flex flex-col space-y-1.5 p-6">
            <h3 className="text-2xl font-semibold leading-none tracking-tight">音频管理</h3>
            <p className="text-sm text-gray-500">管理单词音频文件</p>
          </div>
          <div className="p-6 pt-0">
            <p className="mb-4">查看和管理单词的音频文件。</p>
            <a href="/audio" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              进入音频管理
            </a>
          </div>
        </div>
        
        <div className="rounded-lg border bg-white shadow-sm">
          <div className="flex flex-col space-y-1.5 p-6">
            <h3 className="text-2xl font-semibold leading-none tracking-tight">AI缓存</h3>
            <p className="text-sm text-gray-500">管理AI生成的内容缓存</p>
          </div>
          <div className="p-6 pt-0">
            <p className="mb-4">查看和管理AI生成的内容缓存。</p>
            <a href="/cache" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              进入缓存管理
            </a>
          </div>
        </div>
        
        <div className="rounded-lg border bg-white shadow-sm">
          <div className="flex flex-col space-y-1.5 p-6">
            <h3 className="text-2xl font-semibold leading-none tracking-tight">牌组管理</h3>
            <p className="text-sm text-gray-500">管理Anki牌组</p>
          </div>
          <div className="p-6 pt-0">
            <p className="mb-4">生成和管理Anki牌组文件。</p>
            <a href="/decks" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              进入牌组管理
            </a>
          </div>
        </div>
        
        <div className="rounded-lg border bg-white shadow-sm">
          <div className="flex flex-col space-y-1.5 p-6">
            <h3 className="text-2xl font-semibold leading-none tracking-tight">词典管理</h3>
            <p className="text-sm text-gray-500">管理词典资源</p>
          </div>
          <div className="p-6 pt-0">
            <p className="mb-4">配置和管理各种词典资源。</p>
            <a href="/dictionaries" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              进入词典管理
            </a>
          </div>
        </div>
        
        <div className="rounded-lg border bg-white shadow-sm">
          <div className="flex flex-col space-y-1.5 p-6">
            <h3 className="text-2xl font-semibold leading-none tracking-tight">系统设置</h3>
            <p className="text-sm text-gray-500">配置系统参数</p>
          </div>
          <div className="p-6 pt-0">
            <p className="mb-4">配置系统参数和偏好设置。</p>
            <a href="/settings" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              进入系统设置
            </a>
          </div>
        </div>
      </div>
    </div>
  )
} 