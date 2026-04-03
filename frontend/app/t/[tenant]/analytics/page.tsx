"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"

interface TrendPoint {
  date: string
  visits: number
  unique_visitors: number
  unique_ips: number
}

interface TopPage {
  path: string
  total_visits: number
  unique_visitors: number
  last_visit: string
}

interface RealtimeStats {
  visits_last_hour: number
  unique_visitors_last_hour: number
  active_users: number
  timestamp: string
}

export default function AnalyticsPage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [stats, setStats] = useState<any>(null)
  const [trends, setTrends] = useState<TrendPoint[]>([])
  const [topPages, setTopPages] = useState<TopPage[]>([])
  const [realtime, setRealtime] = useState<RealtimeStats | null>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchData()
    
    // Refresh realtime stats every 30 seconds
    const interval = setInterval(fetchRealtime, 30000)
    return () => clearInterval(interval)
  }, [tenantSlug])
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const headers = { "Authorization": `Bearer ${token}` }
      
      const [dashboardRes] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/analytics/dashboard`, { headers })
      ])
      
      if (dashboardRes.ok) {
        const data = await dashboardRes.json()
        setStats(data.data?.stats)
        setTrends(data.data?.trends || [])
        setTopPages(data.data?.top_pages || [])
      }
    } catch (err) {
      console.error("Failed to fetch analytics:", err)
    } finally {
      setLoading(false)
    }
  }
  
  const fetchRealtime = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/analytics/realtime`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      
      if (res.ok) {
        const data = await res.json()
        setRealtime(data.data)
      }
    } catch (err) {
      console.error("Failed to fetch realtime:", err)
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
          <Link href={`/t/${tenantSlug}`} className="text-ink-muted hover:text-ink flex items-center gap-1">
            <span>←</span> 返回
          </Link>
        </div>
      </nav>
      
      <div className="pt-24 px-4 max-w-6xl mx-auto">
        <h1 className="text-3xl font-serif font-semibold mb-8">📊 访问统计</h1>
        
        {/* Realtime Stats */}
        {realtime && (
          <div className="bg-gradient-to-r from-vermillion/10 to-vermillion/5 rounded-xl p-6 mb-8">
            <h2 className="font-semibold mb-4 flex items-center gap-2">
              <span className="animate-pulse">🔴</span> 实时数据
            </h2>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-3xl font-serif font-semibold text-vermillion">
                  {realtime.visits_last_hour}
                </div>
                <div className="text-sm text-ink-muted">最近1小时访问</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-serif font-semibold">
                  {realtime.unique_visitors_last_hour}
                </div>
                <div className="text-sm text-ink-muted">独立访客</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-serif font-semibold text-green-600">
                  {realtime.active_users}
                </div>
                <div className="text-sm text-ink-muted">活跃用户</div>
              </div>
            </div>
          </div>
        )}
        
        {/* Summary Stats */}
        {stats && (
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard title="👥 总人物" value={stats.persons?.total || 0} />
            <StatCard title="👨‍👩‍👧‍👦 成员" value={stats.members?.total || 0} />
            <StatCard title="📁 图片" value={stats.media?.images || 0} />
            <StatCard title="👁️ 今日访问" value={stats.visits?.today || 0} highlight />
          </div>
        )}
        
        {/* Visit Trends Chart */}
        <div className="bg-white rounded-xl border border-ink/5 p-6 mb-8">
          <h2 className="font-semibold mb-4">📈 访问趋势（最近30天）</h2>
          
          {trends.length > 0 ? (
            <div className="h-48 flex items-end gap-1">
              {trends.slice(-30).map((t, i) => (
                <div
                  key={t.date}
                  className="flex-1 bg-vermillion/20 hover:bg-vermillion/40 rounded-t transition-colors cursor-pointer relative group"
                  style={{ height: `${Math.min(100, (t.visits / Math.max(...trends.map(x => x.visits))) * 100)}%` }}
                  title={`${t.date}: ${t.visits} 次访问`}
                >
                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 px-2 py-1 bg-ink text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                    {t.date}: {t.visits} 次访问
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-ink-muted">暂无访问数据</div>
          )}
        </div>
        
        {/* Top Pages */}
        <div className="bg-white rounded-xl border border-ink/5 p-6">
          <h2 className="font-semibold mb-4">🔥 热门页面</h2>
          
          {topPages.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-ink/10">
                  <th className="text-left py-2">路径</th>
                  <th className="text-right py-2">访问量</th>
                  <th className="text-right py-2">独立访客</th>
                  <th className="text-right py-2">最后访问</th>
                </tr>
              </thead>
              <tbody>
                {topPages.map((p, i) => (
                  <tr key={p.path} className="border-b border-ink/5">
                    <td className="py-3">
                      <span className="text-vermillion font-medium mr-2">#{i + 1}</span>
                      {p.path}
                    </td>
                    <td className="text-right font-medium">{p.total_visits}</td>
                    <td className="text-right text-ink-muted">{p.unique_visitors}</td>
                    <td className="text-right text-ink-muted text-xs">
                      {new Date(p.last_visit).toLocaleDateString("zh-CN")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="text-center py-12 text-ink-muted">暂无页面访问数据</div>
          )}
        </div>
      </div>
    </main>
  )
}

function StatCard({ title, value, highlight = false }: { title: string; value: number; highlight?: boolean }) {
  return (
    <div className={`bg-white rounded-xl p-6 border ${highlight ? "border-vermillion/20" : "border-ink/5"}`}>
      <div className="text-sm text-ink-muted mb-1">{title}</div>
      <div className={`text-3xl font-serif font-semibold ${highlight ? "text-vermillion" : ""}`}>
        {value.toLocaleString()}
      </div>
    </div>
  )
}