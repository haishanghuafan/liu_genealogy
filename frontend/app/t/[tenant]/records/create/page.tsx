"use client"

import { useState } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, Save, X } from "lucide-react"
import { UserMenu } from "@/components/layout/UserMenu"

export default function CreateRecordPage() {
  const params = useParams()
  const router = useRouter()
  const tenantSlug = params.tenant as string
  
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    source_type: "paper",
    source_name: "",
    source_url: "",
    page_number: "",
    volume_number: "",
    section: "",
    reliability: "medium",
    notes: "",
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    
    if (!formData.title.trim()) {
      setError("请输入标题")
      return
    }
    if (!formData.content.trim()) {
      setError("请输入内容")
      return
    }
    
    setSubmitting(true)
    try {
      const token = localStorage.getItem("access_token")
      const res = await fetch(`/api/v1/t/${tenantSlug}/records`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: formData.title,
          content: formData.content,
          source_type: formData.source_type,
          source_name: formData.source_name || null,
          source_url: formData.source_url || null,
          page_number: formData.page_number || null,
          volume_number: formData.volume_number || null,
          section: formData.section || null,
          reliability: formData.reliability,
          notes: formData.notes || null,
        }),
      })
      
      const data = await res.json()
      if (data.success) {
        router.push(`/t/${tenantSlug}/records`)
      } else {
        setError(data.message || "创建失败")
      }
    } catch (err) {
      setError("网络错误，请稍后重试")
      console.error("Failed to create record:", err)
    } finally {
      setSubmitting(false)
    }
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
          <div className="flex items-center gap-3">
            <Link href={`/t/${tenantSlug}/records`} className="text-ink-muted hover:text-ink flex items-center gap-1">
              <ArrowLeft className="h-4 w-4" /> 返回列表
            </Link>
            <div className="w-px h-6 bg-ink/10" />
            <UserMenu />
          </div>
        </div>
      </nav>
      
      <div className="pt-24 pb-12 px-4 max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-serif font-semibold mb-2">📝 添加资料记录</h1>
          <p className="text-ink-muted">记录族谱的原始来源信息</p>
        </div>
        
        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-xl border border-ink/5 p-8 space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}
          
          {/* Title */}
          <div>
            <label className="block text-sm font-medium mb-2">
              标题 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
              placeholder="请输入资料标题"
              maxLength={200}
              required
            />
          </div>
          
          {/* Content */}
          <div>
            <label className="block text-sm font-medium mb-2">
              内容 <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none min-h-[200px] resize-y"
              placeholder="请输入资料内容"
              required
            />
          </div>
          
          {/* Source Type & Reliability */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                来源类型
              </label>
              <select
                value={formData.source_type}
                onChange={(e) => setFormData({ ...formData, source_type: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
              >
                <option value="paper">纸质资料</option>
                <option value="digital">数字资料</option>
                <option value="oral">口述记录</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                可靠性
              </label>
              <select
                value={formData.reliability}
                onChange={(e) => setFormData({ ...formData, reliability: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
              >
                <option value="high">高</option>
                <option value="medium">中</option>
                <option value="low">低</option>
              </select>
            </div>
          </div>
          
          {/* Source Name & Page Number */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                来源名称
              </label>
              <input
                type="text"
                value={formData.source_name}
                onChange={(e) => setFormData({ ...formData, source_name: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
                placeholder="例如：刘氏族谱第一卷"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                页码
              </label>
              <input
                type="text"
                value={formData.page_number}
                onChange={(e) => setFormData({ ...formData, page_number: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
                placeholder="例如：12-15"
              />
            </div>
          </div>
          
          {/* Volume Number & Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                卷号
              </label>
              <input
                type="text"
                value={formData.volume_number}
                onChange={(e) => setFormData({ ...formData, volume_number: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
                placeholder="例如：卷三"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">
                章节
              </label>
              <input
                type="text"
                value={formData.section}
                onChange={(e) => setFormData({ ...formData, section: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
                placeholder="例如：世系表"
              />
            </div>
          </div>
          
          {/* Source URL */}
          <div>
            <label className="block text-sm font-medium mb-2">
              来源链接
            </label>
            <input
              type="url"
              value={formData.source_url}
              onChange={(e) => setFormData({ ...formData, source_url: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
              placeholder="https://example.com/..."
            />
          </div>
          
          {/* Notes */}
          <div>
            <label className="block text-sm font-medium mb-2">
              备注
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none min-h-[100px] resize-y"
              placeholder="其他补充说明..."
            />
          </div>
          
          {/* Actions */}
          <div className="flex gap-4 pt-4 border-t border-ink/5">
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 bg-vermillion text-white px-6 py-3 rounded-lg hover:bg-vermillion-dark transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="h-4 w-4" />
              {submitting ? "提交中..." : "保存记录"}
            </button>
            <Link
              href={`/t/${tenantSlug}/records`}
              className="px-6 py-3 rounded-lg border border-ink/10 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
            >
              <X className="h-4 w-4" />
              取消
            </Link>
          </div>
        </form>
      </div>
    </main>
  )
}
