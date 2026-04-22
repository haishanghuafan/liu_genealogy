"use client"

import { useState, useEffect } from "react"
import Link from "next/link"

interface Tenant {
  id: string
  name: string
  slug: string
  surname: string
  is_public: boolean
  plan: string
  created_at: string
}

interface User {
  id: string
  email: string
  nickname: string | null
  system_role: string
  is_active: boolean
  created_at: string
}

export default function AdminTenantsPage() {
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [users, setUsers] = useState<User[]>([])
  const [activeTab, setActiveTab] = useState<"tenants" | "users">("tenants")
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchData()
  }, [])
  
  const fetchData = async () => {
    const token = localStorage.getItem("access_token") || ""
    try {
      const tenantsRes = await fetch("http://localhost:8012/api/v1/tenants", {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const tenantsData = await tenantsRes.json()
      if (tenantsData.success) setTenants(tenantsData.data)
      
      const usersRes = await fetch("http://localhost:8012/api/v1/auth/admin/users", {
        headers: { "Authorization": `Bearer ${token}` }
      })
      if (usersRes.ok) {
        const usersData = await usersRes.json()
        if (usersData.success) setUsers(usersData.data)
      }
    } catch (err) {
      console.error("Failed to fetch")
    } finally {
      setLoading(false)
    }
  }
  
  const PLAN_NAMES: Record<string, string> = {
    free: "免费版",
    basic: "基础版",
    professional: "专业版",
    enterprise: "企业版",
  }
  
  const ROLE_NAMES: Record<string, string> = {
    user: "普通用户",
    operator: "运营人员",
    super_admin: "超级管理员",
  }
  
  return (
    <main className="min-h-screen bg-paper">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex items-center gap-2">
              <span className="text-2xl">📜</span>
              <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
            </Link>
            <span className="text-ink-muted text-sm">后台管理</span>
          </div>
          <Link href="/dashboard" className="text-ink-muted hover:text-ink flex items-center gap-1">
            <span>←</span> 返回
          </Link>
        </div>
      </nav>
      
      <div className="pt-24 px-4 max-w-6xl mx-auto">
        <h1 className="text-3xl font-serif font-semibold mb-8">⚙️ 平台管理</h1>
        
        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-ink/10">
          <button
            onClick={() => setActiveTab("tenants")}
            className={`pb-3 px-2 font-medium border-b-2 transition-colors ${
              activeTab === "tenants" ? "border-vermillion text-vermillion" : "border-transparent text-ink-muted"
            }`}
          >
            🏢 租户管理 ({tenants.length})
          </button>
          <button
            onClick={() => setActiveTab("users")}
            className={`pb-3 px-2 font-medium border-b-2 transition-colors ${
              activeTab === "users" ? "border-vermillion text-vermillion" : "border-transparent text-ink-muted"
            }`}
          >
            👥 用户管理 ({users.length})
          </button>
        </div>
        
        {loading ? (
          <div className="text-center py-20">
            <div className="text-4xl mb-4">⏳</div>
            <p className="text-ink-muted">加载中...</p>
          </div>
        ) : activeTab === "tenants" ? (
          /* Tenants Table */
          <div className="bg-white rounded-xl border border-ink/5 overflow-hidden">
            <table className="w-full">
              <thead className="bg-paper-warm">
                <tr>
                  <th className="text-left px-6 py-4 font-medium">家族名称</th>
                  <th className="text-left px-6 py-4 font-medium">姓氏</th>
                  <th className="text-left px-6 py-4 font-medium">标识</th>
                  <th className="text-left px-6 py-4 font-medium">套餐</th>
                  <th className="text-left px-6 py-4 font-medium">状态</th>
                  <th className="text-left px-6 py-4 font-medium">创建时间</th>
                  <th className="text-right px-6 py-4 font-medium">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink/5">
                {tenants.map((tenant) => (
                  <tr key={tenant.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium">{tenant.name}</td>
                    <td className="px-6 py-4">{tenant.surname}</td>
                    <td className="px-6 py-4 text-sm text-ink-muted font-mono">{tenant.slug}</td>
                    <td className="px-6 py-4">
                      <span className={`text-xs px-2 py-1 rounded ${
                        tenant.plan === "free" ? "bg-gray-100 text-gray-600" :
                        tenant.plan === "enterprise" ? "bg-purple-100 text-purple-700" :
                        "bg-vermillion/10 text-vermillion"
                      }`}>
                        {PLAN_NAMES[tenant.plan] || tenant.plan}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-xs px-2 py-1 rounded ${tenant.is_public ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
                        {tenant.is_public ? "公开" : "私密"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-ink-muted">
                      {new Date(tenant.created_at).toLocaleDateString("zh-CN")}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex justify-end gap-2">
                        <Link href={`/t/${tenant.slug}/subscription`} className="text-sm text-vermillion hover:underline">
                          订阅
                        </Link>
                        <Link href={`/t/${tenant.slug}/members`} className="text-sm text-vermillion hover:underline">
                          成员
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {tenants.length === 0 && (
              <div className="text-center py-12 text-ink-muted">
                <div className="text-4xl mb-4">🏢</div>
                <p>暂无租户</p>
              </div>
            )}
          </div>
        ) : (
          /* Users Table */
          <div className="bg-white rounded-xl border border-ink/5 overflow-hidden">
            <table className="w-full">
              <thead className="bg-paper-warm">
                <tr>
                  <th className="text-left px-6 py-4 font-medium">昵称</th>
                  <th className="text-left px-6 py-4 font-medium">邮箱</th>
                  <th className="text-left px-6 py-4 font-medium">角色</th>
                  <th className="text-left px-6 py-4 font-medium">状态</th>
                  <th className="text-left px-6 py-4 font-medium">注册时间</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink/5">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium">{user.nickname || "-"}</td>
                    <td className="px-6 py-4">{user.email}</td>
                    <td className="px-6 py-4">
                      <span className={`text-xs px-2 py-1 rounded ${
                        user.system_role === "super_admin" ? "bg-amber-100 text-amber-700" :
                        user.system_role === "operator" ? "bg-blue-100 text-blue-700" :
                        "bg-gray-100 text-gray-600"
                      }`}>
                        {ROLE_NAMES[user.system_role] || user.system_role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`text-xs px-2 py-1 rounded ${user.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                        {user.is_active ? "活跃" : "禁用"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-ink-muted">
                      {new Date(user.created_at).toLocaleDateString("zh-CN")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {users.length === 0 && (
              <div className="text-center py-12 text-ink-muted">
                <div className="text-4xl mb-4">👥</div>
                <p>暂无用户数据</p>
              </div>
            )}
          </div>
        )}
        
        {/* Platform Stats */}
        <div className="mt-10">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <span>📊</span> 平台概览
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl p-6 border border-ink/5">
              <div className="text-sm text-ink-muted mb-1">总家族数</div>
              <div className="text-3xl font-serif font-semibold">{tenants.length}</div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-ink/5">
              <div className="text-sm text-ink-muted mb-1">免费版</div>
              <div className="text-3xl font-serif font-semibold">
                {tenants.filter(t => t.plan === "free").length}
              </div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-ink/5">
              <div className="text-sm text-ink-muted mb-1">付费版</div>
              <div className="text-3xl font-serif font-semibold text-vermillion">
                {tenants.filter(t => t.plan !== "free").length}
              </div>
            </div>
            <div className="bg-white rounded-xl p-6 border border-ink/5">
              <div className="text-sm text-ink-muted mb-1">公开家族</div>
              <div className="text-3xl font-serif font-semibold">
                {tenants.filter(t => t.is_public).length}
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}