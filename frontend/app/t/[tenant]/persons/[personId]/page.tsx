"use client"

import { useEffect, useState, useRef, useCallback } from "react"
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
  TreePine,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Image as ImageIcon,
  Video,
  Music,
  Play,
} from "lucide-react"
import { Tree } from "react-d3-tree"

interface Person {
  id: string
  name: string
  courtesy_name?: string
  art_name?: string
  alias?: string
  gender: string
  generation_id?: number
  branch_id?: string
  father_id?: string
  mother_id?: string
  birth_year?: number
  death_year?: number
  birth_place?: string
  burial_place?: string
  burial_fengshui?: string
  burial_direction?: string
  biography?: string
  achievements?: string
  descendants_location?: string
  notes?: string
  full_name?: string
  generation_name?: string
  branch_name?: string
  father_name?: string
  mother_name?: string
  avatar?: string
}

interface MediaFile {
  id: string
  type: "image" | "video" | "audio"
  url: string
  title?: string
  description?: string
  duration?: number
  created_at: string
}

interface TreePerson {
  id: string
  name: string
  gender: string
  birth_year?: number
  death_year?: number
  generation_id?: number
  spouse?: {
    id: string
    name: string
    gender: string
  }
  children?: TreePerson[]
}

interface FiveGenTree {
  center: TreePerson
  ancestors: TreePerson[]
  descendants: TreePerson[]
  total_generations: number
}

