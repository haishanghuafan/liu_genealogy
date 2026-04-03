"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"

interface FileItem {
  id: string
  filename: string
  url: string
  size: number
  mime_type: string
  created_at: string
}

interface StorageUsage {
  used_mb: number
  max_mb: number
  used_percent: number
  file_count: number
}

export default function FilesPage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [files, setFiles] = useState<FileItem[]>([])
  const [usage, setUsage] = useState<StorageUsage | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  
  useEffect(() => {
    fetchData()
  }, [tenantSlug])
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      
      const [filesRes, usageRes] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/files`, {
          headers: { "Authorization": `Bearer ${token}` }
        }),
        fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/files/usage`, {
          headers: { "Authorization": `Bearer ${token}` }
        })
      ])
      
      const filesData = await filesRes.json()
      const usageData = await usageRes.json()
      
      if (filesData.success) setFiles(filesData.data)
      if (usageData.success) setUsage(usageData.data)
    } catch (err) {
      setError("加载数据失败")
    } finally {
      setLoading(false)
    }
  }
  
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    setUploading(true)
    setError("")
    setSuccess("")
    
    const formData = new FormData()
    formData.append("file", file)
    formData.append("category", "general")
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/files/upload`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess(`文件 ${file.name} 上传成功`)
        fetchData()
      } else {
        setError(data.message || "上传失败")
      }
    } catch (err) {
      setError("上传失败")
    } finally {
      setUploading(false)
    }
  }
  
  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }
  
  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith("image/")) return "🖼️"
    if (mimeType.startsWith("video/")) return "🎬"
    if (mimeType.includes("pdf")) return "📄"
    if (mimeType.includes("word") || mimeType.includes("document")) return "📝"
    if (mimeType.includes("excel") || mimeType.includes("spreadsheet")) return "📊"
    return "📁"
  }
  
  if (loading) {
    return (
      <main className="min-h-screen bg-paper pt-20 px-4">
        <div className="max-w-6xl mx-auto text-center py-20">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-ink-muted">加载中...</p>
        </div>
      </main>
    )
  }
  
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
            <h1 className="text-3xl font-serif font-semibold mb-2">📁 文件管理</h1>
            <p className="text-ink-muted">上传和管理家族照片、文档</p>
          </div>
          <label className="bg-vermillion text-white px-6 py-3 rounded-lg hover:bg-vermillion-dark transition-colors cursor-pointer flex items-center gap-2">
            <span>📤</span> 上传文件
            <input
              type="file"
              className="hidden"
              onChange={handleUpload}
              disabled={uploading}
              accept="image/*,video/*,.pdf,.doc,.docx,.xls,.xlsx"
            />
          </label>
        </div>
        
        {/* Storage Usage */}
        {usage && (
          <div className="bg-white rounded-xl p-6 border border-ink/5 mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-semibold">存储空间</h3>
                <p className="text-sm text-ink-muted">
                  已使用 {usage.used_mb}MB / {usage.max_mb === 999999 ? "无限" : `${usage.max_mb}MB`}
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-serif font-semibold">{usage.file_count}</div>
                <div className="text-sm text-ink-muted">个文件</div>
              </div>
            </div>
            <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-vermillion rounded-full transition-all"
                style={{ width: `${Math.min(usage.used_percent, 100)}%` }}
              />
            </div>
            {usage.used_percent > 80 && (
              <div className="mt-3 text-sm text-vermillion">
                ⚠️ 存储空间即将用完，请升级套餐或清理文件
              </div>
            )}
          </div>
        )}
        
        {/* Messages */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-vermillion/5 border border-vermillion/20 text-vermillion">
            ⚠️ {error}
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 rounded-lg bg-green-50 border border-green-200 text-green-700">
            ✅ {success}
          </div>
        )}
        
        {uploading && (
          <div className="mb-6 p-4 rounded-lg bg-blue-50 border border-blue-200 text-blue-700">
            ⏳ 上传中...
          </div>
        )}
        
        {/* Files Grid */}
        {files.length > 0 ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {files.map((file) => (
              <div
                key={file.id}
                className="bg-white rounded-xl border border-ink/5 overflow-hidden hover:shadow-lg transition-all"
              >
                <div className="aspect-video bg-paper-warm flex items-center justify-center text-4xl">
                  {getFileIcon(file.mime_type)}
                </div>
                <div className="p-4">
                  <div className="font-medium truncate mb-1" title={file.filename}>
                    {file.filename}
                  </div>
                  <div className="flex items-center justify-between text-sm text-ink-muted">
                    <span>{formatSize(file.size)}</span>
                    <a
                      href={`http://localhost:8000${file.url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-vermillion hover:underline"
                    >
                      下载
                    </a>
                  </div>
                  <div className="mt-2 text-xs text-ink-muted">
                    {new Date(file.created_at).toLocaleDateString("zh-CN")}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl border border-ink/5 p-12 text-center">
            <div className="text-5xl mb-4">📁</div>
            <h3 className="text-lg font-semibold mb-2">暂无文件</h3>
            <p className="text-ink-muted mb-6">上传照片、文档来记录家族故事</p>
            <label className="bg-vermillion text-white px-6 py-3 rounded-lg hover:bg-vermillion-dark transition-colors cursor-pointer inline-flex items-center gap-2">
              <span>📤</span> 上传第一个文件
              <input
                type="file"
                className="hidden"
                onChange={handleUpload}
                disabled={uploading}
              />
            </label>
          </div>
        )}
      </div>
    </main>
  )
}