"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"

interface Member {
  id: string
  user_id: string
  email: string
  nickname: string | null
  avatar: string | null
  role: string
  person_id: string | null
  joined_at: string
  invited_by: string | null
}

interface QuotaStatus {
  plan: string
  quotas: {
    persons: { current: number; limit: number; allowed: boolean }
    members: { current: number; limit: number; allowed: boolean }
    admins: { current: number; limit: number; allowed: boolean }
    storage: { current_mb: number; limit_mb: number; allowed: boolean }
  }
  features: Record<string, boolean | string>
}

const ROLE_DISPLAY: Record<string, string> = {
  guest: "受邀访客",
  member: "家族成员",
  editor: "编辑人员",
  reviewer: "审核人员",
  tenant_admin: "家族管理员",
}

export default function MembersPage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [members, setMembers] = useState<Member[]>([])
  const [quotas, setQuotas] = useState<QuotaStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [showInvite, setShowInvite] = useState(false)
  const [inviteEmail, setInviteEmail] = useState("")
  const [inviteRole, setInviteRole] = useState("member")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  
  useEffect(() => {
    fetchData()
  }, [tenantSlug])
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      
      const [membersRes, quotasRes] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/members`, {
          headers: { "Authorization": `Bearer ${token}` }
        }),
        fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/subscription/quotas`, {
          headers: { "Authorization": `Bearer ${token}` }
        })
      ])
      
      const membersData = await membersRes.json()
      const quotasData = await quotasRes.json()
      
      if (membersData.success) setMembers(membersData.data)
      setQuotas(quotasData)
    } catch (err) {
      setError("加载数据失败")
    } finally {
      setLoading(false)
    }
  }
  
  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")
    
    try {
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/members/invite`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token") || ""}`
        },
        body: JSON.stringify({ email: inviteEmail, role: inviteRole })
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        setInviteEmail("")
        setShowInvite(false)
        fetchData()
      } else {
        setError(data.message || "邀请失败")
      }
    } catch (err) {
      setError("网络错误")
    }
  }
  
  const handleUpdateRole = async (memberId: string, newRole: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/members/${memberId}/role`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token") || ""}`
        },
        body: JSON.stringify({ role: newRole })
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        fetchData()
      } else {
        setError(data.message || "更新失败")
      }
    } catch (err) {
      setError("网络错误")
    }
  }
  
  const handleRemove = async (memberId: string) => {
    if (!confirm("确定要移除该成员吗？")) return
    
    try {
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/members/${memberId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${localStorage.getItem("access_token") || ""}` }
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        fetchData()
      } else {
        setError(data.message || "移除失败")
      }
    } catch (err) {
      setError("网络错误")
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
  
  const canInviteMore = quotas?.quotas.members.allowed ?? false
  
  return (
    <main className="min-h-screen bg-paper">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href={`/t/${tenantSlug}`} className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <Link href={`/t/${tenantSlug}`} className="text-ink-muted hover:text-ink flex items-center gap-1">
            <span>←</span> 返回
          </Link>
        </div>
      </nav>
      
      <div className="pt-24 px-4 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-serif font-semibold mb-2">👥 成员管理</h1>
            <p className="text-ink-muted">
              当前成员: {quotas?.quotas.members.current || 0} / {quotas?.quotas.members.limit === -1 ? "无限" : quotas?.quotas.members.limit}
            </p>
          </div>
          <button
            onClick={() => setShowInvite(true)}
            disabled={!canInviteMore}
            className="bg-vermillion text-white px-6 py-3 rounded-lg hover:bg-vermillion-dark transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            <span>➕</span> 邀请成员
          </button>
        </div>
        
        {/* Quota Warning */}
        {!canInviteMore && (
          <div className="mb-6 p-4 rounded-lg bg-vermillion/5 border border-vermillion/20 text-vermillion">
            ⚠️ 成员配额已满，请升级套餐以邀请更多成员
            <Link href={`/t/${tenantSlug}/subscription`} className="underline ml-2">升级套餐</Link>
          </div>
        )}
        
        {/* Messages */}
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
        
        {/* Invite Modal */}
        {showInvite && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 w-full max-w-md">
              <h2 className="text-xl font-semibold mb-4">邀请成员</h2>
              <form onSubmit={handleInvite} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">邮箱地址</label>
                  <input
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
                    placeholder="user@example.com"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">角色</label>
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-ink/10 focus:border-vermillion outline-none"
                  >
                    <option value="guest">受邀访客 - 可查看公开内容</option>
                    <option value="member">家族成员 - 可查看成员内容</option>
                    <option value="editor">编辑人员 - 可编辑族谱</option>
                    <option value="reviewer">审核人员 - 可审核变更</option>
                    <option value="tenant_admin">家族管理员 - 全部权限</option>
                  </select>
                </div>
                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowInvite(false)}
                    className="flex-1 py-2 rounded-lg border border-ink/10 hover:bg-gray-50"
                  >
                    取消
                  </button>
                  <button
                    type="submit"
                    className="flex-1 py-2 rounded-lg bg-vermillion text-white hover:bg-vermillion-dark"
                  >
                    发送邀请
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
        
        {/* Members List */}
        <div className="bg-white rounded-xl border border-ink/5 overflow-hidden">
          <table className="w-full">
            <thead className="bg-paper-warm">
              <tr>
                <th className="text-left px-6 py-4 font-medium">成员</th>
                <th className="text-left px-6 py-4 font-medium">角色</th>
                <th className="text-left px-6 py-4 font-medium">加入时间</th>
                <th className="text-right px-6 py-4 font-medium">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink/5">
              {members.map((member) => (
                <tr key={member.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-vermillion/10 flex items-center justify-center text-lg">
                        {member.avatar ? "👤" : "👤"}
                      </div>
                      <div>
                        <div className="font-medium">{member.nickname || member.email}</div>
                        <div className="text-sm text-ink-muted">{member.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <select
                      value={member.role}
                      onChange={(e) => handleUpdateRole(member.id, e.target.value)}
                      className="px-3 py-1 rounded-lg border border-ink/10 text-sm"
                    >
                      <option value="guest">受邀访客</option>
                      <option value="member">家族成员</option>
                      <option value="editor">编辑人员</option>
                      <option value="reviewer">审核人员</option>
                      <option value="tenant_admin">家族管理员</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 text-sm text-ink-muted">
                    {new Date(member.joined_at).toLocaleDateString("zh-CN")}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() => handleRemove(member.id)}
                      className="text-vermillion hover:underline text-sm"
                    >
                      移除
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {members.length === 0 && (
            <div className="text-center py-12">
              <div className="text-4xl mb-4">👥</div>
              <p className="text-ink-muted">暂无成员</p>
              <button
                onClick={() => setShowInvite(true)}
                className="mt-4 text-vermillion hover:underline"
              >
                邀请第一位成员
              </button>
            </div>
          )}
        </div>
        
        {/* Role Legend */}
        <div className="mt-8 p-6 bg-white rounded-xl border border-ink/5">
          <h3 className="font-semibold mb-4">角色权限说明</h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div><strong>受邀访客</strong> - 可查看公开内容、简单搜索</div>
            <div><strong>家族成员</strong> - 可查看成员级内容</div>
            <div><strong>编辑人员</strong> - 可添加/编辑人物、上传媒体</div>
            <div><strong>审核人员</strong> - 可审核数据变更</div>
            <div><strong>家族管理员</strong> - 全部权限，包括成员管理</div>
          </div>
        </div>
      </div>
    </main>
  )
}