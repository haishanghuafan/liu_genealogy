"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"

interface TenantInfo {
  id: string
  name: string
  slug: string
  surname: string
  plan: string
}

export default function TenantHomePage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [tenant, setTenant] = useState<TenantInfo | null>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchTenant()
  }, [tenantSlug])
  
  const fetchTenant = async () => {
    try {
      const res = await fetch(`http://localhost:8012/api/v1/tenants/${tenantSlug}`)
      const data = await res.json()
      if (data.success !== false) {
        setTenant(data)
      }
    } catch (err) {
      console.error("Failed to load tenant:", err)
    } finally {
      setLoading(false)
    }
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
  
  if (!tenant) {
    return (
      <main className="min-h-screen bg-paper pt-20 px-4">
        <div className="max-w-6xl mx-auto text-center py-20">
          <div className="text-4xl mb-4">😕</div>
          <p className="text-ink-muted">家族不存在</p>
          <Link href="/" className="text-vermillion hover:underline mt-4 inline-block">
            返回首页
          </Link>
        </div>
      </main>
    )
  }
  
  const planNames: Record<string, string> = {
    free: "免费版",
    basic: "基础版",
    professional: "专业版",
    enterprise: "企业版",
  }
  
  return (
    <main className="min-h-screen bg-paper">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link 
              href={`/t/${tenantSlug}/settings`} 
              className="text-ink-muted hover:text-ink px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1"
            >
              <span>⚙️</span> 设置
            </Link>
            <Link 
              href={`/t/${tenantSlug}/subscription`} 
              className="text-ink-muted hover:text-ink px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1"
            >
              <span>💎</span> 订阅
            </Link>
            <Link 
              href={`/t/${tenantSlug}/members`} 
              className="text-ink-muted hover:text-ink px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1"
            >
              <span>👥</span> 成员
            </Link>
          </div>
        </div>
      </nav>
      
      {/* Hero */}
      <div className="pt-32 pb-20 px-4 text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-vermillion/10 text-vermillion text-3xl font-serif font-bold mb-8 border-2 border-vermillion/20">
          {tenant.surname.charAt(0)}
        </div>
        <h1 className="text-4xl md:text-5xl font-serif font-bold text-ink mb-4">
          {tenant.name}
        </h1>
        <p className="text-lg text-ink-muted max-w-2xl mx-auto">
          欢迎来到{tenant.name}的数字族谱空间
        </p>
        
        {/* Plan Badge */}
        <div className="mt-6">
          <span className="inline-flex items-center gap-1 px-4 py-2 rounded-full bg-vermillion/10 text-vermillion text-sm">
            <span>💎</span> {planNames[tenant.plan] || tenant.plan}
          </span>
        </div>
      </div>
      
      {/* Quick Actions */}
      <div className="max-w-5xl mx-auto px-4 pb-20">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Link
            href={`/t/${tenantSlug}/family-tree`}
            className="bg-white rounded-xl p-8 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
          >
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🌳</div>
            <h3 className="text-lg font-semibold mb-2">族谱树</h3>
            <p className="text-sm text-ink-muted">浏览家族世代脉络</p>
          </Link>
          
          <Link
            href={`/t/${tenantSlug}/persons`}
            className="bg-white rounded-xl p-8 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
          >
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">👤</div>
            <h3 className="text-lg font-semibold mb-2">人物管理</h3>
            <p className="text-sm text-ink-muted">管理家族成员信息</p>
          </Link>
          
          <Link
            href={`/t/${tenantSlug}/members`}
            className="bg-white rounded-xl p-8 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
          >
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">👥</div>
            <h3 className="text-lg font-semibold mb-2">成员管理</h3>
            <p className="text-sm text-ink-muted">邀请协作成员</p>
          </Link>
          
          <Link
            href={`/t/${tenantSlug}/files`}
            className="bg-white rounded-xl p-8 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
          >
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">📁</div>
            <h3 className="text-lg font-semibold mb-2">文件管理</h3>
            <p className="text-sm text-ink-muted">上传照片和文档</p>
          </Link>
          
          <Link
            href={`/t/${tenantSlug}/analytics`}
            className="bg-white rounded-xl p-8 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
          >
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">📊</div>
            <h3 className="text-lg font-semibold mb-2">访问统计</h3>
            <p className="text-sm text-ink-muted">查看家族空间访问数据</p>
          </Link>
          
          <Link
            href={`/t/${tenantSlug}/records`}
            className="bg-white rounded-xl p-8 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
          >
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">📚</div>
            <h3 className="text-lg font-semibold mb-2">原始资料</h3>
            <p className="text-sm text-ink-muted">管理族谱来源记录</p>
          </Link>
          
          <Link
            href={`/t/${tenantSlug}/export`}
            className="bg-white rounded-xl p-8 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
          >
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">📥</div>
            <h3 className="text-lg font-semibold mb-2">数据导出</h3>
            <p className="text-sm text-ink-muted">导出 Excel 文件备份</p>
          </Link>
          
          <Link
            href={`/t/${tenantSlug}/subscription`}
            className="bg-gradient-to-br from-vermillion/10 to-vermillion/5 rounded-xl p-8 border border-vermillion/20 hover:shadow-lg transition-all hover:-translate-y-1 group"
          >
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">💎</div>
            <h3 className="text-lg font-semibold mb-2">升级套餐</h3>
            <p className="text-sm text-ink-muted">解锁更多功能</p>
          </Link>
        </div>
        
        {/* Info Card */}
        <div className="mt-12 bg-white rounded-xl border border-ink/5 p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <span>📋</span> 快速开始
          </h3>
          <div className="grid md:grid-cols-3 gap-6 text-sm">
            <div>
              <div className="font-medium text-vermillion mb-1">第一步</div>
              <p className="text-ink-muted">添加始祖和核心人物，建立家族基础</p>
            </div>
            <div>
              <div className="font-medium text-vermillion mb-1">第二步</div>
              <p className="text-ink-muted">邀请家人加入，共同完善族谱信息</p>
            </div>
            <div>
              <div className="font-medium text-vermillion mb-1">第三步</div>
              <p className="text-ink-muted">上传照片和文档，记录家族珍贵记忆</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}