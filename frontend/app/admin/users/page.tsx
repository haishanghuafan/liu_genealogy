"use client"

import { useState, useEffect } from "react"
import Link from "next/link"

interface User {
  id: string
  email: string
  nickname: string | null
  avatar: string | null
  system_role: string
  is_active: boolean
  email_verified: boolean
  created_at: string
  last_login_at: string | null
}

const ROLE_OPTIONS = [
  { value: "user", label: "普通用户" },
  { value: "operator", label: "运营人员" },
  { value: "super_admin", label: "超级管理员" },
]

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [editingUser, setEditingUser] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [search, setSearch] = useState("")

  const [formData, setFormData] = useState<{
    nickname: string
    system_role: string
    is_active: boolean
  } | null>(null)

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      if (!token) {
        setError("请先登录")
        setLoading(false)
        return
      }

      const res = await fetch("http://localhost:8012/api/v1/auth/admin/users", {
        headers: { "Authorization": `Bearer ${token}` }
      })

      if (res.status === 401 || res.status === 403) {
        setError("需要超级管理员权限")
        setLoading(false)
        return
      }

      if (!res.ok) {
        setError(`加载失败 (HTTP ${res.status})`)
        setLoading(false)
        return
      }

      const data = await res.json()
      if (data.success) {
        setUsers(data.data)
      } else {
        setError(data.message || "加载失败")
      }
    } catch (err) {
      setError("网络错误")
    } finally {
      setLoading(false)
    }
  }

  const openEditModal = (user: User) => {
    setEditingUser(user.id)
    setFormData({
      nickname: user.nickname || "",
      system_role: user.system_role,
      is_active: user.is_active,
    })
    setError("")
    setSuccess("")
  }

  const handleSave = async () => {
    if (!formData || !editingUser) return

    setSaving(true)
    setError("")
    setSuccess("")

    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8012/api/v1/auth/admin/users/${editingUser}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })

      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        setEditingUser(null)
        fetchUsers()
      } else {
        setError(data.detail || data.message || "更新失败")
      }
    } catch (err) {
      setError("网络错误")
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (userId: string, email: string) => {
    if (!confirm(`确定要删除用户 ${email} 吗？`)) return

    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8012/api/v1/auth/admin/users/${userId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      })

      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        fetchUsers()
      } else {
        setError(data.detail || data.message || "删除失败")
      }
    } catch (err) {
      setError("网络错误")
    }
  }

  const filteredUsers = users.filter(u =>
    u.email.toLowerCase().includes(search.toLowerCase()) ||
    (u.nickname && u.nickname.toLowerCase().includes(search.toLowerCase()))
  )

  const ROLE_NAMES: Record<string, string> = {
    user: "普通用户",
    operator: "运营人员",
    super_admin: "超级管理员",
    admin: "超级管理员",
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
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-ink-muted hover:text-ink flex items-center gap-1">
              <span>←</span> 返回控制台
            </Link>
          </div>
        </div>
      </nav>

      <div className="pt-24 px-4 max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-serif font-semibold mb-4">👥 用户管理</h1>
          <p className="text-ink-muted">管理平台所有用户</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-vermillion/5 border border-vermillion/20 text-vermillion flex items-center gap-2">
            <span>⚠️</span> {error}
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 rounded-lg bg-green-50 border border-green-200 text-green-700 flex items-center gap-2">
            <span>✅</span> {success}
          </div>
        )}

        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="搜索邮箱或昵称..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-md border border-gray-300 rounded-lg px-4 py-2"
          />
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-xl border border-ink/5 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">邮箱</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">昵称</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">角色</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">注册时间</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">最后登录</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm">{user.email}</td>
                  <td className="px-6 py-4 text-sm">{user.nickname || "-"}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-2 py-1 rounded text-xs ${
                      user.system_role === "super_admin" ? "bg-amber-100 text-amber-800" :
                      user.system_role === "operator" ? "bg-blue-100 text-blue-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {ROLE_NAMES[user.system_role] || user.system_role || "普通用户"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-2 py-1 rounded text-xs ${
                      user.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                    }`}>
                      {user.is_active ? "活跃" : "禁用"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString("zh-CN")}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {user.last_login_at ? new Date(user.last_login_at).toLocaleDateString("zh-CN") : "从未登录"}
                  </td>
                  <td className="px-6 py-4 text-sm text-right space-x-2">
                    <button
                      onClick={() => openEditModal(user)}
                      className="text-vermillion hover:underline"
                    >
                      编辑
                    </button>
                    {user.system_role !== "super_admin" && (
                      <button
                        onClick={() => handleDelete(user.id, user.email)}
                        className="text-red-600 hover:underline"
                      >
                        删除
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredUsers.length === 0 && (
            <div className="text-center py-12 text-ink-muted">
              <div className="text-4xl mb-4">👤</div>
              <p>暂无用户</p>
            </div>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      {editingUser && formData && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-6">编辑用户</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">昵称</label>
                <input
                  type="text"
                  value={formData.nickname}
                  onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">角色</label>
                <select
                  value={formData.system_role}
                  onChange={(e) => setFormData({ ...formData, system_role: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  {ROLE_OPTIONS.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <span className="text-sm">启用账号</span>
                </label>
              </div>
            </div>

            <div className="flex gap-3 mt-6 pt-6 border-t">
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex-1 bg-vermillion text-white py-3 rounded-lg hover:bg-vermillion-dark transition-colors disabled:opacity-50"
              >
                {saving ? "保存中..." : "保存"}
              </button>
              <button
                onClick={() => setEditingUser(null)}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
