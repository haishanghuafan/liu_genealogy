"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"

interface TenantInfo {
  id: string
  name: string
  slug: string
  surname: string
}

export default function TenantHomePage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  const [tenant, setTenant] = useState<TenantInfo | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (tenantSlug) {
      fetchTenantInfo()
    }
  }, [tenantSlug])

  const fetchTenantInfo = async () => {
    try {
      const res = await fetch(`/api/v1/tenants?slug=${tenantSlug}`)
      const data = await res.json()
      if (data.data && data.data.length > 0) {
        setTenant(data.data[0])
      }
    } catch (error) {
      console.error("Failed to fetch tenant:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-paper flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl mb-4 animate-bounce">⏳</div>
          <p className="text-ink-muted">加载中...</p>
        </div>
      </main>
    )
  }

  const tenantName = tenant?.name || `${tenantSlug}家族`

  return (
    <main className="min-h-screen bg-paper">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <div className="hidden md:flex items-center gap-6">
            <Link href={`/${tenantSlug}`} className="text-vermillion font-medium">
              首页
            </Link>
            <Link href={`/${tenantSlug}/family-tree`} className="text-ink-muted hover:text-ink transition-colors">
              族谱树
            </Link>
            <Link href="/tenants" className="text-ink-muted hover:text-ink transition-colors">
              浏览家族
            </Link>
          </div>
        </div>
      </nav>

      <div className="pt-32 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-vermillion/10 text-vermillion text-4xl font-serif font-bold mb-8 border-2 border-vermillion/20">
            {tenant?.surname?.charAt(0) || tenantSlug.charAt(0).toUpperCase()}
          </div>
          
          <h1 className="text-4xl md:text-5xl font-serif font-bold text-ink mb-4">
            {tenantName}
          </h1>
          
          <p className="text-lg text-ink-muted mb-12">
            传承家族记忆，让血脉有迹可循
          </p>

          <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
            <Link
              href={`/${tenantSlug}/family-tree`}
              className="bg-vermillion text-white p-8 rounded-xl hover:bg-vermillion-dark transition-colors flex flex-col items-center gap-3 group"
            >
              <span className="text-5xl group-hover:scale-110 transition-transform">🌳</span>
              <span className="text-xl font-semibold">查看族谱树</span>
              <span className="text-white/80 text-sm">可视化家族世代脉络</span>
            </Link>

            <Link
              href={`/${tenantSlug}/persons`}
              className="bg-white text-ink border border-ink/10 p-8 rounded-xl hover:bg-paper-warm transition-colors flex flex-col items-center gap-3 group"
            >
              <span className="text-5xl group-hover:scale-110 transition-transform">👥</span>
              <span className="text-xl font-semibold">家族成员</span>
              <span className="text-ink-muted text-sm">浏览所有成员列表</span>
            </Link>
          </div>
        </div>
      </div>

      <footer className="py-12 mt-20 border-t border-ink/10">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-ink-muted">
          <p>📜 © 2026 族谱云 · 传承家族记忆</p>
        </div>
      </footer>
    </main>
  )
}
