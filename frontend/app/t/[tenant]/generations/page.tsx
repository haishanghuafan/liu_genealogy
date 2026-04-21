"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { 
  Users, 
  Plus, 
  Search, 
  Edit, 
  Trash2,
  TrendingUp,
} from "lucide-react"

interface Generation {
  id: number
  number: number
  is_spouse: boolean
  name: string | null
  description: string | null
  person_count: number
  title: string
}

export default function GenerationsPage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [generations, setGenerations] = useState<Generation[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingGeneration, setEditingGeneration] = useState<Generation | null>(null)
  
  // Form state
  const [formData, setFormData] = useState({
    number: "",
    is_spouse: false,
    name: "",
    description: "",
  })
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  
  useEffect(() => {
    trackPageVisit()
    fetchGenerations()
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
          path: `/t/${tenantSlug}/generations`,
          page_type: "generation",
        }),
      })
    } catch (err) {
      console.debug("Failed to track visit:", err)
    }
  }
  
  const fetchGenerations = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/generations`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) setGenerations(data.data)
    } catch (err) {
      console.error("Failed to fetch generations:", err)
    } finally {
      setLoading(false)
    }
  }
  
  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/generations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          number: parseInt(formData.number),
        })
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess("世代创建成功")
        setShowCreateModal(false)
        resetForm()
        fetchGenerations()
      } else {
        setError(data.message || "创建失败")
      }
    } catch (err) {
      setError("网络错误")
    }
  }
  
  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccess("")
    
    if (!editingGeneration) return
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/generations/${editingGeneration.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          number: formData.number ? parseInt(formData.number) : undefined,
        })
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess("世代更新成功")
        setEditingGeneration(null)
        resetForm()
        fetchGenerations()
      } else {
        setError(data.message || "更新失败")
      }
    } catch (err) {
      setError("网络错误")
    }
  }
  
  const handleDelete = async (generationId: number) => {
    if (!confirm("确定要删除该世代吗？")) return
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/generations/${generationId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess("世代删除成功")
        fetchGenerations()
      } else {
        setError(data.message || "删除失败")
      }
    } catch (err) {
      setError("网络错误")
    }
  }
  
  const resetForm = () => {
    setFormData({
      number: "",
      is_spouse: false,
      name: "",
      description: "",
    })
    setError("")
    setSuccess("")
  }
  
  const openEditModal = (gen: Generation) => {
    setEditingGeneration(gen)
    setFormData({
      number: gen.number.toString(),
      is_spouse: gen.is_spouse,
      name: gen.name || "",
      description: gen.description || "",
    })
  }
  
  const filteredGenerations = generations.filter(g => 
    search === "" || 
    g.number.toString().includes(search) ||
    g.title.includes(search) ||
    (g.name && g.name.toLowerCase().includes(search.toLowerCase()))
  )
  
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href={`/t/${tenantSlug}`} className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold">族谱云</span>
          </Link>
          <Link href={`/t/${tenantSlug}`} className="text-gray-500 hover:text-gray-700">
            ← 返回
          </Link>
        </div>
      </nav>
      
      <div className="pt-20 px-4 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">🌳 世代管理</h1>
            <p className="text-gray-500">管理族谱的世代层次</p>
          </div>
          <Button 
            onClick={() => {
              resetForm()
              setEditingGeneration(null)
              setShowCreateModal(true)
            }}
            className="bg-green-600 hover:bg-green-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            添加世代
          </Button>
        </div>
        
        {/* Search */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="搜索世代编号或称谓..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        
        {/* Messages */}
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            {success}
          </div>
        )}
        
        {/* Generations List */}
        {loading ? (
          <div className="text-center py-20">
            <div className="text-gray-400">加载中...</div>
          </div>
        ) : filteredGenerations.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center py-20">
              <TrendingUp className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500 mb-4">
                {search ? "没有找到匹配的世代" : "暂无世代记录"}
              </p>
              {!search && (
                <Button
                  onClick={() => {
                    resetForm()
                    setEditingGeneration(null)
                    setShowCreateModal(true)
                  }}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  创建第一个世代
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredGenerations.map((gen) => (
              <Card key={gen.id} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className={`w-16 h-16 rounded-lg flex items-center justify-center text-xl font-bold ${
                        gen.is_spouse 
                          ? "bg-pink-100 text-pink-600" 
                          : "bg-green-100 text-green-600"
                      }`}>
                        {gen.number}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="text-lg font-semibold">{gen.title}</h3>
                          {gen.is_spouse && (
                            <Badge variant="secondary">配偶</Badge>
                          )}
                        </div>
                        {gen.name && (
                          <p className="text-gray-600 text-sm">{gen.name}</p>
                        )}
                        {gen.description && (
                          <p className="text-gray-500 text-sm line-clamp-1">
                            {gen.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className="text-2xl font-bold text-gray-700">
                          {gen.person_count}
                        </div>
                        <div className="text-sm text-gray-500">人</div>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openEditModal(gen)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(gen.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
      
      {/* Create/Edit Modal */}
      {(showCreateModal || editingGeneration) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>
                {editingGeneration ? "编辑世代" : "添加世代"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={editingGeneration ? handleUpdate : handleCreate}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      世代编号 *
                    </label>
                    <Input
                      type="number"
                      min="1"
                      max="100"
                      value={formData.number}
                      onChange={(e) => setFormData({...formData, number: e.target.value})}
                      required
                      placeholder="例如：1"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="is_spouse"
                      checked={formData.is_spouse}
                      onChange={(e) => setFormData({...formData, is_spouse: e.target.checked})}
                      className="w-4 h-4"
                    />
                    <label htmlFor="is_spouse" className="text-sm">
                      配偶世代（用于记录多位配偶）
                    </label>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      世代名称
                    </label>
                    <Input
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      placeholder="例如：文德公系"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      描述
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="w-full px-3 py-2 border rounded-lg"
                      rows={3}
                      placeholder="世代简介..."
                    />
                  </div>
                  <div className="flex gap-2 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowCreateModal(false)
                        setEditingGeneration(null)
                        resetForm()
                      }}
                      className="flex-1"
                    >
                      取消
                    </Button>
                    <Button
                      type="submit"
                      className="flex-1 bg-green-600 hover:bg-green-700"
                    >
                      {editingGeneration ? "更新" : "创建"}
                    </Button>
                  </div>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
    </main>
  )
}
