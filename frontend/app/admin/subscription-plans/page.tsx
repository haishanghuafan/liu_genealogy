"use client"

import { useState, useEffect } from "react"
import Link from "next/link"

interface Plan {
  id: string
  name: string
  price_cny: number
  price_usd: number
  billing_period: string | null
  features: {
    max_persons: number
    max_members: number
    max_storage_mb: number
    max_admins: number
    advanced_visualization: boolean
    data_export: boolean
    api_access: boolean
    custom_domain: boolean
    priority_support: string
  }
}

const PRIORITY_SUPPORT_OPTIONS = [
  { value: "community", label: "社区" },
  { value: "email", label: "邮件" },
  { value: "priority", label: "优先" },
  { value: "dedicated", label: "专属" },
]

export default function AdminSubscriptionPlansPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [editingPlan, setEditingPlan] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const [formData, setFormData] = useState<Plan | null>(null)

  useEffect(() => {
    fetchPlans()
  }, [])

  const fetchPlans = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch("http://localhost:8012/api/v1/subscription/admin/plans", {
        headers: { "Authorization": `Bearer ${token}` }
      })

      if (res.status === 401 || res.status === 403) {
        setError("需要超级管理员权限")
        return
      }

      const data = await res.json()
      if (data.success) setPlans(data.data)
    } catch (err) {
      setError("加载套餐失败")
    } finally {
      setLoading(false)
    }
  }

  const openEditModal = (plan: Plan) => {
    setEditingPlan(plan.id)
    setFormData({ ...plan, features: { ...plan.features } })
    setError("")
    setSuccess("")
  }

  const handleSave = async () => {
    if (!formData || !editingPlan) return

    setSaving(true)
    setError("")
    setSuccess("")

    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8012/api/v1/subscription/admin/plans/${editingPlan}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          name: formData.name,
          price_cny: formData.price_cny,
          price_usd: formData.price_usd,
          billing_period: formData.billing_period,
          features: formData.features,
        })
      })

      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        setEditingPlan(null)
        fetchPlans()
      } else {
        setError(data.detail || data.message || "更新失败")
      }
    } catch (err) {
      setError("网络错误")
    } finally {
      setSaving(false)
    }
  }

  const updateFeature = (key: string, value: any) => {
    if (!formData) return
    setFormData({
      ...formData,
      features: {
        ...formData.features,
        [key]: value,
      }
    })
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
          <h1 className="text-3xl font-serif font-semibold mb-4">💎 套餐配置管理</h1>
          <p className="text-ink-muted">编辑订阅套餐的价格和资源配额</p>
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

        <div className="space-y-6">
          {plans.map((plan) => (
            <div key={plan.id} className="bg-white rounded-xl border border-ink/5 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-semibold">{plan.name}</h2>
                  <p className="text-sm text-ink-muted">
                    ID: {plan.id} | 价格: ¥{plan.price_cny} CNY / ${plan.price_usd} USD
                    {plan.billing_period && ` / ${plan.billing_period === "yearly" ? "年" : "月"}`}
                  </p>
                </div>
                <button
                  onClick={() => openEditModal(plan)}
                  className="bg-vermillion text-white px-4 py-2 rounded-lg hover:bg-vermillion-dark transition-colors"
                >
                  编辑
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-ink-muted">人物上限</div>
                  <div className="font-semibold">{plan.features.max_persons === -1 ? "无限" : plan.features.max_persons}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-ink-muted">成员上限</div>
                  <div className="font-semibold">{plan.features.max_members === -1 ? "无限" : plan.features.max_members}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-ink-muted">存储上限</div>
                  <div className="font-semibold">{plan.features.max_storage_mb === -1 ? "无限" : `${plan.features.max_storage_mb}MB`}</div>
                </div>
                <div className="bg-gray-50 p-3 rounded">
                  <div className="text-ink-muted">管理员上限</div>
                  <div className="font-semibold">{plan.features.max_admins === -1 ? "无限" : plan.features.max_admins}</div>
                </div>
              </div>

              <div className="mt-4 flex gap-2 flex-wrap">
                {plan.features.advanced_visualization && <span className="px-2 py-1 bg-vermillion/10 text-vermillion rounded text-xs">高级可视化</span>}
                {plan.features.data_export && <span className="px-2 py-1 bg-vermillion/10 text-vermillion rounded text-xs">数据导出</span>}
                {plan.features.api_access && <span className="px-2 py-1 bg-vermillion/10 text-vermillion rounded text-xs">API 访问</span>}
                {plan.features.custom_domain && <span className="px-2 py-1 bg-vermillion/10 text-vermillion rounded text-xs">自定义域名</span>}
                <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">客服: {plan.features.priority_support}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Edit Modal */}
      {editingPlan && formData && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl my-8">
            <h2 className="text-xl font-semibold mb-6">编辑套餐: {formData.name}</h2>

            <div className="space-y-6">
              {/* Basic Info */}
              <div>
                <h3 className="font-medium mb-3 text-lg">基本信息</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">套餐名称</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">计费周期</label>
                    <select
                      value={formData.billing_period || ""}
                      onChange={(e) => setFormData({ ...formData, billing_period: e.target.value || null })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    >
                      <option value="">免费</option>
                      <option value="monthly">月付</option>
                      <option value="yearly">年付</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">价格 (CNY)</label>
                    <input
                      type="number"
                      value={formData.price_cny}
                      onChange={(e) => setFormData({ ...formData, price_cny: parseFloat(e.target.value) })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">价格 (USD)</label>
                    <input
                      type="number"
                      value={formData.price_usd}
                      onChange={(e) => setFormData({ ...formData, price_usd: parseFloat(e.target.value) })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                </div>
              </div>

              {/* Resource Quotas */}
              <div>
                <h3 className="font-medium mb-3 text-lg">资源配额</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">人物上限 (-1=无限)</label>
                    <input
                      type="number"
                      value={formData.features.max_persons}
                      onChange={(e) => updateFeature("max_persons", parseInt(e.target.value))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">成员上限 (-1=无限)</label>
                    <input
                      type="number"
                      value={formData.features.max_members}
                      onChange={(e) => updateFeature("max_members", parseInt(e.target.value))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">存储上限 MB (-1=无限)</label>
                    <input
                      type="number"
                      value={formData.features.max_storage_mb}
                      onChange={(e) => updateFeature("max_storage_mb", parseInt(e.target.value))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">管理员上限 (-1=无限)</label>
                    <input
                      type="number"
                      value={formData.features.max_admins}
                      onChange={(e) => updateFeature("max_admins", parseInt(e.target.value))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                </div>
              </div>

              {/* Feature Toggles */}
              <div>
                <h3 className="font-medium mb-3 text-lg">功能开关</h3>
                <div className="space-y-3">
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={formData.features.advanced_visualization}
                      onChange={(e) => updateFeature("advanced_visualization", e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">高级可视化</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={formData.features.data_export}
                      onChange={(e) => updateFeature("data_export", e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">数据导出</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={formData.features.api_access}
                      onChange={(e) => updateFeature("api_access", e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">API 访问</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={formData.features.custom_domain}
                      onChange={(e) => updateFeature("custom_domain", e.target.checked)}
                      className="w-4 h-4"
                    />
                    <span className="text-sm">自定义域名</span>
                  </label>
                  <div>
                    <label className="block text-sm font-medium mb-1">客服级别</label>
                    <select
                      value={formData.features.priority_support}
                      onChange={(e) => updateFeature("priority_support", e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    >
                      {PRIORITY_SUPPORT_OPTIONS.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
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
                onClick={() => setEditingPlan(null)}
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
