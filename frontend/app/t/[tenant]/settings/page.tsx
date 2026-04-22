"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { UserMenu } from "@/components/layout/UserMenu"

interface Settings {
  id: string
  name: string
  slug: string
  description: string | null
  logo: string | null
  plan: string
  max_persons: number
  max_members: number
  is_public: boolean
  allow_public_search: boolean
  require_login_for_details: boolean
  tree_layout: string
  enable_family_tree: boolean
  enable_photo_gallery: boolean
  enable_timeline: boolean
}

export default function SettingsPage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [settings, setSettings] = useState<Settings | null>(null)
  const [activeTab, setActiveTab] = useState<"general" | "privacy" | "display" | "features">("general")
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    is_public: true,
    allow_public_search: true,
    require_login_for_details: false,
    tree_layout: "vertical",
    enable_family_tree: true,
    enable_photo_gallery: true,
    enable_timeline: true,
  })
  
  useEffect(() => {
    fetchSettings()
  }, [tenantSlug])
  
  const fetchSettings = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/settings`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) {
        setSettings(data.data)
        setFormData({
          name: data.data.name || "",
          description: data.data.description || "",
          is_public: data.data.is_public ?? true,
          allow_public_search: data.data.allow_public_search ?? true,
          require_login_for_details: data.data.require_login_for_details ?? false,
          tree_layout: data.data.tree_layout || "vertical",
          enable_family_tree: data.data.enable_family_tree ?? true,
          enable_photo_gallery: data.data.enable_photo_gallery ?? true,
          enable_timeline: data.data.enable_timeline ?? true,
        })
      }
    } catch (err) {
      setError("加载设置失败")
    } finally {
      setLoading(false)
    }
  }
  
  const handleSave = async () => {
    setSaving(true)
    setError("")
    setSuccess("")
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/settings`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess("设置已保存")
        fetchSettings()
      } else {
        setError(data.message || "保存失败")
      }
    } catch (err) {
      setError("网络错误")
    } finally {
      setSaving(false)
    }
  }
  
  if (loading) {
    return (
      <main className="min-h-screen bg-paper pt-20 px-4">
        <div className="max-w-4xl mx-auto text-center py-20">
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
          <div className="flex items-center gap-3">
            <Link href={`/t/${tenantSlug}`} className="text-ink-muted hover:text-ink flex items-center gap-1">
              <span>←</span> 返回
            </Link>
            <div className="w-px h-6 bg-ink/10" />
            <UserMenu />
          </div>
        </div>
      </nav>
      
      <div className="pt-24 px-4 max-w-4xl mx-auto">
        <h1 className="text-3xl font-serif font-semibold mb-8">⚙️ 家族设置</h1>
        
        {/* Plan Info */}
        {settings && (
          <div className="bg-white rounded-xl p-6 border border-ink/5 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="font-semibold mb-1">{settings.name}</h2>
                <p className="text-sm text-ink-muted">
                  套餐: {settings.plan === "free" ? "免费版" : 
                        settings.plan === "basic" ? "基础版" :
                        settings.plan === "professional" ? "专业版" : "企业版"}
                </p>
              </div>
              <Link
                href={`/t/${tenantSlug}/subscription`}
                className="text-vermillion hover:underline text-sm"
              >
                💎 管理订阅
              </Link>
            </div>
          </div>
        )}
        
        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-ink/10">
          {[
            { key: "general", label: "通用", icon: "📋" },
            { key: "privacy", label: "隐私", icon: "🔒" },
            { key: "display", label: "显示", icon: "🎨" },
            { key: "features", label: "功能", icon: "✨" },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as typeof activeTab)}
              className={`pb-3 px-2 font-medium border-b-2 transition-colors ${
                activeTab === tab.key ? "border-vermillion text-vermillion" : "border-transparent text-ink-muted"
              }`}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </div>
        
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
        
        {/* Tab Content */}
        <div className="bg-white rounded-xl border border-ink/5 p-6">
          {activeTab === "general" && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">家族名称</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
                  placeholder="请输入家族名称"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">家族简介</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
                  rows={4}
                  placeholder="介绍您的家族历史、来源等"
                />
              </div>
              
              <div className="flex items-center justify-between py-3 border-t border-ink/5">
                <div>
                  <div className="font-medium">公开家族</div>
                  <div className="text-sm text-ink-muted">允许游客查看家族信息</div>
                </div>
                <button
                  onClick={() => setFormData({ ...formData, is_public: !formData.is_public })}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    formData.is_public ? "bg-vermillion" : "bg-gray-300"
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    formData.is_public ? "translate-x-6" : "translate-x-1"
                  }`} />
                </button>
              </div>
            </div>
          )}
          
          {activeTab === "privacy" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-ink/5">
                <div>
                  <div className="font-medium">公开搜索</div>
                  <div className="text-sm text-ink-muted">允许搜索引擎收录</div>
                </div>
                <button
                  onClick={() => setFormData({ ...formData, allow_public_search: !formData.allow_public_search })}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    formData.allow_public_search ? "bg-vermillion" : "bg-gray-300"
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    formData.allow_public_search ? "translate-x-6" : "translate-x-1"
                  }`} />
                </button>
              </div>
              
              <div className="flex items-center justify-between py-3 border-b border-ink/5">
                <div>
                  <div className="font-medium">登录查看详情</div>
                  <div className="text-sm text-ink-muted">访客需登录才能查看人物详情</div>
                </div>
                <button
                  onClick={() => setFormData({ ...formData, require_login_for_details: !formData.require_login_for_details })}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    formData.require_login_for_details ? "bg-vermillion" : "bg-gray-300"
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    formData.require_login_for_details ? "translate-x-6" : "translate-x-1"
                  }`} />
                </button>
              </div>
            </div>
          )}
          
          {activeTab === "display" && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">族谱树布局</label>
                <select
                  value={formData.tree_layout}
                  onChange={(e) => setFormData({ ...formData, tree_layout: e.target.value })}
                  className="w-full px-4 py-3 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
                >
                  <option value="vertical">垂直布局（从上到下）</option>
                  <option value="horizontal">水平布局（从左到右）</option>
                  <option value="radial">放射布局（从中心向外）</option>
                </select>
              </div>
            </div>
          )}
          
          {activeTab === "features" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-ink/5">
                <div>
                  <div className="font-medium">族谱树</div>
                  <div className="text-sm text-ink-muted">显示族谱树可视化功能</div>
                </div>
                <button
                  onClick={() => setFormData({ ...formData, enable_family_tree: !formData.enable_family_tree })}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    formData.enable_family_tree ? "bg-vermillion" : "bg-gray-300"
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    formData.enable_family_tree ? "translate-x-6" : "translate-x-1"
                  }`} />
                </button>
              </div>
              
              <div className="flex items-center justify-between py-3 border-b border-ink/5">
                <div>
                  <div className="font-medium">照片画廊</div>
                  <div className="text-sm text-ink-muted">显示人物照片功能</div>
                </div>
                <button
                  onClick={() => setFormData({ ...formData, enable_photo_gallery: !formData.enable_photo_gallery })}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    formData.enable_photo_gallery ? "bg-vermillion" : "bg-gray-300"
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    formData.enable_photo_gallery ? "translate-x-6" : "translate-x-1"
                  }`} />
                </button>
              </div>
              
              <div className="flex items-center justify-between py-3">
                <div>
                  <div className="font-medium">时间线</div>
                  <div className="text-sm text-ink-muted">显示家族历史时间线</div>
                </div>
                <button
                  onClick={() => setFormData({ ...formData, enable_timeline: !formData.enable_timeline })}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    formData.enable_timeline ? "bg-vermillion" : "bg-gray-300"
                  }`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full transition-transform ${
                    formData.enable_timeline ? "translate-x-6" : "translate-x-1"
                  }`} />
                </button>
              </div>
            </div>
          )}
          
          {/* Save Button */}
          <div className="mt-8 pt-6 border-t border-ink/5">
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-vermillion text-white px-8 py-3 rounded-lg hover:bg-vermillion-dark transition-colors disabled:opacity-50"
            >
              {saving ? "保存中..." : "💾 保存设置"}
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}