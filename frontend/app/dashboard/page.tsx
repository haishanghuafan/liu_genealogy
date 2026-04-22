"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { UserMenu } from "@/components/layout/UserMenu"

interface UserInfo {
  id: string
  email: string
  nickname: string | null
  system_role: string
}

interface TenantInfo {
  id: string
  name: string
  slug: string
  role: string
  plan: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<UserInfo | null>(null)
  const [tenants, setTenants] = useState<TenantInfo[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchData()
  }, [])
  
  const fetchData = async () => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }
    
    try {
      // Get current user info
      const meData = await api.get("/auth/me")
      setUser(meData)
      
      // Get all tenants and filter by user's access
      const tenantsData = await api.get("/tenants")
      setTenants(tenantsData.data || [])
    } catch (err: any) {
      if (err.message?.includes("Unauthorized") || err.message?.includes("Not authenticated") || err.message?.includes("401")) {
        localStorage.removeItem("access_token")
        router.push("/login")
      } else {
        console.error("Failed to fetch data:", err)
      }
    } finally {
      setLoading(false)
    }
  }
  
  const handleLogout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    router.push("/login")
  }
  
  if (loading) {
    return (
      <main className="min-h-screen bg-paper">
        <div className="pt-32 px-4 max-w-6xl mx-auto text-center">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-ink-muted">加载中...</p>
        </div>
      </main>
    )
  }
  
  const isSuperAdmin = user?.system_role === "super_admin"
  
  return (
    <main className="min-h-screen bg-paper">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>

          <div className="flex items-center gap-4">
            <UserMenu />
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <div className="pt-24 px-4 max-w-6xl mx-auto">
        {/* Welcome */}
        <div className="mb-8">
          <h1 className="text-2xl font-serif font-semibold mb-2">
            👋 你好，{user?.nickname || user?.email?.split("@")[0] || "用户"}
          </h1>
          <p className="text-ink-muted">欢迎回到族谱云，开始管理您的家族档案</p>
        </div>
        
        {/* My Tenants */}
        <div className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span>🏠</span> 我的家族
            </h2>
            <Link 
              href="/tenants/create" 
              className="text-vermillion hover:underline text-sm flex items-center gap-1"
            >
              <span>➕</span> 创建新家族
            </Link>
          </div>
          
          {tenants.length > 0 ? (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {tenants.map((tenant) => (
                <div
                  key={tenant.id}
                  className="bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1"
                >
                  <Link href={`/t/${tenant.slug}`} className="block">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold">{tenant.name}</h3>
                      <span className="text-xs px-2 py-1 bg-vermillion/10 text-vermillion rounded">
                        {tenant.role === "tenant_admin" ? "管理员" : "成员"}
                      </span>
                    </div>
                    <div className="text-sm text-ink-muted">
                      套餐: {tenant.plan === "free" ? "免费版" : tenant.plan}
                    </div>
                  </Link>
                  <div className="mt-3 flex gap-2">
                    <Link 
                      href={`/t/${tenant.slug}/subscription`}
                      className="text-sm text-vermillion hover:underline"
                    >
                      💎 订阅管理
                    </Link>
                    {tenant.role === "tenant_admin" && (
                      <Link 
                        href={`/t/${tenant.slug}/members`}
                        className="text-sm text-vermillion hover:underline"
                      >
                        👥 成员管理
                      </Link>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-ink/5 p-8 text-center">
              <div className="text-5xl mb-4">🏠</div>
              <h3 className="text-lg font-semibold mb-2">您还没有加入任何家族</h3>
              <p className="text-ink-muted mb-6">创建一个新家族或让已有家族的管理员邀请您</p>
              <Link href="/tenants/create" className="bg-vermillion text-white px-6 py-3 rounded-lg hover:bg-vermillion-dark transition-colors inline-flex items-center gap-2">
                <span>✨</span> 创建第一个家族
              </Link>
            </div>
          )}
        </div>
        
        {/* Platform Management (Super Admin Only) */}
        {isSuperAdmin && (
          <div className="mb-10">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span>⚙️</span> 平台管理
            </h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Link
                href="/admin/tenants"
                className="bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1"
              >
                <div className="text-3xl mb-3">🏢</div>
                <h3 className="font-semibold mb-1">租户管理</h3>
                <p className="text-sm text-ink-muted">管理所有家族租户</p>
              </Link>
              
              <Link
                href="/admin/users"
                className="bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1"
              >
                <div className="text-3xl mb-3">👥</div>
                <h3 className="font-semibold mb-1">用户管理</h3>
                <p className="text-sm text-ink-muted">管理平台用户</p>
              </Link>
              
              <Link
                href="/admin/subscription-plans"
                className="bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1"
              >
                <div className="text-3xl mb-3">💎</div>
                <h3 className="font-semibold mb-1">套餐配置</h3>
                <p className="text-sm text-ink-muted">配置订阅套餐和价格</p>
              </Link>
              
              <Link
                href="/admin/stats"
                className="bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1"
              >
                <div className="text-3xl mb-3">📊</div>
                <h3 className="font-semibold mb-1">数据统计</h3>
                <p className="text-sm text-ink-muted">平台运营数据</p>
              </Link>
            </div>
          </div>
        )}
        
        {/* Quick Actions */}
        <div className="mb-10">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>⚡</span> 快捷操作
          </h2>
          <div className="grid sm:grid-cols-2 gap-4">
            <Link
              href="/tenants/create"
              className="bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl group-hover:scale-110 transition-transform">➕</div>
                <div>
                  <h3 className="font-semibold mb-1">创建新家族</h3>
                  <p className="text-sm text-ink-muted">开始记录您的家族历史</p>
                </div>
              </div>
            </Link>
            
            <Link
              href="/tenants"
              className="bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl group-hover:scale-110 transition-transform">🔍</div>
                <div>
                  <h3 className="font-semibold mb-1">浏览家族</h3>
                  <p className="text-sm text-ink-muted">查看和管理已创建的家族</p>
                </div>
              </div>
            </Link>
            
            <Link
              href="/settings"
              className="bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl group-hover:scale-110 transition-transform">⚙️</div>
                <div>
                  <h3 className="font-semibold mb-1">账号设置</h3>
                  <p className="text-sm text-ink-muted">管理个人信息和安全设置</p>
                </div>
              </div>
            </Link>
            
            <a
              href="http://localhost:8000/api/v1/docs"
              target="_blank"
              className="bg-white rounded-xl p-6 border border-ink/5 hover:shadow-lg transition-all hover:-translate-y-1 group"
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl group-hover:scale-110 transition-transform">📚</div>
                <div>
                  <h3 className="font-semibold mb-1">API 文档</h3>
                  <p className="text-sm text-ink-muted">开发者接口文档</p>
                </div>
              </div>
            </a>
          </div>
        </div>
        
        {/* Recent Activity */}
        <div>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>📋</span> 最近活动
          </h2>
          <div className="bg-white rounded-xl border border-ink/5 p-8 text-center">
            <div className="text-5xl mb-4">🌱</div>
            <h3 className="text-lg font-semibold mb-2">还没有活动</h3>
            <p className="text-ink-muted">创建您的第一个家族，开始记录家族故事吧！</p>
          </div>
        </div>
      </div>
    </main>
  )
}