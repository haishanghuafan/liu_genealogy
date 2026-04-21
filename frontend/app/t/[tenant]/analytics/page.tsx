"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, TrendingUp, Users, Eye, Calendar } from "lucide-react"

interface SummaryStats {
  total_views: number
  unique_visitors: number
  person_views: number
  branch_views: number
  generation_views: number
  family_tree_views: number
  period_days: number
}

interface DailyStat {
  date: string
  total_views: number
  unique_visitors: number
}

export default function AnalyticsPage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<SummaryStats | null>(null)
  const [dailyStats, setDailyStats] = useState<DailyStat[]>([])
  
  useEffect(() => {
    // Track page visit
    trackPageVisit()
    fetchAnalytics()
  }, [tenantSlug])
  
  const trackPageVisit = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      await fetch(`http://localhost:8012/api/v1/t/${tenantSlug}/analytics/track`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          path: `/t/${tenantSlug}/analytics`,
          page_type: "analytics",
        }),
      })
    } catch (err) {
      // Silently fail - analytics should not break the page
      console.debug("Failed to track visit:", err)
    }
  }
  
  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const headers = { "Authorization": `Bearer ${token}` }
      
      const [summaryRes, dailyRes] = await Promise.all([
        fetch(`http://localhost:8012/api/v1/t/${tenantSlug}/analytics/summary?days=30`, { headers }),
        fetch(`http://localhost:8012/api/v1/t/${tenantSlug}/analytics/daily?days=30`, { headers }),
      ])
      
      const summaryData = await summaryRes.json()
      const dailyData = await dailyRes.json()
      
      if (summaryData.success) setSummary(summaryData.data)
      if (dailyData.success) setDailyStats(dailyData.data)
    } catch (err) {
      console.error("Failed to fetch analytics:", err)
    } finally {
      setLoading(false)
    }
  }
  
  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">加载中...</div>
      </main>
    )
  }
  
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href={`/t/${tenantSlug}`} className="flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              <span>返回</span>
            </Link>
            <h1 className="text-xl font-bold">📊 访问统计</h1>
          </div>
        </div>
      </nav>
      
      <div className="pt-20 px-4 max-w-7xl mx-auto">
        {/* Summary Cards */}
        {summary && (
          <>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">
                    总访问次数
                  </CardTitle>
                  <Eye className="h-4 w-4 text-gray-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{summary.total_views}</div>
                  <p className="text-xs text-gray-500 mt-1">
                    过去 {summary.period_days} 天
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">
                    独立访客
                  </CardTitle>
                  <Users className="h-4 w-4 text-gray-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{summary.unique_visitors}</div>
                  <p className="text-xs text-gray-500 mt-1">
                    过去 {summary.period_days} 天
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">
                    人物页面
                  </CardTitle>
                  <TrendingUp className="h-4 w-4 text-gray-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{summary.person_views}</div>
                  <p className="text-xs text-gray-500 mt-1">
                    访问次数
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-500">
                    家族树
                  </CardTitle>
                  <Calendar className="h-4 w-4 text-gray-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{summary.family_tree_views}</div>
                  <p className="text-xs text-gray-500 mt-1">
                    访问次数
                  </p>
                </CardContent>
              </Card>
            </div>
            
            {/* Page Type Breakdown */}
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>页面类型分布</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {summary.person_views}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">人物</div>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {summary.branch_views || 0}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">支系</div>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {summary.generation_views || 0}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">世代</div>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {summary.family_tree_views}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">家族树</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
        
        {/* Daily Stats Chart */}
        <Card>
          <CardHeader>
            <CardTitle>每日访问趋势</CardTitle>
          </CardHeader>
          <CardContent>
            {dailyStats.length > 0 ? (
              <div className="space-y-2">
                {dailyStats.slice(-14).map((stat, index) => (
                  <div key={index} className="flex items-center gap-4">
                    <div className="w-24 text-sm text-gray-600">
                      {new Date(stat.date).toLocaleDateString('zh-CN', {
                        month: 'short',
                        day: 'numeric'
                      })}
                    </div>
                    <div className="flex-1 h-8 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-blue-500 rounded-full transition-all duration-300"
                        style={{
                          width: `${Math.min(100, (stat.total_views / Math.max(...dailyStats.map(s => s.total_views))) * 100)}%`
                        }}
                      />
                    </div>
                    <div className="w-16 text-sm text-gray-600 text-right">
                      {stat.total_views} 次
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                暂无数据
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  )
}
