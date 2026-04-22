"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { UserMenu } from "@/components/layout/UserMenu"

interface UserInfo {
  id: string
  email: string
  nickname: string | null
  phone: string | null
  system_role: string
  created_at: string
}

export default function ProfilePage() {
  const router = useRouter()
  const [user, setUser] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState({ type: "", text: "" })

  const [formData, setFormData] = useState({
    nickname: "",
    phone: "",
  })

  useEffect(() => {
    fetchUserInfo()
  }, [])

  const fetchUserInfo = async () => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }

    try {
      const response = await fetch("http://localhost:8012/api/v1/auth/me", {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.id) {
        setUser(data)
        setFormData({
          nickname: data.nickname || "",
          phone: data.phone || "",
        })
      } else {
        router.push("/login")
      }
    } catch (err) {
      console.error("Failed to fetch user info:", err)
      setMessage({ type: "error", text: "获取用户信息失败" })
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMessage({ type: "", text: "" })

    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }

    try {
      const response = await fetch("http://localhost:8012/api/v1/auth/me", {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()
      if (data.id) {
        setUser(data)
        setMessage({ type: "success", text: "个人信息更新成功" })
      } else {
        setMessage({ type: "error", text: data.message || "更新失败" })
      }
    } catch (err) {
      setMessage({ type: "error", text: "网络错误，请稍后重试" })
    } finally {
      setSaving(false)
    }
  }

  const getRoleName = (role: string) => {
    const roles: Record<string, string> = {
      super_admin: "超级管理员",
      admin: "管理员",
      user: "普通用户",
    }
    return roles[role] || role
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-paper">
        <div className="pt-32 px-4 max-w-4xl mx-auto text-center">
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
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="text-ink-muted hover:text-ink flex items-center gap-1">
              <span>←</span> 返回
            </Link>
            <div className="w-px h-6 bg-ink/10" />
            <UserMenu />
          </div>
        </div>
      </nav>

      <div className="pt-24 px-4 max-w-2xl mx-auto pb-20">
        <h1 className="text-3xl font-serif font-semibold mb-2">👤 个人信息</h1>
        <p className="text-ink-muted mb-8">管理您的账号信息</p>

        {/* Message */}
        {message.text && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.type === "success" ? "bg-green-50 text-green-700 border border-green-200" : "bg-red-50 text-red-700 border border-red-200"
          }`}>
            {message.text}
          </div>
        )}

        {/* User Info Card */}
        <div className="bg-white rounded-xl border border-ink/5 p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">账号信息</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between py-2 border-b border-ink/5">
              <span className="text-ink-muted">邮箱</span>
              <span className="font-medium">{user?.email}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-ink/5">
              <span className="text-ink-muted">角色</span>
              <span className="font-medium">{getRoleName(user?.system_role || "user")}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-ink/5">
              <span className="text-ink-muted">注册时间</span>
              <span className="font-medium">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString("zh-CN") : "-"}
              </span>
            </div>
          </div>
        </div>

        {/* Edit Form */}
        <div className="bg-white rounded-xl border border-ink/5 p-6">
          <h2 className="text-lg font-semibold mb-4">编辑资料</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-ink-muted mb-1">
                昵称
              </label>
              <input
                type="text"
                value={formData.nickname}
                onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
                placeholder="请输入昵称"
                maxLength={50}
              />
              <p className="text-xs text-ink-muted mt-1">用于显示的名称，不超过50个字符</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-ink-muted mb-1">
                手机号
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-2 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
                placeholder="请输入手机号"
              />
            </div>

            <div className="pt-4 flex gap-3">
              <button
                type="submit"
                disabled={saving}
                className="flex-1 bg-vermillion text-white px-6 py-2 rounded-lg hover:bg-vermillion-dark transition-colors disabled:opacity-50"
              >
                {saving ? "保存中..." : "保存修改"}
              </button>
              <Link
                href="/change-password"
                className="px-6 py-2 rounded-lg border border-ink/10 hover:bg-gray-50 transition-colors"
              >
                修改密码
              </Link>
            </div>
          </form>
        </div>
      </div>
    </main>
  )
}
