"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import api from "@/lib/api"
import { UserMenu } from "@/components/layout/UserMenu"

interface Tenant {
  id: string
  name: string
  slug: string
  surname: string
  is_public: boolean
  plan: string
  created_at: string
}

export default function TenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoggedIn, setIsLoggedIn] = useState(false)

  useEffect(() => {
    // Check login status
    const token = localStorage.getItem("access_token")
    setIsLoggedIn(!!token)

    fetchTenants()
  }, [])

  const fetchTenants = async () => {
    try {
      const response = await api.get<{ data: Tenant[] }>("/tenants")
      setTenants(response.data || [])
    } catch (error) {
      console.error("Failed to fetch tenants:", error)
    } finally {
      setLoading(false)
    }
  }

  const filteredTenants = tenants.filter(tenant =>
    tenant.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tenant.surname.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <main className="min-h-screen bg-paper">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <Link href="/tenants" className="text-vermillion font-medium flex items-center gap-1">
              <span>🔍</span> 浏览家族
            </Link>
            {isLoggedIn ? (
              <UserMenu />
            ) : (
              <>
                <Link href="/login" className="text-ink-muted hover:text-ink transition-colors">登录</Link>
                <Link href="/register" className="bg-vermillion text-white px-4 py-2 rounded-lg hover:bg-vermillion-dark transition-colors flex items-center gap-1">
                  <span>✨</span> 创建族谱
                </Link>
              </>
            )}
          </div>

          {isLoggedIn ? (
            <div className="md:hidden">
              <UserMenu />
            </div>
          ) : (
            <Link href="/register" className="md:hidden bg-vermillion text-white px-4 py-2 rounded-lg text-sm">
              开始
            </Link>
          )}
        </div>
      </nav>

      <div className="pt-24 px-4 max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-serif font-semibold mb-2">🏠 家族列表</h1>
          <p className="text-ink-muted">发现和浏览公开的家族族谱</p>
        </div>

        <div className="mb-8">
          <div className="relative max-w-md">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-muted">🔍</span>
            <input
              type="text"
              className="w-full pl-12 pr-4 py-3 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
              placeholder="搜索家族名称或姓氏..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {loading ? (
          <div className="bg-white rounded-xl border border-ink/5 p-12 text-center">
            <div className="text-4xl mb-4 animate-bounce">⏳</div>
            <p className="text-ink-muted">加载中...</p>
          </div>
        ) : filteredTenants.length === 0 ? (
          <div className="bg-white rounded-xl border border-ink/5 p-12 text-center">
            <div className="text-6xl mb-6">🏰</div>
            <h2 className="text-xl font-serif font-semibold mb-3">
              {searchQuery ? "未找到匹配的家族" : "暂无公开家族"}
            </h2>
            <p className="text-ink-muted mb-8 max-w-md mx-auto">
              {searchQuery ? "请尝试其他搜索词" : "成为第一个创建家族的用户，为您的家族建立数字族谱"}
            </p>
            <div className="flex justify-center gap-4 flex-wrap">
              <Link href="/register" className="bg-vermillion text-white px-6 py-3 rounded-lg hover:bg-vermillion-dark transition-colors inline-flex items-center gap-2">
                <span>🚀</span> 免费创建族谱
              </Link>
              <Link href="/" className="bg-white text-ink border border-ink/10 px-6 py-3 rounded-lg hover:bg-paper-warm transition-colors inline-flex items-center gap-2">
                <span>←</span> 返回首页
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTenants.map((tenant) => (
              <Link
                key={tenant.id}
                href={`/${tenant.slug}`}
                className="bg-white rounded-xl border border-ink/5 p-6 hover:shadow-lg hover:-translate-y-1 transition-all group"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-full bg-vermillion/10 flex items-center justify-center text-2xl">
                    {tenant.surname.charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg group-hover:text-vermillion transition-colors">
                      {tenant.name}
                    </h3>
                    <p className="text-sm text-ink-muted">刘氏</p>
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm text-ink-muted">
                  <span className="bg-paper px-2 py-1 rounded">公开</span>
                  <span className="group-hover:translate-x-1 transition-transform">进入 →</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      <footer className="py-12 mt-20 border-t border-ink/10">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-ink-muted">
          <p>📜 © 2026 族谱云 · 传承家族记忆</p>
        </div>
      </footer>
    </main>
  )
}
