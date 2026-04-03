"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, FileText, AlertCircle, CheckCircle, X, Download } from "lucide-react"

interface BatchImportProps {
  tenantSlug: string
  onSuccess: () => void
  onClose: () => void
}

export function BatchImport({ tenantSlug, onSuccess, onClose }: BatchImportProps) {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<any[]>([])
  const [importing, setImporting] = useState(false)
  const [result, setResult] = useState<{ success: number; failed: number; errors: string[] } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    
    setFile(f)
    setResult(null)
    
    // Parse CSV/Excel for preview
    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        const text = event.target?.result as string
        const lines = text.split("\n").slice(0, 6) // Preview first 5 rows
        const headers = lines[0].split(",")
        const rows = lines.slice(1, 6).map(line => {
          const values = line.split(",")
          const obj: any = {}
          headers.forEach((h, i) => obj[h.trim()] = values[i]?.trim())
          return obj
        })
        setPreview(rows)
      } catch (err) {
        console.error("Parse error", err)
      }
    }
    reader.readAsText(f)
  }
  
  const handleImport = async () => {
    if (!file) return
    
    setImporting(true)
    setResult(null)
    
    try {
      const formData = new FormData()
      formData.append("file", file)
      
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/persons/batch-import`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData
      })
      
      const data = await res.json()
      if (data.success) {
        setResult({
          success: data.data.success || 0,
          failed: data.data.failed || 0,
          errors: data.data.errors || []
        })
        if (data.data.success > 0) {
          onSuccess()
        }
      } else {
        setResult({ success: 0, failed: 0, errors: [data.message || "导入失败"] })
      }
    } catch (err) {
      setResult({ success: 0, failed: 0, errors: ["网络错误"] })
    } finally {
      setImporting(false)
    }
  }
  
  const downloadTemplate = () => {
    const csv = `name,gender,generation_id,courtesy_name,art_name,birth_year,death_year,birth_place,father_name,mother_name,biography,visibility
张三,M,1,子敬,,1950,2020,广东省梅州市,,,公开
李四,F,1,,慧芳,1952,,,张三,,公开`
    
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "人物导入模板.csv"
    a.click()
    URL.revokeObjectURL(url)
  }
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" /> 批量导入人物
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Download Template */}
          <div className="bg-blue-50 p-4 rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-blue-500" />
              <div>
                <div className="font-medium">下载导入模板</div>
                <div className="text-sm text-gray-500">按模板格式填写人物信息</div>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={downloadTemplate}>
              <Download className="h-4 w-4 mr-1" /> 下载模板
            </Button>
          </div>
          
          {/* File Upload */}
          <div
            className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:border-vermillion transition-colors"
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.xlsx,.xls"
              className="hidden"
              onChange={handleFileChange}
            />
            {file ? (
              <div className="flex items-center justify-center gap-2">
                <FileText className="h-8 w-8 text-green-500" />
                <div className="text-left">
                  <div className="font-medium">{file.name}</div>
                  <div className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</div>
                </div>
                <button
                  className="ml-2 p-1 hover:bg-gray-100 rounded"
                  onClick={(e) => { e.stopPropagation(); setFile(null); setPreview([]); }}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <>
                <Upload className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                <div className="text-gray-600">点击上传 CSV/Excel 文件</div>
                <div className="text-sm text-gray-400">支持 .csv, .xlsx 格式</div>
              </>
            )}
          </div>
          
          {/* Preview */}
          {preview.length > 0 && (
            <div className="overflow-x-auto">
              <div className="text-sm font-medium mb-2">数据预览 (前5行)</div>
              <table className="w-full text-sm border-collapse">
                <thead>
                  <tr className="bg-gray-50">
                    {Object.keys(preview[0] || {}).map(key => (
                      <th key={key} className="px-2 py-1 text-left border">{key}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.map((row, i) => (
                    <tr key={i} className="border-b">
                      {Object.values(row).map((val: any, j) => (
                        <td key={j} className="px-2 py-1 border">{val}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          
          {/* Result */}
          {result && (
            <div className={`p-4 rounded-lg ${result.success > 0 ? "bg-green-50" : "bg-red-50"}`}>
              <div className="flex items-center gap-2 mb-2">
                {result.success > 0 ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-red-500" />
                )}
                <span className="font-medium">
                  导入完成: 成功 {result.success} 条, 失败 {result.failed} 条
                </span>
              </div>
              {result.errors.length > 0 && (
                <ul className="text-sm text-red-600 space-y-1">
                  {result.errors.slice(0, 5).map((err, i) => (
                    <li key={i}>• {err}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
          
          {/* Actions */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>取消</Button>
            <Button 
              onClick={handleImport} 
              disabled={!file || importing}
            >
              {importing ? "导入中..." : "开始导入"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}