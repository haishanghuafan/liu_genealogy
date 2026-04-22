"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Lock, ArrowLeft } from "lucide-react"

export default function PasswordChangePage() {
  const router = useRouter()
  
  const [formData, setFormData] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  })
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [loading, setLoading] = useState(false)
  
  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")
    setSuccess("")
    
    // Validate passwords match
    if (formData.new_password !== formData.confirm_password) {
      setError("新密码不一致")
      setLoading(false)
      return
    }
    
    // Validate password length
    if (formData.new_password.length < 6) {
      setError("新密码至少需要 6 个字符")
      setLoading(false)
      return
    }
    
    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch("http://localhost:8012/api/v1/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          old_password: formData.old_password,
          new_password: formData.new_password,
        })
      })
      
      const data = await res.json()
      if (data.success) {
        setSuccess("密码修改成功")
        setTimeout(() => router.push("/dashboard"), 1500)
      } else {
        setError(data.message || "密码修改失败")
      }
    } catch (err) {
      setError("网络错误，请重试")
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex items-center gap-2 mb-2">
            <Button variant="ghost" size="sm" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              返回
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <Lock className="h-8 w-8 text-blue-600" />
            <CardTitle>修改密码</CardTitle>
          </div>
          <CardDescription>
            为了账户安全，请定期更换密码
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
          {success && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
              {success}
            </div>
          )}
          
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <Label>当前密码</Label>
              <Input
                type="password"
                value={formData.old_password}
                onChange={(e) => setFormData({...formData, old_password: e.target.value})}
                required
                placeholder="输入当前密码"
              />
            </div>
            <div>
              <Label>新密码</Label>
              <Input
                type="password"
                value={formData.new_password}
                onChange={(e) => setFormData({...formData, new_password: e.target.value})}
                required
                placeholder="输入新密码"
                minLength={6}
              />
            </div>
            <div>
              <Label>确认新密码</Label>
              <Input
                type="password"
                value={formData.confirm_password}
                onChange={(e) => setFormData({...formData, confirm_password: e.target.value})}
                required
                placeholder="再次输入新密码"
              />
            </div>
            <Button 
              type="submit" 
              className="w-full"
              disabled={loading}
            >
              {loading ? "修改中..." : "修改密码"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  )
}
