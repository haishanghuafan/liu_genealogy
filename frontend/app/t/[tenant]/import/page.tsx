"use client"

import { useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Upload, FileSpreadsheet, CheckCircle, XCircle, AlertCircle } from "lucide-react"
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
      
      const res = await fetch(`http://localhost:8012/api/v1/t/${tenantSlug}/import/excel`, {
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
      // Create Excel workbook
      const wb = XLSX.utils.book_new()

      // 统一表格：族谱人物数据（单表设计）
      // 字段顺序：基本信息 -> 世代/支系 -> 家庭关系 -> 详细信息
      const headers = [
        // 基本信息（必填）
        "姓名*", "性别*", "是否为外族配偶",
        // 世代与支系
        "世代数", "世代名称", "支系名称", "支系描述",
        // 家庭关系
        "父亲姓名", "母亲姓名", "配偶姓名",
        // 称谓信息
        "字", "号", "别名", "辈份字",
        // 生卒信息
        "出生年份", "逝世年份", "出生地",
        // 墓葬信息
        "葬地", "墓形/风水", "坐向",
        // 文字描述
        "生平简介", "主要事迹", "后裔分布",
        // 其他
        "备注", "排序"
      ]

      // 示例数据：展示一个完整家族结构
      const examples = [
        // 第1世：始祖
        ["刘邦", "男", "否", 1, "第1世", "沛县支系", "始祖刘邦所在支系", "", "", "吕雉", "", "", "", "", -256, -195, "江苏徐州", "", "", "", "汉高祖，汉朝开国皇帝", "建立汉朝，统一中国", "", "", 1],
        // 第1世：配偶
        ["吕雉", "女", "是", 1, "第1世", "", "", "", "", "刘邦", "", "", "", "", -241, -180, "", "", "", "", "汉高后，皇后", "辅佐文帝、景帝", "", "", 2],
        // 第2世：子女
        ["刘盈", "男", "否", 2, "第2世", "", "", "刘邦", "吕雉", "张嫣", "", "", "", "", -210, -188, "", "", "", "", "汉惠帝", "", "", "", 1],
        ["刘肥", "男", "否", 2, "第2世", "齐王支系", "齐王刘肥后裔", "刘邦", "曹氏", "", "", "", "", "", -221, -189, "", "", "", "", "齐悼惠王", "", "", "", 2],
        ["刘恒", "男", "否", 2, "第2世", "文帝支系", "汉文帝刘恒后裔", "刘邦", "薄姬", "窦漪房", "", "", "", "", -203, -157, "", "", "", "", "汉文帝", "开创文景之治", "", "", 3],
        // 第2世：配偶
        ["张嫣", "女", "是", 2, "第2世", "", "", "", "", "刘盈", "", "", "", "", -202, -163, "", "", "", "", "孝惠皇后", "", "", "", 4],
        ["窦漪房", "女", "是", 2, "第2世", "", "", "", "", "刘恒", "", "", "", "", -205, -135, "", "", "", "", "窦太后", "", "", "", 5],
        // 第3世
        ["刘启", "男", "否", 3, "第3世", "", "", "刘恒", "窦漪房", "王娡", "", "", "", "", -188, -141, "", "", "", "", "汉景帝", "继续文景之治", "", "", 1],
        ["刘武", "男", "否", 3, "第3世", "梁王支系", "梁孝王刘武后裔", "刘恒", "窦漪房", "", "", "", "", "", -184, -144, "", "", "", "", "梁孝王", "", "", "", 2],
        // 第3世：配偶
        ["王娡", "女", "是", 3, "第3世", "", "", "", "", "刘启", "", "", "", "", -173, -126, "", "", "", "", "孝景皇后", "", "", "", 3],
        // 第4世
        ["刘彻", "男", "否", 4, "第4世", "", "", "刘启", "王娡", "陈阿娇", "", "", "", "", -156, -87, "", "", "", "", "汉武帝", "开疆拓土，独尊儒术", "", "", 1],
      ]

      const ws = XLSX.utils.aoa_to_sheet([headers, ...examples])

      // 设置列宽（按字段分组）
      ws['!cols'] = [
        // 基本信息
        { wch: 10 }, { wch: 8 }, { wch: 12 },
        // 世代与支系
        { wch: 8 }, { wch: 10 }, { wch: 12 }, { wch: 20 },
        // 家庭关系
        { wch: 10 }, { wch: 10 }, { wch: 10 },
        // 称谓信息
        { wch: 8 }, { wch: 8 }, { wch: 10 }, { wch: 10 },
        // 生卒信息
        { wch: 10 }, { wch: 10 }, { wch: 12 },
        // 墓葬信息
        { wch: 12 }, { wch: 12 }, { wch: 10 },
        // 文字描述
        { wch: 30 }, { wch: 30 }, { wch: 20 },
        // 其他
        { wch: 20 }, { wch: 8 }
      ]

      // 添加工作表
      XLSX.utils.book_append_sheet(wb, ws, "族谱人物数据")

      // 添加说明工作表
      const helpHeaders = ["字段名", "说明", "是否必填", "示例值"]
      const helpData = [
        ["姓名*", "人物姓名", "是", "刘邦"],
        ["性别*", "男/女", "是", "男"],
        ["是否为外族配偶", "是/否，标记嫁入/入赘人员", "否", "否"],
        ["世代数", "数字，如1,2,3", "否", "1"],
        ["世代名称", "如'第1世'", "否", "第1世"],
        ["支系名称", "所属支系名称", "否", "沛县支系"],
        ["支系描述", "支系说明", "否", "始祖刘邦所在支系"],
        ["父亲姓名", "父亲姓名，用于建立父子关系", "否", "刘邦"],
        ["母亲姓名", "母亲姓名，用于建立母子关系", "否", "吕雉"],
        ["配偶姓名", "主要配偶姓名，用于建立配偶关系", "否", "吕雉"],
        ["字", "表字", "否", "季"],
        ["号", "别号", "否", ""],
        ["别名", "其他名称", "否", ""],
        ["辈份字", "辈分字", "否", ""],
        ["出生年份", "出生年份，公元前用负数", "否", "-256"],
        ["逝世年份", "逝世年份，公元前用负数", "否", "-195"],
        ["出生地", "出生地点", "否", "江苏徐州"],
        ["葬地", "安葬地点", "否", ""],
        ["墓形/风水", "墓葬形制", "否", ""],
        ["坐向", "墓葬坐向", "否", ""],
        ["生平简介", "人物简介", "否", "汉高祖，汉朝开国皇帝"],
        ["主要事迹", "重要事迹", "否", "建立汉朝，统一中国"],
        ["后裔分布", "后代分布情况", "否", ""],
        ["备注", "其他备注", "否", ""],
        ["排序", "同世代内排序，数字越小越靠前", "否", "1"],
      ]
      const helpWs = XLSX.utils.aoa_to_sheet([helpHeaders, ...helpData])
      helpWs['!cols'] = [{ wch: 18 }, { wch: 40 }, { wch: 10 }, { wch: 20 }]
      XLSX.utils.book_append_sheet(wb, helpWs, "字段说明")

      // Generate Excel file
      const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })

      // Download file
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = '族谱数据导入模板.xlsx'
      a.click()
      URL.revokeObjectURL(url)
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
              下载 Excel 模板
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
