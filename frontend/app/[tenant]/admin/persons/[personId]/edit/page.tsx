"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { ArrowLeft, Save, X } from "lucide-react"

interface Person {
  id: string
  name: string
  courtesy_name: string | null
  art_name: string | null
  alias: string | null
  generation_char: string | null
  gender: string
  is_outsider: boolean
  generation_id: number | null
  branch_id: string | null
  father_id: string | null
  mother_id: string | null
  birth_year: number | null
  death_year: number | null
  birth_place: string | null
  biography: string | null
  achievements: string | null
  notes: string | null
  sort_order: number
  visibility: string
}

interface Generation {
  id: number
  number: number
  title: string
}

interface Branch {
  id: string
  name: string
}

export default function PersonEditPage() {
  const params = useParams()
  const router = useRouter()
  const tenantSlug = params.tenant as string
  const personId = params.personId as string
  
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [generations, setGenerations] = useState<Generation[]>([])
  const [branches, setBranches] = useState<Branch[]>([])
  const [persons, setPersons] = useState<Person[]>([])
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  
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
    biography: "",
    achievements: "",
    notes: "",
    sort_order: "0",
    visibility: "public",
  })
  
  useEffect(() => {
    fetchData()
  }, [tenantSlug, personId])
  
  const fetchData = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const headers = { "Authorization": `Bearer ${token}` }
      
      // Fetch person data
      const personRes = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/persons/${personId}`, { headers })
      const personData = await personRes.json()
      
      if (personData.success) {
        const person = personData.data
        setFormData({
          name: person.name || "",
          courtesy_name: person.courtesy_name || "",
          art_name: person.art_name || "",
          alias: person.alias || "",
          generation_char: person.generation_char || "",
          gender: person.gender || "M",
          is_outsider: person.is_outsider || false,
          generation_id: person.generation_id?.toString() || "",
          branch_id: person.branch_id?.toString() || "",
          father_id: person.father_id?.toString() || "",
          mother_id: person.mother_id?.toString() || "",
          birth_year: person.birth_year?.toString() || "",
          death_year: person.death_year?.toString() || "",
          birth_place: person.birth_place || "",
          biography: person.biography || "",
          achievements: person.achievements || "",
          notes: person.notes || "",
          sort_order: person.sort_order?.toString() || "0",
          visibility: person.visibility || "public",
        })
      }
      
      // Fetch generations and branches
      const [genRes, branchRes, personRes2] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/generations`, { headers }),
        fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/branches`, { headers }),
        fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/persons`, { headers }),
      ])
      
      const genData = await genRes.json()
      const branchData = await branchRes.json()
      const personsData = await personRes2.json()
      
      if (genData.success) setGenerations(genData.data)
      if (branchData.success) setBranches(branchData.data)
      if (personsData.success) setPersons(personsData.data)
      
    } catch (err) {
      console.error("Failed to fetch data:", err)
      setError("加载数据失败")
    } finally {
      setLoading(false)
    }
  }
  
  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError("")
    setSuccess("")
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/persons/${personId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          ...formData,
          generation_id: formData.generation_id ? parseInt(formData.generation_id) : null,
          birth_year: formData.birth_year ? parseInt(formData.birth_year) : null,
          death_year: formData.death_year ? parseInt(formData.death_year) : null,
          sort_order: parseInt(formData.sort_order),
        })
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess("保存成功")
        setTimeout(() => router.push(`/t/${tenantSlug}/persons/${personId}`), 1000)
      } else {
        setError(data.message || "保存失败")
      }
    } catch (err) {
      setError("网络错误")
    } finally {
      setSaving(false)
    }
  }
  
  const handleCancel = () => {
    router.back()
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
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={handleCancel}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              返回
            </Button>
            <h1 className="text-xl font-bold">编辑人物</h1>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleCancel}>
              <X className="h-4 w-4 mr-2" />
              取消
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              <Save className="h-4 w-4 mr-2" />
              {saving ? "保存中..." : "保存"}
            </Button>
          </div>
        </div>
      </header>
      
      {/* Form */}
      <div className="max-w-4xl mx-auto px-4 py-8">
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
        
        <form onSubmit={handleSave} className="space-y-6">
          {/* Basic Info */}
          <Card>
            <CardHeader>
              <CardTitle>基本信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>姓名 *</Label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label>字</Label>
                  <Input
                    value={formData.courtesy_name}
                    onChange={(e) => setFormData({...formData, courtesy_name: e.target.value})}
                  />
                </div>
                <div>
                  <Label>号</Label>
                  <Input
                    value={formData.art_name}
                    onChange={(e) => setFormData({...formData, art_name: e.target.value})}
                  />
                </div>
                <div>
                  <Label>别名</Label>
                  <Input
                    value={formData.alias}
                    onChange={(e) => setFormData({...formData, alias: e.target.value})}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>性别</Label>
                  <Select
                    value={formData.gender}
                    onValueChange={(value) => setFormData({...formData, gender: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="M">男</SelectItem>
                      <SelectItem value="F">女</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center gap-2 mt-8">
                  <input
                    type="checkbox"
                    id="is_outsider"
                    checked={formData.is_outsider}
                    onChange={(e) => setFormData({...formData, is_outsider: e.target.checked})}
                    className="w-4 h-4"
                  />
                  <Label htmlFor="is_outsider">外族配偶</Label>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Family Relations */}
          <Card>
            <CardHeader>
              <CardTitle>家庭关系</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>父亲</Label>
                  <Select
                    value={formData.father_id}
                    onValueChange={(value) => setFormData({...formData, father_id: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="选择父亲" />
                    </SelectTrigger>
                    <SelectContent>
                      {persons.filter(p => p.gender === 'M').map((person) => (
                        <SelectItem key={person.id} value={person.id}>
                          {person.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>母亲</Label>
                  <Select
                    value={formData.mother_id}
                    onValueChange={(value) => setFormData({...formData, mother_id: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="选择母亲" />
                    </SelectTrigger>
                    <SelectContent>
                      {persons.filter(p => p.gender === 'F').map((person) => (
                        <SelectItem key={person.id} value={person.id}>
                          {person.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>世代</Label>
                  <Select
                    value={formData.generation_id}
                    onValueChange={(value) => setFormData({...formData, generation_id: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="选择世代" />
                    </SelectTrigger>
                    <SelectContent>
                      {generations.map((gen) => (
                        <SelectItem key={gen.id} value={gen.id.toString()}>
                          {gen.title}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>支系</Label>
                  <Select
                    value={formData.branch_id}
                    onValueChange={(value) => setFormData({...formData, branch_id: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="选择支系" />
                    </SelectTrigger>
                    <SelectContent>
                      {branches.map((branch) => (
                        <SelectItem key={branch.id} value={branch.id}>
                          {branch.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
          
          {/* Life Events */}
          <Card>
            <CardHeader>
              <CardTitle>生卒信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>出生年份</Label>
                  <Input
                    type="number"
                    value={formData.birth_year}
                    onChange={(e) => setFormData({...formData, birth_year: e.target.value})}
                    placeholder="例如：1920"
                  />
                </div>
                <div>
                  <Label>逝世年份</Label>
                  <Input
                    type="number"
                    value={formData.death_year}
                    onChange={(e) => setFormData({...formData, death_year: e.target.value})}
                    placeholder="例如：1990"
                  />
                </div>
              </div>
              <div>
                <Label>出生地</Label>
                <Input
                  value={formData.birth_place}
                  onChange={(e) => setFormData({...formData, birth_place: e.target.value})}
                  placeholder="例如：福建省福州市"
                />
              </div>
            </CardContent>
          </Card>
          
          {/* Biography */}
          <Card>
            <CardHeader>
              <CardTitle>生平事迹</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>生平简介</Label>
                <Textarea
                  value={formData.biography}
                  onChange={(e) => setFormData({...formData, biography: e.target.value})}
                  rows={5}
                  placeholder="人物生平简介..."
                />
              </div>
              <div>
                <Label>主要事迹</Label>
                <Textarea
                  value={formData.achievements}
                  onChange={(e) => setFormData({...formData, achievements: e.target.value})}
                  rows={4}
                  placeholder="主要成就和事迹..."
                />
              </div>
              <div>
                <Label>备注</Label>
                <Textarea
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  rows={3}
                  placeholder="其他备注信息..."
                />
              </div>
            </CardContent>
          </Card>
          
          {/* Settings */}
          <Card>
            <CardHeader>
              <CardTitle>设置</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>排序</Label>
                  <Input
                    type="number"
                    value={formData.sort_order}
                    onChange={(e) => setFormData({...formData, sort_order: e.target.value})}
                  />
                </div>
                <div>
                  <Label>可见性</Label>
                  <Select
                    value={formData.visibility}
                    onValueChange={(value) => setFormData({...formData, visibility: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">公开</SelectItem>
                      <SelectItem value="member">仅成员</SelectItem>
                      <SelectItem value="private">私有</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </form>
      </div>
    </main>
  )
}
