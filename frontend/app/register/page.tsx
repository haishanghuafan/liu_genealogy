"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { api } from "@/lib/api"

export default function RegisterPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  })
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }))
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    
    if (formData.password !== formData.confirmPassword) {
      setError("两次输入的密码不一致")
      return
    }
    
    if (formData.password.length < 8) {
      setError("密码长度不能少于8个字符")
      return
    }
    
    setLoading(true)
    
    try {
      await api.post("/auth/register", {
        email: formData.email,
        password: formData.password,
        full_name: formData.name,
      })
      
      router.push("/login?registered=true")
    } catch (err: any) {
      setError(err.response?.data?.detail || "注册失败，请稍后重试")
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <main className="min-h-screen flex bg-paper">
      {/* Left Side - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-2">
              <span className="text-3xl">📜</span>
              <span className="font-serif text-2xl font-bold text-vermillion">族谱云</span>
            </Link>
          </div>
          
          <div className="mb-8">
            <h2 className="text-2xl font-serif font-semibold mb-2 flex items-center gap-2">
              🌟 创建账号
            </h2>
            <p className="text-ink-muted">
              已有账号？{" "}
              <Link href="/login" className="text-vermillion hover:underline">
                立即登录
              </Link>
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="name" className="block text-sm font-medium flex items-center gap-2">
                <span>👤</span> 您的姓名
              </label>
              <input
                id="name"
                name="name"
                type="text"
                className="w-full px-4 py-3 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
                placeholder="请输入姓名"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium flex items-center gap-2">
                <span>📧</span> 邮箱地址
              </label>
              <input
                id="email"
                name="email"
                type="email"
                className="w-full px-4 py-3 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
                placeholder="your@email.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-medium flex items-center gap-2">
                <span>🔐</span> 设置密码
              </label>
              <input
                id="password"
                name="password"
                type="password"
                className="w-full px-4 py-3 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
                placeholder="至少8个字符"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="block text-sm font-medium flex items-center gap-2">
                <span>🔒</span> 确认密码
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                className="w-full px-4 py-3 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
                placeholder="再次输入密码"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>
            
            {error && (
              <div className="p-4 rounded-lg bg-vermillion/5 border border-vermillion/20 text-vermillion text-sm flex items-center gap-2">
                <span>⚠️</span> {error}
              </div>
            )}
            
            <button
              type="submit"
              className="w-full bg-vermillion text-white py-4 rounded-lg hover:bg-vermillion-dark transition-colors font-medium disabled:opacity-50 flex items-center justify-center gap-2"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="animate-spin">⏳</span> 创建中...
                </>
              ) : (
                <>
                  <span>🚀</span> 创建账号
                </>
              )}
            </button>
          </form>
          
          <div className="mt-8 text-center">
            <Link href="/" className="text-sm text-ink-muted hover:text-ink inline-flex items-center gap-1">
              <span>←</span> 返回首页
            </Link>
          </div>
        </div>
      </div>
      
      {/* Right Side */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-vermillion to-vermillion-dark text-white flex-col justify-center p-16 relative overflow-hidden">
        {/* Decorative */}
        <div className="absolute top-10 right-10 text-6xl opacity-20">🏠</div>
        <div className="absolute bottom-10 left-10 text-4xl opacity-20">👨‍👩‍👧‍👦</div>
        <div className="absolute top-1/2 right-20 text-3xl opacity-10">🌸</div>
        
        <div className="relative z-10">
          <h1 className="text-3xl font-serif font-semibold mb-6 flex items-center gap-3">
            <span>🏡</span> 开启家族传承
          </h1>
          <p className="text-white/80 mb-12">
            创建账号，为您的家族建立专属的数字族谱，<br/>
            让血脉传承，让记忆永存。
          </p>
          
          <div className="space-y-6">
            <Feature icon="🌳" text="可视化族谱树，直观展示家族脉络" />
            <Feature icon="✍️" text="多人协作，家族成员共同维护" />
            <Feature icon="📱" text="多端同步，随时随地查阅" />
            <Feature icon="🔒" text="隐私可控，数据安全有保障" />
          </div>
        </div>
      </div>
    </main>
  )
}

function Feature({ icon, text }: { icon: string; text: string }) {
  return (
    <div className="flex items-center gap-4">
      <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-xl flex-shrink-0">
        {icon}
      </div>
      <span className="text-white/90">{text}</span>
    </div>
  )
}