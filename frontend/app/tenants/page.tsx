"use client"

import Link from "next/link"
import { useState } from "react"

export default function TenantsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  
  // TODO: Fetch from API
  const tenants = [
    // Empty for now
  ]
  
  return (
    <main className="min-h-screen bg-paper">
      {/* Navigation */}
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
            <Link href="/login" className="text-ink-muted hover:text-ink transition-colors">登录</Link>
            <Link href="/register" className="bg-vermillion text-white px-4 py-2 rounded-lg hover:bg-vermillion-dark transition-colors flex items-center gap-1">
              <span>✨</span> 创建族谱
            </Link>
          </div>
        </div>
      </nav>
      
      {/* Main Content */}
      <div className="pt-24 px-4 max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-serif font-semibold mb-2">🏠 家族列表</h1>
          <p className="text-ink-muted">发现和浏览公开的家族族谱</p>
        </div>
        
        {/* Search */}
        <div className="mb-8">
          <div className="relative max-w-md">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-ink-muted">🔍</span>
            <input
              type="text"
              className="w-full pl-12 pr-4 py-3 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
              placeholder="搜索家族名称..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        
        {/* Tenants Grid */}
        {tenants.length === 0 ? (
          <div className="bg-white rounded-xl border border-ink/5 p-12 text-center">
            <div className="text-6xl mb-6">🏰</div>
            <h2 className="text-xl font-serif font-semibold mb-3">暂无公开家族</h2>
            <p className="text-ink-muted mb-8 max-w-md mx-auto">
              成为第一个创建家族的用户，为您的家族建立数字族谱，让血脉传承，让记忆永存。
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
            {/* Tenant cards would go here */}
          </div>
        )}
      </div>
      
      {/* Footer */}
      <footer className="py-12 mt-20 border-t border-ink/10">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-ink-muted">
          <p>📜 © 2026 族谱云 · 传承家族记忆</p>
        </div>
      </footer>
    </main>
  )
}