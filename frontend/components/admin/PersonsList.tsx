"use client"

import { useState, useEffect } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table"
import {
  Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle,
} from "@/components/ui/dialog"
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Search, Plus, Edit, Trash2, Users, RefreshCw, Upload, User, MapPin, BookOpen, Heart } from "lucide-react"
import { api } from "@/lib/api"
import { BatchImport } from "./BatchImport"

interface Person {
  id: string
  name: string
  courtesy_name?: string
  art_name?: string
  alias?: string
  generation_char?: string
  gender: string
  is_outsider: boolean
  generation_id?: number
  branch_id?: string
  father_id?: string
  mother_id?: string
  birth_year?: number
  death_year?: number
  birth_place?: string
  lunar_birthday?: string
  burial_place?: string
  burial_fengshui?: string
  burial_direction?: string
  biography?: string
  achievements?: string
  descendants_location?: string
  notes?: string
  visibility: string
  father_name?: string
  mother_name?: string
  branch_name?: string
  generation_name?: string
}

interface PersonsListProps {
  tenantSlug: string
}

export function PersonsList({ tenantSlug }: PersonsListProps) {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [generationFilter, setGenerationFilter] = useState<string>("")
  const [genderFilter, setGenderFilter] = useState<string>("")
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isBatchImportOpen, setIsBatchImportOpen] = useState(false)
  const [editingPerson, setEditingPerson] = useState<Person | null>(null)
  
  const queryClient = useQueryClient()
  
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["persons", tenantSlug, page, search, generationFilter, genderFilter],
    queryFn: async () => {
      const params = new URLSearchParams({ page: String(page), page_size: "20" })
      if (search) params.append("search", search)
      if (generationFilter) params.append("generation", generationFilter)
      if (genderFilter) params.append("gender", genderFilter)
      const response = await api.get(`/t/${tenantSlug}/persons?${params}`)
      return response.data
    },
  })
  
  const { data: generations } = useQuery({
    queryKey: ["generations", tenantSlug],
    queryFn: async () => {
      const response = await api.get(`/t/${tenantSlug}/persons/generations`)
      return response.data
    },
  })
  
  const { data: branches } = useQuery({
    queryKey: ["branches", tenantSlug],
    queryFn: async () => {
      const response = await api.get(`/t/${tenantSlug}/persons/branches`)
      return response.data
    },
  })
  
  const deleteMutation = useMutation({
    mutationFn: async (personId: string) => {
      await api.delete(`/t/${tenantSlug}/persons/${personId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["persons", tenantSlug] })
    },
  })
  
  const handleDelete = (person: Person) => {
    if (confirm(`确定要删除 "${person.name}" 吗？此操作不可撤销。`)) {
      deleteMutation.mutate(person.id)
    }
  }
  
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">👤 人物管理</h2>
          <p className="text-gray-500 text-sm">共 {data?.meta?.total || 0} 条记录</p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setIsBatchImportOpen(true)}>
            <Upload className="h-4 w-4 mr-2" /> 批量导入
          </Button>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4 mr-2" /> 刷新
          </Button>
          <Button onClick={() => { setEditingPerson(null); setIsFormOpen(true); }}>
            <Plus className="h-4 w-4 mr-2" /> 添加人物
          </Button>
        </div>
      </div>
      
      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex gap-4 flex-wrap">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="搜索姓名、字、号、别名..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={generationFilter} onValueChange={setGenerationFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="世代" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">全部世代</SelectItem>
                {generations?.map((gen: any) => (
                  <SelectItem key={gen.id} value={String(gen.id)}>
                    第{gen.number}世 {gen.name ? `(${gen.name})` : ""}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={genderFilter} onValueChange={setGenderFilter}>
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="性别" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">全部</SelectItem>
                <SelectItem value="M">男</SelectItem>
                <SelectItem value="F">女</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>
      
      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-8 text-center text-gray-500">⏳ 加载中...</div>
          ) : data?.data?.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>暂无数据</p>
              <Button className="mt-4" onClick={() => setIsFormOpen(true)}>
                <Plus className="h-4 w-4 mr-2" /> 添加第一个人物
              </Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>姓名</TableHead>
                  <TableHead>世代</TableHead>
                  <TableHead>生卒年</TableHead>
                  <TableHead>父母</TableHead>
                  <TableHead>支系</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.data?.map((person: Person) => (
                  <TableRow key={person.id}>
                    <TableCell>
                      <div>
                        <span className="font-medium">{person.name}</span>
                        {(person.courtesy_name || person.art_name) && (
                          <div className="text-xs text-gray-500">
                            {person.courtesy_name && <span>字{person.courtesy_name}</span>}
                            {person.art_name && <span className="ml-2">号{person.art_name}</span>}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {person.generation_id ? `第${person.generation_id}世` : "-"}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {person.birth_year || person.death_year ? (
                          <div>
                            <div>{person.birth_year || "?"} - {person.death_year || "?"}</div>
                            {person.birth_place && (
                              <div className="text-xs text-gray-500 flex items-center gap-1">
                                <MapPin className="h-3 w-3" />{person.birth_place}
                              </div>
                            )}
                          </div>
                        ) : "-"}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {person.father_name && <div>父: {person.father_name}</div>}
                        {person.mother_name && <div>母: {person.mother_name}</div>}
                        {!person.father_name && !person.mother_name && "-"}
                      </div>
                    </TableCell>
                    <TableCell>{person.branch_name || "-"}</TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {person.visibility === "public" ? "公开" : 
                         person.visibility === "member" ? "成员可见" : "私密"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="sm" onClick={() => { setEditingPerson(person); setIsFormOpen(true); }}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(person)} className="text-red-500 hover:text-red-700">
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
      
      {/* Pagination */}
      {data?.meta && data.meta.total_pages > 1 && (
        <div className="flex justify-center gap-2">
          <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>
            上一页
          </Button>
          <span className="py-2 px-4 text-sm">{page} / {data.meta.total_pages}</span>
          <Button variant="outline" size="sm" disabled={page >= data.meta.total_pages} onClick={() => setPage(page + 1)}>
            下一页
          </Button>
        </div>
      )}
      
      {/* Form Dialog */}
      <PersonFormDialog
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        tenantSlug={tenantSlug}
        person={editingPerson}
        generations={generations || []}
        branches={branches || []}
        onSuccess={() => {
          setIsFormOpen(false)
          queryClient.invalidateQueries({ queryKey: ["persons", tenantSlug] })
        }}
      />
      
      {/* Batch Import Dialog */}
      {isBatchImportOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <BatchImport
              tenantSlug={tenantSlug}
              onSuccess={() => {
                setIsBatchImportOpen(false)
                queryClient.invalidateQueries({ queryKey: ["persons", tenantSlug] })
              }}
              onClose={() => setIsBatchImportOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  )
}

// Enhanced Person Form with tabs
interface PersonFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  tenantSlug: string
  person?: Person | null
  generations: any[]
  branches: any[]
  onSuccess: () => void
}

function PersonFormDialog({ open, onOpenChange, tenantSlug, person, generations, branches, onSuccess }: PersonFormDialogProps) {
  const [activeTab, setActiveTab] = useState("basic")
  const [formData, setFormData] = useState({
    name: "",
    courtesy_name: "",
    art_name: "",
    alias: "",
    generation_char: "",
    gender: "M",
    is_outsider: false,
    generation_id: "",
    branch_id: "",
    father_id: "",
    mother_id: "",
    birth_year: "",
    death_year: "",
    birth_place: "",
    lunar_birthday: "",
    burial_place: "",
    burial_fengshui: "",
    burial_direction: "",
    biography: "",
    achievements: "",
    descendants_location: "",
    notes: "",
    visibility: "public",
  })
  
  const [fatherSearch, setFatherSearch] = useState("")
  const [motherSearch, setMotherSearch] = useState("")
  
  // Fetch potential parents
  const { data: potentialFathers } = useQuery({
    queryKey: ["persons", tenantSlug, "search", fatherSearch, "M"],
    queryFn: async () => {
      if (!fatherSearch || fatherSearch.length < 1) return []
      const params = new URLSearchParams({ search: fatherSearch, gender: "M", page_size: "10" })
      const response = await api.get(`/t/${tenantSlug}/persons?${params}`)
      return response.data?.data || []
    },
    enabled: fatherSearch.length >= 1,
  })
  
  const { data: potentialMothers } = useQuery({
    queryKey: ["persons", tenantSlug, "search", motherSearch, "F"],
    queryFn: async () => {
      if (!motherSearch || motherSearch.length < 1) return []
      const params = new URLSearchParams({ search: motherSearch, gender: "F", page_size: "10" })
      const response = await api.get(`/t/${tenantSlug}/persons?${params}`)
      return response.data?.data || []
    },
    enabled: motherSearch.length >= 1,
  })
  
  useEffect(() => {
    if (person) {
      setFormData({
        name: person.name || "",
        courtesy_name: person.courtesy_name || "",
        art_name: person.art_name || "",
        alias: person.alias || "",
        generation_char: person.generation_char || "",
        gender: person.gender || "M",
        is_outsider: person.is_outsider || false,
        generation_id: person.generation_id?.toString() || "",
        branch_id: person.branch_id || "",
        father_id: person.father_id || "",
        mother_id: person.mother_id || "",
        birth_year: person.birth_year?.toString() || "",
        death_year: person.death_year?.toString() || "",
        birth_place: person.birth_place || "",
        lunar_birthday: person.lunar_birthday || "",
        burial_place: person.burial_place || "",
        burial_fengshui: person.burial_fengshui || "",
        burial_direction: person.burial_direction || "",
        biography: person.biography || "",
        achievements: person.achievements || "",
        descendants_location: person.descendants_location || "",
        notes: person.notes || "",
        visibility: person.visibility || "public",
      })
    } else {
      setFormData({
        name: "", courtesy_name: "", art_name: "", alias: "", generation_char: "",
        gender: "M", is_outsider: false, generation_id: "", branch_id: "",
        father_id: "", mother_id: "", birth_year: "", death_year: "",
        birth_place: "", lunar_birthday: "", burial_place: "",
        burial_fengshui: "", burial_direction: "", biography: "",
        achievements: "", descendants_location: "", notes: "", visibility: "public",
      })
    }
  }, [person])
  
  const saveMutation = useMutation({
    mutationFn: async (data: any) => {
      const payload = {
        ...data,
        generation_id: data.generation_id ? parseInt(data.generation_id) : null,
        birth_year: data.birth_year ? parseInt(data.birth_year) : null,
        death_year: data.death_year ? parseInt(data.death_year) : null,
        father_id: data.father_id || null,
        mother_id: data.mother_id || null,
        branch_id: data.branch_id || null,
      }
      
      if (person) {
        return api.put(`/t/${tenantSlug}/persons/${person.id}`, payload)
      } else {
        return api.post(`/t/${tenantSlug}/persons`, payload)
      }
    },
    onSuccess: () => onSuccess(),
  })
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    saveMutation.mutate(formData)
  }
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{person ? "编辑人物" : "添加人物"}</DialogTitle>
          <DialogDescription>
            录入人物信息，带 * 为必填项
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid grid-cols-4">
              <TabsTrigger value="basic"><User className="h-4 w-4 inline mr-1" />基本信息</TabsTrigger>
              <TabsTrigger value="life"><Heart className="h-4 w-4 inline mr-1" />生卒信息</TabsTrigger>
              <TabsTrigger value="burial"><MapPin className="h-4 w-4 inline mr-1" />安葬信息</TabsTrigger>
              <TabsTrigger value="bio"><BookOpen className="h-4 w-4 inline mr-1" />传记</TabsTrigger>
            </TabsList>
            
            {/* Basic Info Tab */}
            <TabsContent value="basic" className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">姓名 *</label>
                  <Input value={formData.name} onChange={(e) => setFormData({...formData, name: e.target.value})} required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">性别</label>
                  <Select value={formData.gender} onValueChange={(v) => setFormData({...formData, gender: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="M">男</SelectItem>
                      <SelectItem value="F">女</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">字</label>
                  <Input value={formData.courtesy_name} onChange={(e) => setFormData({...formData, courtesy_name: e.target.value})} placeholder="表字" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">号</label>
                  <Input value={formData.art_name} onChange={(e) => setFormData({...formData, art_name: e.target.value})} placeholder="别号" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">别名</label>
                  <Input value={formData.alias} onChange={(e) => setFormData({...formData, alias: e.target.value})} placeholder="曾用名、乳名等" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">辈分字</label>
                  <Input value={formData.generation_char} onChange={(e) => setFormData({...formData, generation_char: e.target.value})} placeholder="族谱辈分用字" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">世代</label>
                  <Select value={formData.generation_id} onValueChange={(v) => setFormData({...formData, generation_id: v})}>
                    <SelectTrigger><SelectValue placeholder="选择世代" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">未指定</SelectItem>
                      {generations?.map((gen: any) => (
                        <SelectItem key={gen.id} value={String(gen.id)}>第{gen.number}世 {gen.name ? `(${gen.name})` : ""}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">支系</label>
                  <Select value={formData.branch_id} onValueChange={(v) => setFormData({...formData, branch_id: v})}>
                    <SelectTrigger><SelectValue placeholder="选择支系" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">未指定</SelectItem>
                      {branches?.map((b: any) => (
                        <SelectItem key={b.id} value={b.id}>{b.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="flex items-center gap-2 pt-2">
                <input type="checkbox" id="outsider" checked={formData.is_outsider} onChange={(e) => setFormData({...formData, is_outsider: e.target.checked})} className="rounded" />
                <label htmlFor="outsider" className="text-sm">外姓（如女婿、儿媳等）</label>
              </div>
            </TabsContent>
            
            {/* Life Info Tab */}
            <TabsContent value="life" className="space-y-4 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">出生年份</label>
                  <Input type="number" value={formData.birth_year} onChange={(e) => setFormData({...formData, birth_year: e.target.value})} placeholder="如: 1950" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">逝世年份</label>
                  <Input type="number" value={formData.death_year} onChange={(e) => setFormData({...formData, death_year: e.target.value})} placeholder="如: 2020" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">出生地</label>
                  <Input value={formData.birth_place} onChange={(e) => setFormData({...formData, birth_place: e.target.value})} placeholder="省/市/县" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">农历生日</label>
                  <Input value={formData.lunar_birthday} onChange={(e) => setFormData({...formData, lunar_birthday: e.target.value})} placeholder="如: 正月初一" />
                </div>
              </div>
              
              <div className="border-t pt-4 mt-4">
                <h4 className="font-medium mb-3">父母</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">父亲</label>
                    <div className="relative">
                      <Input 
                        value={fatherSearch} 
                        onChange={(e) => { setFatherSearch(e.target.value); }}
                        placeholder="输入姓名搜索..."
                      />
                      {potentialFathers && potentialFathers.length > 0 && fatherSearch && (
                        <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-40 overflow-auto">
                          {potentialFathers.map((p: Person) => (
                            <div 
                              key={p.id} 
                              className="px-3 py-2 hover:bg-gray-50 cursor-pointer"
                              onClick={() => { setFormData({...formData, father_id: p.id}); setFatherSearch(p.name); }}
                            >
                              {p.name} {p.generation_id ? `第${p.generation_id}世` : ""}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">母亲</label>
                    <div className="relative">
                      <Input 
                        value={motherSearch} 
                        onChange={(e) => { setMotherSearch(e.target.value); }}
                        placeholder="输入姓名搜索..."
                      />
                      {potentialMothers && potentialMothers.length > 0 && motherSearch && (
                        <div className="absolute z-10 w-full mt-1 bg-white border rounded-lg shadow-lg max-h-40 overflow-auto">
                          {potentialMothers.map((p: Person) => (
                            <div 
                              key={p.id} 
                              className="px-3 py-2 hover:bg-gray-50 cursor-pointer"
                              onClick={() => { setFormData({...formData, mother_id: p.id}); setMotherSearch(p.name); }}
                            >
                              {p.name}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
            
            {/* Burial Info Tab */}
            <TabsContent value="burial" className="space-y-4 mt-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">安葬地</label>
                  <Input value={formData.burial_place} onChange={(e) => setFormData({...formData, burial_place: e.target.value})} placeholder="详细地址" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">风水坐向</label>
                    <Input value={formData.burial_fengshui} onChange={(e) => setFormData({...formData, burial_fengshui: e.target.value})} placeholder="如: 坐北朝南" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">朝向描述</label>
                    <Input value={formData.burial_direction} onChange={(e) => setFormData({...formData, burial_direction: e.target.value})} placeholder="如: 亥山巳向" />
                  </div>
                </div>
              </div>
            </TabsContent>
            
            {/* Biography Tab */}
            <TabsContent value="bio" className="space-y-4 mt-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">生平简介</label>
                  <textarea 
                    className="w-full min-h-[120px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={formData.biography} 
                    onChange={(e) => setFormData({...formData, biography: e.target.value})} 
                    placeholder="记录人物生平、职业、贡献等..."
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">成就荣誉</label>
                  <textarea 
                    className="w-full min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={formData.achievements} 
                    onChange={(e) => setFormData({...formData, achievements: e.target.value})} 
                    placeholder="功名、学位、重要事迹..."
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">后人分布</label>
                  <Input value={formData.descendants_location} onChange={(e) => setFormData({...formData, descendants_location: e.target.value})} placeholder="后人居住地" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">备注</label>
                  <textarea 
                    className="w-full min-h-[60px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={formData.notes} 
                    onChange={(e) => setFormData({...formData, notes: e.target.value})} 
                    placeholder="其他补充信息..."
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">可见性</label>
                  <Select value={formData.visibility} onValueChange={(v) => setFormData({...formData, visibility: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">公开 - 所有人可见</SelectItem>
                      <SelectItem value="member">成员可见 - 仅家族成员</SelectItem>
                      <SelectItem value="private">私密 - 仅管理员</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </TabsContent>
          </Tabs>
          
          {/* Actions */}
          <div className="flex justify-between pt-4 border-t">
            <Button type="button" variant="outline" onClick={() => setActiveTab(activeTab === "basic" ? "basic" : activeTab === "life" ? "basic" : activeTab === "burial" ? "life" : "burial")}>
              上一步
            </Button>
            <div className="flex gap-2">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>取消</Button>
              <Button type="submit" disabled={saveMutation.isPending}>
                {saveMutation.isPending ? "保存中..." : person ? "保存修改" : "添加人物"}
              </Button>
            </div>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}