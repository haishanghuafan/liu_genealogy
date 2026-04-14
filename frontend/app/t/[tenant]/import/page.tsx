"use client"

import { useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileSpreadsheet, CheckCircle, XCircle, AlertCircle } from "lucide-react"

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
      
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/import/excel`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData
      })
      
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError("上传失败，请重试")
    } finally {
      setUploading(false)
    }
  }
  
  const handleDownloadTemplate = async () => {
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8000/api/v1/t/${tenantSlug}/import/excel-template`, {
        headers: { "Authorization": `Bearer ${token}` }
      })
      
      const data = await res.json()
      if (data.success) {
        // Create CSV template (simpler than Excel)
        const headers = [
          "name", "gender", "generation_number", "branch_name",
          "father_name", "mother_name", "courtesy_name", "art_name",
          "birth_year", "death_year", "birth_place", "biography", "sort_order"
        ]
        
        const examples = [
          ["刘邦", "M", "1", "沛县支系", "", "", "", "", "-256", "-195", "江苏徐州", "", "1"],
          ["刘盈", "M", "2", "", "刘邦", "", "", "", "-210", "-188", "", "", "1"]
        ]
        
        let csv = headers.join(",") + "\n"
        examples.forEach(row => {
          csv += row.join(",") + "\n"
        })
        
        const blob = new Blob([csv], { type: 'text/csv' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = '人物导入模板.csv'
        a.click()
        URL.revokeObjectURL(url)
      }
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
              <h3 className="font-semibold mb-2">必需列：</h3>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li><strong>name</strong> - 姓名</li>
                <li><strong>gender</strong> - 性别 (M=男，F=女)</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2">可选列：</h3>
              <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                <li>generation_number - 世代编号</li>
                <li>branch_name - 支系名称</li>
                <li>father_name - 父亲姓名</li>
                <li>mother_name - 母亲姓名</li>
                <li>birth_year - 出生年份</li>
                <li>death_year - 逝世年份</li>
                <li>birth_place - 出生地</li>
                <li>biography - 生平简介</li>
              </ul>
            </div>
            <Button onClick={handleDownloadTemplate} variant="outline" size="sm">
              <FileSpreadsheet className="h-4 w-4 mr-2" />
              下载 CSV 模板
            </Button>
          </CardContent>
        </Card>
        
        {/* Upload */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>上传文件</CardTitle>
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
