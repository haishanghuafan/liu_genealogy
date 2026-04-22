"use client"

import { useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Upload, FileSpreadsheet, CheckCircle, XCircle, AlertCircle, AlertTriangle } from "lucide-react"
import * as XLSX from "xlsx"

interface ImportResult {
  row: number
  name: string
  success: boolean
  person_id?: string
  error?: string
}

export default function ImportExcelPage() {
  const params = useParams()
  const router = useRouter()
  const tenantSlug = params.tenant as string
  
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [replaceMode, setReplaceMode] = useState(false)
  const [result, setResult] = useState<{
    success: boolean
    imported_count: number
    error_count: number
    details: ImportResult[]
    message?: string
  } | null>(null)
  const [error, setError] = useState("")
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      // Validate file type
      if (!selectedFile.name.endsWith('.xlsx') && !selectedFile.name.endsWith('.xls')) {
        setError("请选择 Excel 文件 (.xlsx 或 .xls)")
        return
      }
      setFile(selectedFile)
      setError("")
      setResult(null)
    }
  }
  
  const handleUpload = async () => {
    if (!file) {
      setError("请选择文件")
      return
    }
    
    setUploading(true)
    setError("")
    setResult(null)
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const formData = new FormData()
      formData.append('file', file)
      
      const endpoint = replaceMode 
        ? `http://localhost:8012/api/v1/t/${tenantSlug}/import/excel/replace`
        : `http://localhost:8012/api/v1/t/${tenantSlug}/import/excel`
      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        setError(data.detail || data.message || "导入失败，请重试")
        return
      }
      
      setResult(data)
    } catch (err) {
      setError("上传失败，请重试")
    } finally {
      setUploading(false)
    }
  }
  
  const handleDownloadTemplate = async () => {
    try {
      // 下载静态模板文件
      const link = document.createElement("a")
      link.href = "/templates/liu_genealogy_template.xlsx"
      link.download = "族谱人物导入模板.xlsx"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      console.error("Failed to download template:", err)
    }
  }
  
  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold">📊 Excel 数据导入</h1>
          <Button variant="ghost" onClick={() => router.push(`/t/${tenantSlug}/persons`)}>
            ← 返回人物列表
          </Button>
        </div>
      </nav>
      
      <div className="pt-20 px-4 max-w-4xl mx-auto">
        {/* Instructions */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>导入说明</CardTitle>
            <CardDescription>
              通过 Excel 文件批量导入人物数据
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">模板结构：</h3>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li><strong>族谱人物数据</strong> - 包含完整的人物记录和关系</li>
                <li><strong>字段说明</strong> - 详细的字段说明文档</li>
                <li><strong>下载模板</strong> - 空模板，包含示例数据</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2">关键字段：</h3>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li><strong>人物序号</strong> - 全局唯一序号，从1开始</li>
                <li><strong>姓名</strong> - 人物姓名</li>
                <li><strong>性别</strong> - 男/女</li>
                <li><strong>世代数</strong> - 世代编号</li>
                <li><strong>父亲序号</strong> - 父亲的序号</li>
                <li><strong>母亲序号</strong> - 母亲的序号</li>
                <li><strong>配偶序号列表</strong> - 配偶序号，多个用逗号分隔</li>
              </ul>
            </div>
            <Button onClick={handleDownloadTemplate} variant="outline" size="sm">
              <FileSpreadsheet className="h-4 w-4 mr-2" />
              下载 Excel 模板
            </Button>
          </CardContent>
        </Card>
        
        {/* Replace Mode Toggle */}
        <Card className="mb-6 border-amber-200 bg-amber-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-amber-500 mt-0.5" />
                <div>
                  <div className="font-medium">替换导入模式</div>
                  <div className="text-sm text-gray-600">
                    开启后将先删除所有现有数据，再导入新数据。<br/>
                    <span className="text-amber-600 font-medium">警告：此操作不可逆！</span>
                  </div>
                </div>
              </div>
              <Switch 
                checked={replaceMode} 
                onCheckedChange={setReplaceMode}
              />
            </div>
          </CardContent>
        </Card>
        
        {/* Upload */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>上传文件 {replaceMode && "(替换模式)"}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload">
                <div className="cursor-pointer">
                  <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <p className="text-sm text-gray-600 mb-2">
                    {file ? file.name : "点击或拖拽文件到此处"}
                  </p>
                  <p className="text-xs text-gray-500">
                    支持格式：.xlsx, .xls
                  </p>
                </div>
              </label>
            </div>
            
            {error && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            )}
            
            <Button 
              onClick={handleUpload} 
              disabled={!file || uploading}
              className="w-full"
            >
              {uploading ? "导入中..." : "开始导入"}
            </Button>
          </CardContent>
        </Card>
        
        {/* Results */}
        {result && (
          <Card>
            <CardHeader>
              <CardTitle>导入结果</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Summary */}
              <div className="grid grid-cols-2 gap-4">
                <div className={`p-4 rounded-lg ${result.success ? 'bg-green-50' : 'bg-yellow-50'}`}>
                  <div className="flex items-center gap-2">
                    <CheckCircle className={`h-5 w-5 ${result.success ? 'text-green-600' : 'text-yellow-600'}`} />
                    <div>
                      <div className="text-2xl font-bold">{result.imported_count}</div>
                      <div className="text-sm text-gray-600">成功导入</div>
                    </div>
                  </div>
                </div>
                {result.error_count > 0 && (
                  <div className="p-4 rounded-lg bg-red-50">
                    <div className="flex items-center gap-2">
                      <XCircle className="h-5 w-5 text-red-600" />
                      <div>
                        <div className="text-2xl font-bold">{result.error_count}</div>
                        <div className="text-sm text-gray-600">导入失败</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {result.message && (
                <div className={`p-4 rounded-lg ${result.success ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'}`}>
                  {result.message}
                </div>
              )}
              
              {/* Details */}
              {result.details && result.details.length > 0 && (
                <div className="max-h-96 overflow-y-auto">
                  <h3 className="font-semibold mb-2">详细结果：</h3>
                  <div className="space-y-2">
                    {result.details.slice(0, 50).map((detail, index) => (
                      <div 
                        key={index}
                        className={`p-3 rounded-lg text-sm flex items-center justify-between ${
                          detail.success ? 'bg-green-50' : 'bg-red-50'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          {detail.success ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-600" />
                          )}
                          <span>
                            行 {detail.row}: {detail.name}
                          </span>
                        </div>
                        {!detail.success && detail.error && (
                          <span className="text-red-600 text-xs">{detail.error}</span>
                        )}
                      </div>
                    ))}
                    {result.details.length > 50 && (
                      <p className="text-center text-gray-500 text-sm py-2">
                        仅显示前 50 条，共 {result.details.length} 条
                      </p>
                    )}
                  </div>
                </div>
              )}
              
              {/* Actions */}
              <div className="flex gap-2 pt-4">
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setResult(null)
                    setFile(null)
                  }}
                >
                  重新导入
                </Button>
                <Button 
                  onClick={() => router.push(`/t/${tenantSlug}/persons`)}
                >
                  查看人物列表
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}
