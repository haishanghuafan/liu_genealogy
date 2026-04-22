"use client"

import { useState } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"

export default function ExportPage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  
  const [exporting, setExporting] = useState<string | null>(null)
  const [error, setError] = useState("")
  
  const handleExport = async (type: string) => {
    setExporting(type)
    setError("")
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`/api/v1/t/${tenantSlug}/export/${type}/excel`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      
      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || "导出失败")
      }
      
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${type}_${new Date().toISOString().split("T")[0]}.xlsx`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err: any) {
      setError(err.message || "导出失败")
    } finally {
      setExporting(null)
    }
  }
  
  const exportOptions = [
    {
      id: "single-sheet",
      title: "📊 族谱数据（单表）",
      description: "导出所有族谱数据到单个 Excel 工作表，包含人物、世代、关系等完整信息，可直接用于导入",
      icon: "📊",
      highlight: true,
    },
    {
      id: "persons",
      title: "👥 人物数据",
      description: "仅导出人物详细信息列表",
      icon: "👥",
    },
    {
      id: "full",
      title: "📦 完整数据包（多表）",
      description: "导出所有数据到多个 Excel 工作表（世代、人物、配偶关系）",
      icon: "📦",
    },
  ]
  
  return (
    <main className="min-h-screen bg-paper">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href={`/t/${tenantSlug}`} className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <Link href={`/t/${tenantSlug}`} className="text-ink-muted hover:text-ink flex items-center gap-1">
            <span>←</span> 返回
          </Link>
        </div>
      </nav>
      
      <div className="pt-24 px-4 max-w-4xl mx-auto">
        <h1 className="text-3xl font-serif font-semibold mb-4">📥 数据导出</h1>
        <p className="text-ink-muted mb-8">将族谱数据导出为 Excel 文件，方便备份和离线查看</p>
        
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-vermillion/5 border border-vermillion/20 text-vermillion">
            ⚠️ {error}
          </div>
        )}
        
        <div className="space-y-4">
          {exportOptions.map((option) => (
            <div
              key={option.id}
              className={`bg-white rounded-xl p-6 border ${
                option.highlight 
                  ? "border-vermillion/20 bg-gradient-to-r from-vermillion/5 to-transparent" 
                  : "border-ink/5"
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold mb-1 flex items-center gap-2">
                    <span className="text-2xl">{option.icon}</span>
                    {option.title}
                  </h3>
                  <p className="text-sm text-ink-muted">{option.description}</p>
                </div>
                <button
                  onClick={() => handleExport(option.id)}
                  disabled={exporting !== null}
                  className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                    option.highlight
                      ? "bg-vermillion text-white hover:bg-vermillion-dark"
                      : "bg-ink text-white hover:bg-ink-light"
                  } disabled:opacity-50`}
                >
                  {exporting === option.id ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-spin">⏳</span> 导出中...
                    </span>
                  ) : (
                    "📥 导出 Excel"
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="font-medium text-blue-800 mb-2">💡 提示</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• 推荐使用"族谱数据（单表）"导出，格式与导入模板完全匹配</li>
            <li>• 导出的 Excel 文件可用 Microsoft Office 或 WPS 打开</li>
            <li>• 建议定期导出完整数据包进行备份</li>
            <li>• 单表导出的数据可直接用于重新导入系统</li>
          </ul>
        </div>
      </div>
    </main>
  )
}