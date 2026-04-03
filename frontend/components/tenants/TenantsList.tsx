"use client"

import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Search, Users, ChevronRight } from "lucide-react"
import { api } from "@/lib/api"

interface Tenant {
  id: string
  name: string
  slug: string
  surname: string
  is_public: boolean
  plan: string
}

export function TenantsList() {
  const [search, setSearch] = useState("")
  
  const { data, isLoading } = useQuery({
    queryKey: ["tenants", search],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (search) params.append("surname", search)
      const response = await api.get(`/tenants?${params}`)
      return response.data
    },
  })
  
  const tenants = data?.data || []
  
  const filteredTenants = search
    ? tenants.filter((t: Tenant) =>
        t.surname.includes(search) || t.name.includes(search)
      )
    : tenants
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">家族列表</h1>
        <p className="text-gray-500">浏览已注册的家族族谱</p>
      </div>
      
      {/* Search */}
      <div className="max-w-md mx-auto">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="搜索姓氏..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>
      
      {/* Tenants Grid */}
      {isLoading ? (
        <div className="text-center py-12 text-gray-500">加载中...</div>
      ) : filteredTenants.length === 0 ? (
        <div className="text-center py-12">
          <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500">暂无家族数据</p>
          {search && (
            <p className="text-sm text-gray-400 mt-2">
              未找到姓氏为 "{search}" 的家族
            </p>
          )}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredTenants.map((tenant: Tenant) => (
            <Link key={tenant.id} href={`/t/${tenant.slug}/family-tree`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer group">
                <CardContent className="pt-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center">
                        <span className="text-xl font-bold text-primary-700">
                          {tenant.surname.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-semibold group-hover:text-primary-600 transition">
                          {tenant.name}
                        </h3>
                        <p className="text-sm text-gray-500">{tenant.surname}氏</p>
                      </div>
                    </div>
                    <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-primary-500 transition" />
                  </div>
                  
                  <div className="flex gap-2 mt-4">
                    {tenant.is_public ? (
                      <Badge variant="outline">公开</Badge>
                    ) : (
                      <Badge variant="secondary">私密</Badge>
                    )}
                    {tenant.plan !== "free" && (
                      <Badge>专业版</Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}