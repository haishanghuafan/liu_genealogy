"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Eye, EyeOff } from "lucide-react"
import { api } from "@/lib/api"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    
    try {
      const data = await api.post("/auth/login", { email, password })
      const { access_token, refresh_token } = data
      
      localStorage.setItem("access_token", access_token)
      localStorage.setItem("refresh_token", refresh_token)
      
      router.push("/dashboard")
    } catch (err: any) {
      setError(err.message || "登录失败，请检查邮箱和密码")
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <main className="min-h-screen flex bg-paper">
      {/* Left Side */}
      <div className="hidden lg:flex lg:w-1/2 bg-ink text-white flex-col justify-center p-16 relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-10 right-10 text-6xl opacity-10">📜</div>
        <div className="absolute bottom-10 left-10 text-4xl opacity-10">🌳</div>
        
        <div className="relative z-10">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-vermillion text-3xl font-serif font-bold mb-6 border-2 border-white/20">
              谱
            </div>
            <h1 className="text-3xl font-serif font-semibold mb-4 flex items-center gap-3">
              <span>👋</span> 欢迎回来
            </h1>
            <p className="text-white/60">登录以继续管理您的家族族谱</p>
          </div>
          
          <blockquote className="mt-12 pt-12 border-t border-white/10">
            <p className="text-xl font-serif text-white/80 italic">
              "家之有谱，犹国之有史。"
            </p>
            <cite className="text-white/40 text-sm mt-2 block">— 梁启超</cite>
          </blockquote>
        </div>
      </div>
      
      {/* Right Side */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Logo (mobile) */}
          <div className="lg:hidden text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-2">
              <span className="text-3xl">📜</span>
              <span className="font-serif text-2xl font-bold text-vermillion">族谱云</span>
            </Link>
          </div>
          
          <div className="mb-8">
            <h2 className="text-2xl font-serif font-semibold mb-2">🔑 登录账号</h2>
            <p className="text-ink-muted">
              还没有账号？{" "}
              <Link href="/register" className="text-vermillion hover:underline">
                立即注册
              </Link>
            </p>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium flex items-center gap-2">
                <span>📧</span> 邮箱地址
              </label>
              <input
                id="email"
                type="email"
                className="w-full px-4 py-3 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-sm font-medium flex items-center gap-2">
                  <span>🔐</span> 密码
                </label>
                <Link href="/forgot-password" className="text-sm text-ink-muted hover:text-ink">
                  忘记密码？
                </Link>
              </div>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  className="w-full px-4 py-3 pr-12 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none transition-all"
                  placeholder="输入密码"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted hover:text-ink transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
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
                  <span className="animate-spin">⏳</span> 登录中...
                </>
              ) : (
                <>
                  <span>🚀</span> 登录
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
    </main>
  )
}