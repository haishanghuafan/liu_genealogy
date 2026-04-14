"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
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
  MapPin,
  User,
} from "lucide-react"

interface Branch {
  id: string
  name: string
  founder_id: string | null
  founder_name: string | null
  description: string | null
  location: string | null
  member_count: number
}

export default function BranchesPage() {
  const params = useParams()
  const router = useRouter()
  const tenantSlug = params.tenant as string
  
  const [branches, setBranches] = useState<Branch[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingBranch, setEditingBranch] = useState<Branch | null>(null)
  
  // Form state
  const [formData, setFormData] = useState({
    name: "",
    founder_id: "",
    description: "",
    location: "",
  })
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  
  useEffect(() => {
    fetchBranches()
  }, [tenantSlug])
  
  const fetchBranches = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/branches`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const data = await res.json()
      if (data.success) setBranches(data.data)
    } catch (err) {
      console.error("Failed to fetch branches:", err)
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
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/branches`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess("支系创建成功")
        setShowCreateModal(false)
        resetForm()
        fetchBranches()
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
    
    if (!editingBranch) return
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/branches/${editingBranch.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess("支系更新成功")
        setEditingBranch(null)
        resetForm()
        fetchBranches()
      } else {
        setError(data.message || "更新失败")
      }
    } catch (err) {
      setError("网络错误")
    }
  }
  
  const handleDelete = async (branchId: string) => {
    if (!confirm("确定要删除该支系吗？")) return
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/branches/${branchId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess("支系删除成功")
        fetchBranches()
      } else {
        setError(data.message || "删除失败")
      }
    } catch (err) {
      setError("网络错误")
    }
  }
  
  const resetForm = () => {
    setFormData({
      name: "",
      founder_id: "",
      description: "",
      location: "",
    })
    setError("")
    setSuccess("")
  }
  
  const openEditModal = (branch: Branch) => {
    setEditingBranch(branch)
    setFormData({
      name: branch.name,
      founder_id: branch.founder_id || "",
      description: branch.description || "",
      location: branch.location || "",
    })
  }
  
  const filteredBranches = branches.filter(b => 
    search === "" || 
    b.name.toLowerCase().includes(search.toLowerCase()) ||
    (b.location && b.location.toLowerCase().includes(search.toLowerCase()))
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
            <h1 className="text-3xl font-bold mb-2">🏛️ 支系管理</h1>
            <p className="text-gray-500">管理家族的不同支系和分支</p>
          </div>
          <Button 
            onClick={() => {
              resetForm()
              setEditingBranch(null)
              setShowCreateModal(true)
            }}
            className="bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            创建支系
          </Button>
        </div>
        
        {/* Search */}
        <div className="mb-6">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="搜索支系名称或地区..."
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
        
        {/* Branch List */}
        {loading ? (
          <div className="text-center py-20">
            <div className="text-gray-400">加载中...</div>
          </div>
        ) : filteredBranches.length === 0 ? (
          <Card>
            <CardContent className="pt-6 text-center py-20">
              <Users className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500 mb-4">
                {search ? "没有找到匹配的支系" : "暂无支系记录"}
              </p>
              {!search && (
                <Button
                  onClick={() => {
                    resetForm()
                    setEditingBranch(null)
                    setShowCreateModal(true)
                  }}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  创建第一个支系
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredBranches.map((branch) => (
              <Card key={branch.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-start justify-between">
                    <span className="text-lg">{branch.name}</span>
                    <Badge variant="secondary">{branch.member_count} 人</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {branch.founder_name && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <User className="h-4 w-4" />
                      <span>开基祖：{branch.founder_name}</span>
                    </div>
                  )}
                  {branch.location && (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <MapPin className="h-4 w-4" />
                      <span>{branch.location}</span>
                    </div>
                  )}
                  {branch.description && (
                    <p className="text-sm text-gray-600 line-clamp-2">
                      {branch.description}
                    </p>
                  )}
                  <div className="flex gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/t/${tenantSlug}/branches/${branch.id}`)}
                    >
                      详情
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => openEditModal(branch)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(branch.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
      
      {/* Create/Edit Modal */}
      {(showCreateModal || editingBranch) && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>
                {editingBranch ? "编辑支系" : "创建支系"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={editingBranch ? handleUpdate : handleCreate}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      支系名称 *
                    </label>
                    <Input
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      required
                      placeholder="例如：福建支系"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      开基祖 ID
                    </label>
                    <Input
                      value={formData.founder_id}
                      onChange={(e) => setFormData({...formData, founder_id: e.target.value})}
                      placeholder="人物 UUID"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      分布地区
                    </label>
                    <Input
                      value={formData.location}
                      onChange={(e) => setFormData({...formData, location: e.target.value})}
                      placeholder="例如：福建福州"
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
                      placeholder="支系简介..."
                    />
                  </div>
                  <div className="flex gap-2 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowCreateModal(false)
                        setEditingBranch(null)
                        resetForm()
                      }}
                      className="flex-1"
                    >
                      取消
                    </Button>
                    <Button
                      type="submit"
                      className="flex-1 bg-blue-600 hover:bg-blue-700"
                    >
                      {editingBranch ? "更新" : "创建"}
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
