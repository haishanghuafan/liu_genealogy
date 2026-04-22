"use client"

import { useState, useEffect } from "react"
import Link from "next/link"

interface Permission {
  id: string
  code: string
  name: string
  group: string
  description: string | null
  resource_type: string
  tenant_id: string | null
}

interface PermissionGroup {
  [key: string]: Permission[]
}

export default function AdminPermissionsPage() {
  const [activeTab, setActiveTab] = useState<"system" | "tenant">("system")
  const [permissionGroups, setPermissionGroups] = useState<PermissionGroup>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchData()
  }, [activeTab])

  const fetchData = async () => {
    const token = localStorage.getItem("access_token") || ""
    try {
      const scope = activeTab
      const permsRes = await fetch(`http://localhost:8012/api/v1/admin/permissions/list?scope=${scope}`, {
        headers: { "Authorization": `Bearer ${token}` }
      })

      const permsData = await permsRes.json()
      if (permsData.success) setPermissionGroups(permsData.data.groups)
    } catch (err) {
      setError("加载失败")
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

  return (
    <main className="min-h-screen bg-paper">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/admin/roles" className="text-ink-muted hover:text-ink flex items-center gap-1">
              <span>🔐</span> 角色管理
            </Link>
            <Link href="/dashboard" className="text-ink-muted hover:text-ink flex items-center gap-1">
              <span>←</span> 返回控制台
            </Link>
          </div>
        </div>
      </nav>

      <div className="pt-24 px-4 max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-serif font-semibold mb-2">📋 权限管理</h1>
          <p className="text-ink-muted">查看系统所有可用权限</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-vermillion/5 border border-vermillion/20 text-vermillion">
            ⚠️ {error}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-ink/10">
          <button
            onClick={() => setActiveTab("system")}
            className={`pb-3 px-2 font-medium border-b-2 transition-colors ${
              activeTab === "system" ? "border-vermillion text-vermillion" : "border-transparent text-ink-muted"
            }`}
          >
            🏛️ 系统级权限
          </button>
          <button
            onClick={() => setActiveTab("tenant")}
            className={`pb-3 px-2 font-medium border-b-2 transition-colors ${
              activeTab === "tenant" ? "border-vermillion text-vermillion" : "border-transparent text-ink-muted"
            }`}
          >
            🏠 租户级权限
          </button>
        </div>

        <div className="space-y-6">
          {Object.entries(permissionGroups).map(([group, perms]) => (
            <div key={group} className="bg-white rounded-xl border border-ink/5 overflow-hidden">
              <div className="px-6 py-4 bg-paper-warm border-b border-ink/5">
                <h3 className="font-semibold">{group}</h3>
              </div>
              <div className="divide-y divide-ink/5">
                {perms.map((perm) => (
                  <div key={perm.id} className="px-6 py-3 flex items-center justify-between">
                    <div>
                      <div className="font-medium">{perm.name}</div>
                      <div className="text-sm text-ink-muted font-mono">{perm.code}</div>
                    </div>
                    <div className="text-sm text-ink-muted max-w-xs text-right">
                      {perm.description || "-"}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
