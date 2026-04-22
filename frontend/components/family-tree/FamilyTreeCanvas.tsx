"use client"

import { useEffect, useRef, useState } from "react"
import { Tree } from "react-d3-tree"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ZoomIn, ZoomOut, Maximize2, RotateCcw } from "lucide-react"

interface SpouseInfo {
  id: string
  name: string
  gender: string
}

interface SpouseWithChildren {
  spouse: SpouseInfo
  children: PersonNode[]
}

interface PersonNode {
  id: string
  name: string
  generation?: number
  gender?: string
  birthYear?: number
  deathYear?: number
  avatar?: string
  courtesyName?: string
  isSpouse?: boolean
  children?: PersonNode[]
}

interface FamilyTreeProps {
  tenantSlug: string
  rootPersonId?: string
  onNodeClick?: (personId: string) => void
}

export function FamilyTreeCanvas({ tenantSlug, rootPersonId, onNodeClick }: FamilyTreeProps) {
  const [treeData, setTreeData] = useState<PersonNode | null>(null)
  const [totalPersons, setTotalPersons] = useState(0)
  const [totalTrees, setTotalTrees] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [zoom, setZoom] = useState(1)
  const [translate, setTranslate] = useState({ x: 400, y: 50 })
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchTreeData()
  }, [tenantSlug, rootPersonId])

  const fetchTreeData = async () => {
    try {
      setLoading(true)
      // 增加 depth 参数以获取更多世代数据
      const url = rootPersonId
        ? `http://localhost:8012/api/v1/t/${tenantSlug}/family-tree?root_id=${rootPersonId}&depth=10`
        : `http://localhost:8012/api/v1/t/${tenantSlug}/family-tree?depth=10`
      
      const response = await fetch(url)
      const data = await response.json()
      
      if (data.success) {
        if (data.data.trees) {
          setTotalPersons(data.data.total_persons || 0)
          setTotalTrees(data.data.total_trees || 0)
          
          if (data.data.trees.length === 0) {
            setTreeData(null)
          } else if (data.data.trees.length === 1) {
            setTreeData(data.data.trees[0])
          } else {
            const virtualRoot: PersonNode = {
              id: "virtual-root",
              name: "刘氏族谱",
              generation: 0,
              gender: "M",
              children: data.data.trees,
            }
            setTreeData(virtualRoot)
          }
        } else {
          setTreeData(data.data)
        }
      } else {
        setError(data.error?.message || "加载失败")
      }
    } catch (err) {
      setError("网络错误，请稍后重试")
    } finally {
      setLoading(false)
    }
  }

  const handleZoomIn = () => setZoom((z) => Math.min(z * 1.2, 3))
  const handleZoomOut = () => setZoom((z) => Math.max(z / 1.2, 0.3))
  const handleReset = () => {
    setZoom(1)
    setTranslate({ x: 400, y: 50 })
  }
  const handleFitScreen = () => {
    if (containerRef.current) {
      const { width, height } = containerRef.current.getBoundingClientRect()
      setTranslate({ x: width / 2, y: 80 })
      setZoom(0.8)
    }
  }

  if (loading) {
    return <FamilyTreeSkeleton />
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <Card className="w-96">
          <CardContent className="pt-6 text-center">
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={fetchTreeData}>重试</Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!treeData) {
    return (
      <div className="flex items-center justify-center h-full">
        <Card className="w-96">
          <CardContent className="pt-6 text-center">
            <p className="text-gray-500">暂无族谱数据</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="relative w-full h-full" ref={containerRef}>
      {/* Control Panel */}
      <div className="absolute top-4 right-4 z-10 flex gap-2">
        <Button variant="outline" size="icon" onClick={handleZoomIn}>
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={handleZoomOut}>
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={handleFitScreen}>
          <Maximize2 className="h-4 w-4" />
        </Button>
        <Button variant="outline" size="icon" onClick={handleReset}>
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>

      {/* Stats */}
      {totalPersons > 0 && (
        <div className="absolute top-4 left-4 z-10 bg-white/90 dark:bg-gray-800/90 rounded-lg p-3 shadow-lg">
          <div className="text-sm font-medium">族谱统计</div>
          <div className="text-xs text-gray-500 mt-1">
            共 {totalPersons} 位成员 · {totalTrees} 个分支
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-white/90 dark:bg-gray-800/90 rounded-lg p-3 shadow-lg">
        <div className="text-sm font-medium mb-2">图例</div>
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded-full bg-blue-500" />
            <span>男性</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-4 rounded-full bg-pink-500" />
            <span>女性</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-0.5 bg-gray-400" />
            <span>父子</span>
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
        nodeSize={{ x: 280, y: 160 }}
        separation={{ siblings: 1.8, nonSiblings: 2.2 }}
        renderCustomNodeElement={(rd3tProps) => (
          <PersonNodeCard
            nodeData={rd3tProps.nodeDatum as PersonNode}
            onNodeClick={onNodeClick}
          />
        )}
        onNodeClick={(node) => {
          const nodeData = node.data as PersonNode
          if (nodeData.id !== "virtual-root" && onNodeClick) {
            onNodeClick(nodeData.id)
          }
        }}
        collapsible={false}
      />
    </div>
  )
}

interface PersonNodeCardProps {
  nodeData: PersonNode
  onNodeClick?: (personId: string) => void
}

function PersonNodeCard({ nodeData, onNodeClick }: PersonNodeCardProps) {
  const isVirtualRoot = nodeData.id === "virtual-root"
  const isMale = nodeData.gender !== "F"
  const isSpouse = nodeData.isSpouse || false
  
  if (isVirtualRoot) {
    return (
      <foreignObject width={200} height={60} x={-100} y={-30}>
        <div
          className="w-full h-full rounded-lg border-2 border-amber-400 bg-amber-50 dark:bg-amber-950 shadow-lg p-2 flex items-center justify-center cursor-default"
        >
          <div className="font-serif font-bold text-amber-800 dark:text-amber-200 text-base">
            {nodeData.name}
          </div>
        </div>
      </foreignObject>
    )
  }

  // 配偶节点显示样式
  if (isSpouse) {
    return (
      <foreignObject width={180} height={80} x={-90} y={-40}>
        <div
          className={`
            w-full h-full rounded-lg border-2 border-pink-300 bg-pink-50 dark:bg-pink-950
            shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer
            p-3 flex flex-col
          `}
          onClick={() => onNodeClick?.(nodeData.id)}
        >
          <div className="flex items-center gap-3 flex-1">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-pink-500 flex items-center justify-center text-white font-bold">
                {nodeData.name.charAt(0)}
              </div>
            </div>

            <div className="flex-1 min-w-0">
              <div className="font-medium text-sm truncate">{nodeData.name}</div>
              {nodeData.generation && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  第{nodeData.generation}世
                </div>
              )}
            </div>
          </div>
        </div>
      </foreignObject>
    )
  }

  // 主要人物节点显示样式
  const borderColor = isMale ? "border-blue-400" : "border-pink-400"
  const bgColor = isMale ? "bg-blue-50" : "bg-pink-50"
  const darkBgColor = isMale ? "dark:bg-blue-950" : "dark:bg-pink-950"
  const avatarColor = isMale ? "bg-blue-500" : "bg-pink-500"

  return (
    <foreignObject width={180} height={100} x={-90} y={-50}>
      <div
        className={`
          w-full h-full rounded-lg border-2 ${borderColor} ${bgColor} ${darkBgColor}
          shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer
          p-3 flex flex-col
        `}
        onClick={() => onNodeClick?.(nodeData.id)}
      >
        <div className="flex items-center gap-3 flex-1">
          <div className="flex-shrink-0">
            {nodeData.avatar ? (
              <img
                src={nodeData.avatar}
                alt={nodeData.name}
                className="w-10 h-10 rounded-full object-cover border-2 border-white"
              />
            ) : (
              <div className={`w-10 h-10 rounded-full ${avatarColor} flex items-center justify-center text-white font-bold`}>
                {nodeData.name.charAt(0)}
              </div>
            )}
          </div>

          <div className="flex-1 min-w-0">
            <div className="font-medium text-sm truncate">{nodeData.name}</div>
            {nodeData.generation && (
              <div className="text-xs text-gray-500 dark:text-gray-400">
                第{nodeData.generation}世
              </div>
            )}
            {nodeData.birthYear && (
              <div className="text-xs text-gray-400 dark:text-gray-500">
                {nodeData.birthYear}{nodeData.deathYear ? ` - ${nodeData.deathYear}` : ""}
              </div>
            )}
          </div>
        </div>
      </div>
    </foreignObject>
  )
}

function FamilyTreeSkeleton() {
  return (
    <div className="w-full h-full bg-gray-100 dark:bg-gray-900 animate-pulse flex items-center justify-center">
      <div className="text-gray-400">正在加载族谱树...</div>
    </div>
  )
}