export default function PersonDetailPage() {
  const params = useParams()
  const router = useRouter()
  const tenantSlug = params.tenant as string
  const personId = params.personId as string

  const [person, setPerson] = useState<Person | null>(null)
  const [treeData, setTreeData] = useState<FiveGenTree | null>(null)
  const [media, setMedia] = useState<MediaFile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPerson()
    fetchTree()
    fetchMedia()
  }, [tenantSlug, personId])

  const fetchPerson = async () => {
    try {
      setLoading(true)
      setError(null)
      const token = localStorage.getItem("access_token") || ""
      const response = await fetch(`http://localhost:8012/api/v1/t/${tenantSlug}/persons/${personId}`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const data = await response.json()

      if (data.success && data.data) {
        setPerson(data.data)
      } else {
        setError("人物不存在")
      }
    } catch (err) {
      setError("加载失败")
      console.error("Failed to fetch person:", err)
    } finally {
      setLoading(false)
    }
  }

  const fetchTree = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const response = await fetch(`http://localhost:8012/api/v1/t/${tenantSlug}/persons/${personId}/tree`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success && data.data) {
        setTreeData(data.data)
      }
    } catch (err) {
      console.error("Failed to fetch tree:", err)
    }
  }

  const fetchMedia = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const response = await fetch(`http://localhost:8012/api/v1/t/${tenantSlug}/persons/${personId}/media`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.success && data.data) {
        setMedia(data.data)
      }
    } catch (err) {
      console.error("Failed to fetch media:", err)
    }
  }

  const formatDuration = (seconds?: number) => {
    if (!seconds) return ""
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  if (loading) {
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
            <p className="text-red-500 mb-4">{error || "加载失败或人物不存在"}</p>
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
          <Link href={`/t/${tenantSlug}/persons/${personId}/edit`}>
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
                  {person.avatar ? (
                    <img
                      src={person.avatar}
                      alt={person.name}
                      className="w-24 h-24 rounded-full object-cover border-4 border-white shadow-lg"
                    />
                  ) : (
                    <div className={`w-24 h-24 rounded-full flex items-center justify-center text-3xl font-bold text-white ${person.gender === "F" ? "bg-pink-500" : "bg-blue-500"}`}>
                      {person.name.charAt(0)}
                    </div>
                  )}

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
                          <span>{person.branch_name}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Media Gallery */}
            {media.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <ImageIcon className="h-5 w-5" />
                    媒体资料
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Images */}
                  {media.filter(m => m.type === "image").length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 mb-3">图片</h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {media.filter(m => m.type === "image").map((img) => (
                          <div key={img.id} className="relative group">
                            <img
                              src={img.url}
                              alt={img.title || "图片"}
                              className="w-full h-32 object-cover rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                              onClick={() => window.open(img.url, "_blank")}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Videos */}
                  {media.filter(m => m.type === "video").length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 mb-3">视频</h4>
                      <div className="space-y-3">
                        {media.filter(m => m.type === "video").map((vid) => (
                          <div key={vid.id} className="flex items-center gap-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <div className="w-16 h-12 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center">
                              <Play className="h-6 w-6 text-gray-500" />
                            </div>
                            <div className="flex-1">
                              <p className="font-medium">{vid.title || "未命名视频"}</p>
                              <p className="text-sm text-gray-500">
                                {new Date(vid.created_at).toLocaleDateString("zh-CN")}
                              </p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => window.open(vid.url, "_blank")}
                            >
                              播放
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Audios */}
                  {media.filter(m => m.type === "audio").length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-500 mb-3">音频</h4>
                      <div className="space-y-3">
                        {media.filter(m => m.type === "audio").map((audio) => (
                          <div key={audio.id} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <div className="flex items-center gap-3 mb-2">
                              <Music className="h-5 w-5 text-gray-500" />
                              <span className="font-medium">{audio.title || "未命名音频"}</span>
                              {audio.duration && (
                                <span className="text-sm text-gray-500">({formatDuration(audio.duration)})</span>
                              )}
                            </div>
                            <audio
                              controls
                              src={audio.url}
                              className="w-full"
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* 5-Generation Tree */}
            {treeData && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <TreePine className="h-5 w-5" />
                    五代族谱图（上2代 · 本人 · 下2代）
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <FiveGenerationTree tree={treeData} tenantSlug={tenantSlug} />
                </CardContent>
              </Card>
            )}

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
                  亲属关系
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {person.father_name && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">父亲</span>
                    <span>{person.father_name}</span>
                  </div>
                )}
                {person.mother_name && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-500">母亲</span>
                    <span>{person.mother_name}</span>
                  </div>
                )}
                {!person.father_name && !person.mother_name && (
                  <p className="text-gray-400 text-sm">暂无记录</p>
                )}
              </CardContent>
            </Card>

            {/* Notes */}
            {person.notes && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">备注</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 dark:text-gray-400 text-sm whitespace-pre-wrap">
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

// Convert FiveGenTree to react-d3-tree format
function convertToD3TreeData(tree: FiveGenTree) {
  const { center, ancestors, descendants } = tree

  // Build tree structure
  function buildTreeNode(person: TreePerson): any {
    const node: any = {
      id: person.id,
      name: person.name,
      gender: person.gender,
      birth_year: person.birth_year,
      death_year: person.death_year,
      generation_id: person.generation_id,
      spouse: person.spouse,
    }

    if (person.children && person.children.length > 0) {
      node.children = person.children.map(child => buildTreeNode(child))
    }

    return node
  }

  // Build tree with ancestors above and descendants below
  // ancestors = [grandfather, father], oldest first (index 0 is oldest)
  // We need: grandfather (top) -> father -> center -> children

  // Start with center person as base
  let rootNode = buildTreeNode(center)

  // Add descendants as children of center
  if (descendants.length > 0) {
    rootNode.children = descendants.map(child => buildTreeNode(child))
  }

  // Add ancestors on top (reverse order: father -> grandfather)
  // ancestors[0] = grandfather, ancestors[1] = father
  // We want: grandfather -> father -> center
  for (let i = ancestors.length - 1; i >= 0; i--) {
    const ancestor = ancestors[i]
    const ancestorNode = buildTreeNode(ancestor)
    ancestorNode.children = [rootNode]
    rootNode = ancestorNode
  }

  return rootNode
}

// 5-Generation Tree Component using react-d3-tree
function FiveGenerationTree({ tree, tenantSlug }: { tree: FiveGenTree; tenantSlug: string }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [zoom, setZoom] = useState(1)
  const [translate, setTranslate] = useState({ x: 400, y: 50 })

  const treeData = useCallback(() => convertToD3TreeData(tree), [tree])()

  const handleZoomIn = () => setZoom((z) => Math.min(z * 1.2, 3))
  const handleZoomOut = () => setZoom((z) => Math.max(z / 1.2, 0.3))
  const handleReset = () => {
    setZoom(1)
    setTranslate({ x: 400, y: 50 })
  }

  const handleNodeClick = (node: any) => {
    const nodeData = node.data
    if (nodeData.id && typeof window !== 'undefined') {
      window.location.href = `/t/${tenantSlug}/persons/${nodeData.id}`
    }
  }

  return (
    <div className="relative w-full h-[600px]" ref={containerRef}>
      {/* Control Panel */}
      <div className="absolute top-4 right-4 z-10 flex gap-2">
        <Button variant="outline" size="icon" onClick={handleZoomIn}>
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={handleZoomOut}>
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={handleReset}>
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-white/90 dark:bg-gray-800/90 rounded-lg p-3 shadow-lg">
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded-full bg-blue-500" />
            <span>男性</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded-full bg-pink-500" />
            <span>女性</span>
          </div>
        </div>
      </div>

      {/* Tree */}
      <Tree
        data={treeData}
        orientation="vertical"
        pathFunc="step"
        translate={translate}
        zoom={zoom}
        nodeSize={{ x: 160, y: 100 }}
        separation={{ siblings: 1.5, nonSiblings: 2 }}
        renderCustomNodeElement={(rd3tProps) => (
          <PersonNodeCard nodeData={rd3tProps.nodeDatum} onNodeClick={handleNodeClick} />
        )}
        onNodeClick={handleNodeClick}
        collapsible
        initialDepth={3}
      />
    </div>
  )
}

// Person Node Card Component for react-d3-tree
function PersonNodeCard({ nodeData, onNodeClick }: { nodeData: any; onNodeClick?: (node: any) => void }) {
  const isMale = nodeData.gender !== "F"
  const borderColor = isMale ? "border-blue-400" : "border-pink-400"
  const bgColor = isMale ? "bg-blue-50" : "bg-pink-50"
  const darkBgColor = isMale ? "dark:bg-blue-950" : "dark:bg-pink-950"

  return (
    <foreignObject width={140} height={70} x={-70} y={-35}>
      <div
        className={`
          w-full h-full rounded-lg border-2 ${borderColor} ${bgColor} ${darkBgColor}
          shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer
          p-2 overflow-hidden
        `}
        onClick={() => onNodeClick?.({ data: nodeData })}
      >
        <div className="flex flex-col items-center justify-center h-full gap-1">
          <div className="text-sm font-medium text-center">{nodeData.name}</div>
          {nodeData.spouse && (
            <div className="text-xs text-gray-500">
              配 {nodeData.spouse.name}
            </div>
          )}
          {nodeData.generation_id && (
            <div className="text-xs text-gray-400">
              第{nodeData.generation_id}世
            </div>
          )}
        </div>
      </div>
    </foreignObject>
  )
}
