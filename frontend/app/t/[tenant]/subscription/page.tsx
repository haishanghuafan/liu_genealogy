"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter, useParams } from "next/navigation"
import { UserMenu } from "@/components/layout/UserMenu"

interface Plan {
  id: string
  name: string
  price: number
  price_display: string
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

interface CurrentSubscription {
  tenant_id: string
  current_plan: string
  plan_name: string
  subscription: {
    id: string
    plan: string
    started_at: string
    expires_at: string
    status: string
  } | null
}

export default function SubscriptionPage() {
  const router = useRouter()
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [plans, setPlans] = useState<Plan[]>([])
  const [current, setCurrent] = useState<CurrentSubscription | null>(null)
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  
  useEffect(() => {
    fetchData()
  }, [tenantSlug])
  
  const fetchData = async () => {
    try {
      // Fetch plans (public)
      const plansRes = await fetch("http://localhost:8000/api/v1/subscription/plans")
      const plansData = await plansRes.json()
      if (plansData.success) setPlans(plansData.data)
      
      // Fetch current subscription
      const currentRes = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/subscription/current`, {
        headers: { "Authorization": `Bearer ${localStorage.getItem("access_token") || ""}` }
      })
      const currentData = await currentRes.json()
      if (currentData.success) setCurrent(currentData.data)
    } catch (err) {
      setError("加载数据失败")
    } finally {
      setLoading(false)
    }
  }
  
  const handleUpgrade = async (planId: string) => {
    if (planId === current?.current_plan) return
    
    setUpgrading(true)
    setError("")
    setSuccess("")
    
    try {
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/subscription/upgrade`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token") || ""}`
        },
        body: JSON.stringify({ new_plan: planId })
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        fetchData()
      } else {
        setError(data.message || "升级失败")
      }
    } catch (err) {
      setError("网络错误")
    } finally {
      setUpgrading(false)
    }
  }
  
  const handleCancel = async () => {
    if (!confirm("确定要取消订阅吗？将降级为免费版")) return
    
    setUpgrading(true)
    try {
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/subscription/cancel`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${localStorage.getItem("access_token") || ""}` }
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        fetchData()
      } else {
        setError(data.message || "取消失败")
      }
    } catch (err) {
      setError("网络错误")
    } finally {
      setUpgrading(false)
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
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href={`/t/${tenantSlug}`} className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href={`/t/${tenantSlug}`} className="text-ink-muted hover:text-ink flex items-center gap-1">
              <span>←</span> 返回
            </Link>
            <div className="w-px h-6 bg-ink/10" />
            <UserMenu />
          </div>
        </div>
      </nav>
      
      <div className="pt-24 px-4 max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-serif font-semibold mb-4">💎 订阅管理</h1>
          <p className="text-ink-muted">选择适合您家族的套餐</p>
        </div>
        
        {/* Current Plan */}
        {current && (
          <div className="bg-white rounded-xl p-6 border border-ink/5 mb-10">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold mb-1">当前套餐</h2>
                <p className="text-2xl font-serif text-vermillion">{current.plan_name}</p>
                {current.subscription && (
                  <p className="text-sm text-ink-muted mt-1">
                    到期时间: {new Date(current.subscription.expires_at).toLocaleDateString("zh-CN")}
                  </p>
                )}
              </div>
              {current.current_plan !== "free" && (
                <button
                  onClick={handleCancel}
                  disabled={upgrading}
                  className="text-vermillion border border-vermillion px-4 py-2 rounded-lg hover:bg-vermillion/5 transition-colors"
                >
                  取消订阅
                </button>
              )}
            </div>
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
        
        {/* Plans Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => {
            const isCurrent = current?.current_plan === plan.id
            const features = plan.features
            
            return (
              <div
                key={plan.id}
                className={`bg-white rounded-xl border-2 p-6 transition-all ${
                  isCurrent 
                    ? "border-vermillion shadow-lg" 
                    : "border-ink/5 hover:border-vermillion/30 hover:shadow-md"
                }`}
              >
                {/* Plan Header */}
                <div className="text-center mb-6">
                  <h3 className="text-xl font-semibold mb-2">{plan.name}</h3>
                  <div className="text-3xl font-serif text-vermillion">
                    {plan.price === 0 ? "免费" : `¥${plan.price}`}
                  </div>
                  {plan.billing_period && (
                    <p className="text-sm text-ink-muted">/{plan.billing_period === "yearly" ? "年" : "月"}</p>
                  )}
                </div>
                
                {/* Features */}
                <ul className="space-y-3 mb-6 text-sm">
                  <li className="flex items-center gap-2">
                    <span className="text-vermillion">👤</span>
                    人物: {features.max_persons === -1 ? "无限" : features.max_persons}
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-vermillion">👥</span>
                    成员: {features.max_members === -1 ? "无限" : features.max_members}
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-vermillion">💾</span>
                    存储: {features.max_storage_mb === -1 ? "无限" : `${features.max_storage_mb}MB`}
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-vermillion">🔑</span>
                    管理员: {features.max_admins === -1 ? "无限" : features.max_admins}
                  </li>
                  <li className={`flex items-center gap-2 ${features.advanced_visualization ? "" : "text-ink-muted"}`}>
                    <span>{features.advanced_visualization ? "✅" : "❌"}</span>
                    高级可视化
                  </li>
                  <li className={`flex items-center gap-2 ${features.data_export ? "" : "text-ink-muted"}`}>
                    <span>{features.data_export ? "✅" : "❌"}</span>
                    数据导出
                  </li>
                  <li className={`flex items-center gap-2 ${features.api_access ? "" : "text-ink-muted"}`}>
                    <span>{features.api_access ? "✅" : "❌"}</span>
                    API 访问
                  </li>
                  <li className={`flex items-center gap-2 ${features.custom_domain ? "" : "text-ink-muted"}`}>
                    <span>{features.custom_domain ? "✅" : "❌"}</span>
                    自定义域名
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-vermillion">🎧</span>
                    客服: {features.priority_support === "community" ? "社区" : 
                          features.priority_support === "email" ? "邮件" :
                          features.priority_support === "priority" ? "优先" : "专属"}
                  </li>
                </ul>
                
                {/* Action Button */}
                <button
                  onClick={() => handleUpgrade(plan.id)}
                  disabled={isCurrent || upgrading || plan.id === "free"}
                  className={`w-full py-3 rounded-lg font-medium transition-colors ${
                    isCurrent
                      ? "bg-vermillion text-white cursor-default"
                      : plan.id === "free"
                      ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                      : "bg-vermillion text-white hover:bg-vermillion-dark"
                  }`}
                >
                  {isCurrent ? "当前套餐" : plan.id === "free" ? "免费版" : upgrading ? "处理中..." : "升级"}
                </button>
              </div>
            )
          })}
        </div>
        
        {/* Note */}
        <div className="mt-10 text-center text-sm text-ink-muted">
          <p>💡 升级后立即生效，费用按剩余时间比例计算</p>
          <p className="mt-2">如需发票或企业定制，请联系客服</p>
        </div>
      </div>
    </main>
  )
}