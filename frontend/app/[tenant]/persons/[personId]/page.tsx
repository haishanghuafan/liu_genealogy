"use client"

import { useQuery } from "@tanstack/react-query"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  ArrowLeft, 
  Calendar, 
  MapPin, 
  Users, 
  Edit,
  User,
  Heart,
} from "lucide-react"
import { api } from "@/lib/api"

export default function PersonDetailPage() {
  const params = useParams()
  const router = useRouter()
  const tenantSlug = params.tenant as string
  const personId = params.personId as string
  
  const { data, isLoading, error } = useQuery({
    queryKey: ["person", tenantSlug, personId],
    queryFn: async () => {
      const response = await api.get(`/t/${tenantSlug}/persons/${personId}`)
      return response.data
    },
  })
  
  const person = data?.data
  
  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">加载中...</div>
      </main>
    )
  }
  
  if (error || !person) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-red-500 mb-4">加载失败或人物不存在</p>
            <Button onClick={() => router.back()}>返回</Button>
          </CardContent>
        </Card>
      </main>
    )
  }
  
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回
          </Button>
          <div className="flex-1">
            <h1 className="text-xl font-bold">{person.name}</h1>
            {person.courtesy_name && (
              <span className="text-gray-500 text-sm">字{person.courtesy_name}</span>
            )}
          </div>
          <Link href={`/t/${tenantSlug}/admin/persons`}>
            <Button size="sm">
              <Edit className="h-4 w-4 mr-2" />
              编辑
            </Button>
          </Link>
        </div>
      </header>
      
      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Info Card */}
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-start gap-6">
                  {/* Avatar */}
                  <div className={`w-24 h-24 rounded-full flex items-center justify-center text-3xl font-bold text-white ${person.gender === "F" ? "bg-pink-500" : "bg-blue-500"}`}>
                    {person.name.charAt(0)}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-2xl font-bold">{person.name}</h2>
                      <Badge variant={person.gender === "F" ? "destructive" : "default"}>
                        {person.gender === "F" ? "女" : "男"}
                      </Badge>
                      {person.generation_id && (
                        <Badge variant="outline">第{person.generation_id}世</Badge>
                      )}
                    </div>
                    
                    {person.full_name && (
                      <p className="text-gray-500 mb-4">{person.full_name}</p>
                    )}
                    
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      {person.birth_year && (
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          <span>{person.birth_year}年</span>
                          {person.death_year && <span>- {person.death_year}年</span>}
                        </div>
                      )}
                      {person.birth_place && (
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          <span>{person.birth_place}</span>
                        </div>
                      )}
                      {person.branch_name && (
                        <div className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          <span>{person.branch_names}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Biography */}
            {person.biography && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">生平简介</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                    {person.biography}
                  </p>
                </CardContent>
              </Card>
            )}
            
            {/* Achievements */}
            {person.achievements && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">主要事迹</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                    {person.achievements}
                  </p>
                </CardContent>
              </Card>
            )}
            
            {/* Burial Info */}
            {(person.burial_place || person.burial_fengshui || person.burial_direction) && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">墓葬信息</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  {person.burial_place && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">葬地</span>
                      <span>{person.burial_place}</span>
                    </div>
                  )}
                  {person.burial_fengshui && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">墓形/风水</span>
                      <span>{person.burial_fengshui}</span>
                    </div>
                  )}
                  {person.burial_direction && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">坐向</span>
                      <span>{person.burial_direction}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
          
          {/* Sidebar */}
          <div className="space-y-6">
            {/* Family Relations */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  家庭关系
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Father */}
                {person.father_id && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">父亲</span>
                    <Link 
                      href={`/t/${tenantSlug}/persons/${person.father_id}`}
                      className="text-primary-600 hover:underline"
                    >
                      {person.father_name || "查看详情"}
                    </Link>
                  </div>
                )}
                
                {/* Mother */}
                {person.mother_id && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">母亲</span>
                    <Link 
                      href={`/t/${tenantSlug}/persons/${person.mother_id}`}
                      className="text-primary-600 hover:underline"
                    >
                      {person.mother_name || "查看详情"}
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>
            
            {/* Actions */}
            <Card>
              <CardContent className="pt-6 space-y-2">
                <Link href={`/t/${tenantSlug}/family-tree?root=${person.id}`} className="block">
                  <Button variant="outline" className="w-full justify-start">
                    <Users className="h-4 w-4 mr-2" />
                    查看族谱树
                  </Button>
                </Link>
              </CardContent>
            </Card>
            
            {/* Notes */}
            {person.notes && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">备注</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                    {person.notes}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}