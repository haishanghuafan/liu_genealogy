"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import {
  Dialog, DialogContent, DialogHeader, DialogTitle,
} from "@/components/ui/dialog"
import { Search, Plus, Edit, Trash2, Users, RefreshCw, Upload, User, ArrowLeft } from "lucide-react"
import { api } from "@/lib/api"

interface Person {
  id: string
  name: string
  courtesy_name?: string
  art_name?: string
  generation_number?: number
  gender: string
  birth_year?: number
  death_year?: number
  branch_name?: string
  father_name?: string
}

interface PageMeta {
  total: number
  page: number
  page_size: number
  total_pages: number
}

export default function PersonsPage() {
  const params = useParams()
  const router = useRouter()
  const tenantSlug = params.tenant as string

  const [persons, setPersons] = useState<Person[]>([])
  const [meta, setMeta] = useState<PageMeta | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [generationFilter, setGenerationFilter] = useState<string>("")
  const [genderFilter, setGenderFilter] = useState<string>("")

  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingPerson, setEditingPerson] = useState<Person | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    courtesy_name: "",
    art_name: "",
    gender: "M",
    generation_number: undefined as number | undefined,
    birth_year: undefined as number | undefined,
    death_year: undefined as number | undefined,
  })
  const [formError, setFormError] = useState("")
  const [formSuccess, setFormSuccess] = useState("")

  useEffect(() => {
    fetchPersons()
  }, [tenantSlug, page, search, generationFilter, genderFilter])

  const fetchPersons = async () => {
    setLoading(true)
    try {
      const queryParams = new URLSearchParams({
        page: String(page),
        page_size: "20",
      })
      if (search) queryParams.append("search", search)
      if (generationFilter) queryParams.append("generation", generationFilter)
      if (genderFilter) queryParams.append("gender", genderFilter)

      const response = await api.get(`/t/${tenantSlug}/persons?${queryParams}`)
      if (response.success) {
        setPersons(response.data)
        setMeta(response.meta)
      }
    } catch (err) {
      console.error("Failed to fetch persons:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError("")
    setFormSuccess("")

    try {
      const response = await api.post(`/t/${tenantSlug}/persons`, formData)
      if (response.success) {
        setFormSuccess("人物创建成功")
        setShowCreateModal(false)
        resetForm()
        fetchPersons()
      } else {
        setFormError(response.message || "创建失败")
      }
    } catch (err: any) {
      setFormError(err.message || "网络错误")
    }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingPerson) return

    setFormError("")
    setFormSuccess("")

    try {
      const response = await api.put(`/t/${tenantSlug}/persons/${editingPerson.id}`, formData)
      if (response.success) {
        setFormSuccess("人物更新成功")
        setEditingPerson(null)
        resetForm()
        fetchPersons()
      } else {
        setFormError(response.message || "更新失败")
      }
    } catch (err: any) {
      setFormError(err.message || "网络错误")
    }
  }

  const handleDelete = async (person: Person) => {
    if (!confirm(`确定要删除 "${person.name}" 吗？此操作不可撤销。`)) {
      return
    }

    try {
      const response = await api.delete(`/t/${tenantSlug}/persons/${person.id}`)
      if (response.success) {
        fetchPersons()
      } else {
        alert(response.message || "删除失败")
      }
    } catch (err: any) {
      alert(err.message || "删除失败")
    }
  }

  const openEditModal = (person: Person) => {
    setEditingPerson(person)
    setFormData({
      name: person.name,
      courtesy_name: person.courtesy_name || "",
      art_name: person.art_name || "",
      gender: person.gender,
      generation_number: person.generation_number,
      birth_year: person.birth_year,
      death_year: person.death_year,
    })
    setShowCreateModal(true)
  }

  const resetForm = () => {
    setFormData({
      name: "",
      courtesy_name: "",
      art_name: "",
      gender: "M",
      generation_number: undefined,
      birth_year: undefined,
      death_year: undefined,
    })
    setFormError("")
    setFormSuccess("")
  }

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.push(`/t/${tenantSlug}`)}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回
          </Button>
          <h1 className="text-xl font-bold">👥 人物列表</h1>
          <div className="flex-1" />
          <Button variant="outline" size="sm" onClick={() => router.push(`/t/${tenantSlug}/import`)}>
            <Upload className="h-4 w-4 mr-2" />
            批量导入
          </Button>
        </div>
      </nav>

      <div className="pt-20 px-4 max-w-7xl mx-auto">
        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="pt-4">
            <div className="flex gap-4 flex-wrap">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="搜索姓名、字、号..."
                  value={search}
                  onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                  className="pl-10"
                />
              </div>

              <Select value={generationFilter} onValueChange={(v) => { setGenerationFilter(v); setPage(1); }}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="世代" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">全部世代</SelectItem>
                  <SelectItem value="1">第1世</SelectItem>
                  <SelectItem value="2">第2世</SelectItem>
                  <SelectItem value="3">第3世</SelectItem>
                </SelectContent>
              </Select>

              <Select value={genderFilter} onValueChange={(v) => { setGenderFilter(v); setPage(1); }}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="性别" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">全部</SelectItem>
                  <SelectItem value="M">男</SelectItem>
                  <SelectItem value="F">女</SelectItem>
                </SelectContent>
              </Select>

              <Button variant="outline" size="sm" onClick={() => fetchPersons()}>
                <RefreshCw className="h-4 w-4 mr-2" />
                刷新
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              共 {meta?.total || 0} 条记录
            </CardTitle>
            <Button onClick={() => { resetForm(); setEditingPerson(null); setShowCreateModal(true); }}>
              <Plus className="h-4 w-4 mr-2" />
              添加人物
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="p-8 text-center text-gray-500">⏳ 加载中...</div>
            ) : persons.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>暂无数据</p>
                <Button className="mt-4" onClick={() => setShowCreateModal(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  添加第一个人物
                </Button>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>姓名</TableHead>
                    <TableHead>性别</TableHead>
                    <TableHead>世代</TableHead>
                    <TableHead>字号</TableHead>
                    <TableHead>生卒年</TableHead>
                    <TableHead>支系</TableHead>
                    <TableHead>操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {persons.map((person) => (
                    <TableRow key={person.id}>
                      <TableCell>
                        <Link
                          href={`/t/${tenantSlug}/persons/${person.id}`}
                          className="font-medium hover:text-blue-600 hover:underline"
                        >
                          {person.name}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Badge variant={person.gender === "F" ? "destructive" : "default"}>
                          {person.gender === "F" ? "女" : "男"}
                        </Badge>
                      </TableCell>
                      <TableCell>{person.generation_number ? `第${person.generation_number}世` : "-"}</TableCell>
                      <TableCell>
                        {person.courtesy_name ? `字${person.courtesy_name}` : ""}
                        {person.art_name ? `号${person.art_name}` : ""}
                        {!person.courtesy_name && !person.art_name && "-"}
                      </TableCell>
                      <TableCell>
                        {person.birth_year || "?"}
                        {person.death_year ? ` - ${person.death_year}` : ""}
                      </TableCell>
                      <TableCell>{person.branch_name || "-"}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openEditModal(person)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(person)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {/* Pagination */}
            {meta && meta.total_pages > 1 && (
              <div className="flex items-center justify-between p-4 border-t">
                <div className="text-sm text-gray-500">
                  第 {meta.page} / {meta.total_pages} 页，共 {meta.total} 条
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    disabled={page <= 1}
                  >
                    上一页
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={page >= meta.total_pages}
                  >
                    下一页
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Create/Edit Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingPerson ? "编辑人物" : "添加人物"}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={editingPerson ? handleUpdate : handleCreate} className="space-y-4">
            {formError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {formError}
              </div>
            )}
            {formSuccess && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
                {formSuccess}
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">姓名 *</label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  placeholder="输入姓名"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">性别 *</label>
                <Select value={formData.gender} onValueChange={(v) => setFormData({ ...formData, gender: v })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="M">男</SelectItem>
                    <SelectItem value="F">女</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">字</label>
                <Input
                  value={formData.courtesy_name}
                  onChange={(e) => setFormData({ ...formData, courtesy_name: e.target.value })}
                  placeholder="字号（字）"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">号</label>
                <Input
                  value={formData.art_name}
                  onChange={(e) => setFormData({ ...formData, art_name: e.target.value })}
                  placeholder="号"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">世代</label>
                <Input
                  type="number"
                  value={formData.generation_number || ""}
                  onChange={(e) => setFormData({ ...formData, generation_number: e.target.value ? Number(e.target.value) : undefined })}
                  placeholder="世代数字"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">出生年</label>
                <Input
                  type="number"
                  value={formData.birth_year || ""}
                  onChange={(e) => setFormData({ ...formData, birth_year: e.target.value ? Number(e.target.value) : undefined })}
                  placeholder="如：1980"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">逝世年</label>
              <Input
                type="number"
                value={formData.death_year || ""}
                onChange={(e) => setFormData({ ...formData, death_year: e.target.value ? Number(e.target.value) : undefined })}
                placeholder="如：2050"
              />
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowCreateModal(false)}>
                取消
              </Button>
              <Button type="submit">
                {editingPerson ? "保存" : "创建"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </main>
  )
}