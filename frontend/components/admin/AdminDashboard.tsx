"use client"

import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, TreeDeciduous, Calendar, TrendingUp } from "lucide-react"
import { api } from "@/lib/api"

interface DashboardProps {
  tenantSlug: string
}

export function AdminDashboard({ tenantSlug }: DashboardProps) {
  // Fetch statistics
  const { data: stats } = useQuery({
    queryKey: ["stats", tenantSlug],
    queryFn: async () => {
      const [personsRes, treeRes] = await Promise.all([
        api.get(`/t/${tenantSlug}/persons?page_size=1`),
        api.get(`/t/${tenantSlug}/family-tree/statistics`),
      ])
      return {
        totalPersons: personsRes.data.meta?.total || 0,
        treeStats: treeRes.data.data,
      }
    },
  })
  
  const statCards = [
    {
      title: "总人物数",
      value: stats?.totalPersons || 0,
      icon: Users,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      title: "世代数",
      value: stats?.treeStats?.max_generation || 0,
      icon: TreeDeciduous,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      title: "最早记载",
      value: stats?.treeStats?.generations?.[0]?.generation
        ? `第${stats.treeStats.generations[0].generation}世`
        : "-",
      icon: Calendar,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
    },
    {
      title: "最新世代",
      value: stats?.treeStats?.max_generation
        ? `第${stats.treeStats.max_generation}世`
        : "-",
      icon: TrendingUp,
      color: "text-orange-600",
      bgColor: "bg-orange-50",
    },
  ]
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">管理概览</h1>
        <p className="text-gray-500 mt-1">家族数据统计与快捷操作</p>
      </div>
      
      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <Card key={stat.title}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-4">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-sm text-gray-500">{stat.title}</p>
                  <p className="text-2xl font-bold">{stat.value}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* Generation Chart */}
      {stats?.treeStats?.generations && stats.treeStats.generations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>各代人数分布</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stats.treeStats.generations.map((gen: any) => (
                <div key={gen.generation} className="flex items-center gap-4">
                  <div className="w-20 text-sm text-gray-500">
                    第{gen.generation}世
                  </div>
                  <div className="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full transition-all"
                      style={{
                        width: `${Math.min(
                          (gen.count / Math.max(...stats.treeStats.generations.map((g: any) => g.count))) * 100,
                          100
                        )}%`,
                      }}
                    />
                  </div>
                  <div className="w-12 text-sm font-medium text-right">
                    {gen.count}人
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">快捷操作</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <a
              href={`/t/${tenantSlug}/admin/persons`}
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition"
            >
              <Users className="h-5 w-5 text-gray-400" />
              <div>
                <p className="font-medium">管理人物</p>
                <p className="text-sm text-gray-500">添加、编辑、删除人物信息</p>
              </div>
            </a>
            <a
              href={`/t/${tenantSlug}/family-tree`}
              className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition"
            >
              <TreeDeciduous className="h-5 w-5 text-gray-400" />
              <div>
                <p className="font-medium">查看族谱树</p>
                <p className="text-sm text-gray-500">可视化展示家族关系</p>
              </div>
            </a>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">最近活动</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2 text-gray-500">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
                <span>系统已就绪</span>
              </div>
              <p className="text-gray-400">
                开始录入家族成员信息，构建您的数字族谱。
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}