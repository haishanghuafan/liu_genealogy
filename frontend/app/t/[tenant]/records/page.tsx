"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { Search, Plus, BookOpen, FileText, CheckCircle, AlertCircle } from "lucide-react"

interface Record {
  id: string
  title: string
  content: string
  source_type: string
  source_name: string | null
  page_number: string | null
  reliability: string
  is_verified: boolean
  created_at: string
}

export default function RecordsPage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [records, setRecords] = useState<Record[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [sourceFilter, setSourceFilter] = useState("")
  
  useEffect(() => {
    fetchRecords()
  }, [tenantSlug])
  
  const fetchRecords = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/records`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) setRecords(data.data)
    } catch (err) {
      console.error("Failed to fetch records:", err)
    } finally {
      setLoading(false)
    }
  }
  
  const sourceTypeNames: Record<string, string> = {
    paper: "纸质资料",
    digital: "数字资料",
    oral: "口述记录",
  }
  
  const reliabilityNames: Record<string, string> = {
    high: "高",
    medium: "中",
    low: "低",
  }
  
  const filteredRecords = records.filter(r => 
    (search === "" || r.title.includes(search) || r.content.includes(search)) &&
    (sourceFilter === "" || r.source_type === sourceFilter)
  )
  
  return (
    <main className="min-h-screen bg-paper">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href={`/t/${tenantSlug}`} className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <Link href={`/t/${tenantSlug}`} className="text-ink-muted hover:text-ink flex items-center gap-1">
            <span>←</span> 返回
          </Link>
        </div>
      </nav>
      
      <div className="pt-24 px-4 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-serif font-semibold mb-2">📚 原始资料</h1>
            <p className="text-ink-muted">记录族谱的原始来源，确保数据可追溯</p>
          </div>
          <Link
            href={`/t/${tenantSlug}/records/create`}
            className="bg-vermillion text-white px-6 py-3 rounded-lg hover:bg-vermillion-dark transition-colors flex items-center gap-2"
          >
            <Plus className="h-4 w-4" /> 添加记录
          </Link>
        </div>
        
        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-ink-muted" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索标题或内容..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
            />
          </div>
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
          >
            <option value="">全部来源</option>
            <option value="paper">纸质资料</option>
            <option value="digital">数字资料</option>
            <option value="oral">口述记录</option>
          </select>
        </div>
        
        {/* Records List */}
        {loading ? (
          <div className="text-center py-20 text-ink-muted">⏳ 加载中...</div>
        ) : filteredRecords.length === 0 ? (
          <div className="bg-white rounded-xl border border-ink/5 p-12 text-center">
            <BookOpen className="h-12 w-12 mx-auto mb-4 text-ink-muted opacity-50" />
            <p className="text-ink-muted mb-4">暂无资料记录</p>
            <Link
              href={`/t/${tenantSlug}/records/create`}
              className="text-vermillion hover:underline"
            >
              添加第一条资料
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredRecords.map((record) => (
              <Link
                key={record.id}
                href={`/t/${tenantSlug}/records/${record.id}`}
                className="block bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <FileText className="h-5 w-5 text-vermillion" />
                      <h3 className="font-semibold text-lg">{record.title}</h3>
                      {record.is_verified && (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      )}
                    </div>
                    <p className="text-ink-muted text-sm mb-3 line-clamp-2">
                      {record.content.substring(0, 200)}...
                    </p>
                    <div className="flex items-center gap-4 text-sm text-ink-muted">
                      <span className="flex items-center gap-1">
                        📁 {sourceTypeNames[record.source_type] || record.source_type}
                      </span>
                      {record.source_name && (
                        <span className="flex items-center gap-1">
                          📖 {record.source_name}
                        </span>
                      )}
                      {record.page_number && (
                        <span>P{record.page_number}</span>
                      )}
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        record.reliability === 'high' ? 'bg-green-100 text-green-700' :
                        record.reliability === 'low' ? 'bg-red-100 text-red-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        可靠性: {reliabilityNames[record.reliability] || record.reliability}
                      </span>
                    </div>
                  </div>
                  <div className="text-right text-xs text-ink-muted">
                    {new Date(record.created_at).toLocaleDateString("zh-CN")}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}