"use client"

import { useState, useEffect, useRef } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowLeft, Upload, X, Image as ImageIcon, Video, Music, User } from "lucide-react"
import { api } from "@/lib/api"

interface Person {
  id: string
  name: string
  courtesy_name?: string
  art_name?: string
  alias?: string
  gender: string
  generation_id?: number
  birth_year?: number
  death_year?: number
  birth_place?: string
  burial_place?: string
  biography?: string
  achievements?: string
  notes?: string
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

// File size limits in bytes
const MAX_AVATAR_SIZE = 5 * 1024 * 1024      // 5MB
const MAX_IMAGE_SIZE = 10 * 1024 * 1024      // 10MB
const MAX_AUDIO_SIZE = 50 * 1024 * 1024      // 50MB
const MAX_VIDEO_SIZE = 100 * 1024 * 1024     // 100MB

export default function PersonEditPage() {
  const params = useParams()
  const router = useRouter()
  const tenantSlug = params.tenant as string
  const personId = params.personId as string

  const [person, setPerson] = useState<Person | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const [media, setMedia] = useState<MediaFile[]>([])
  const [mediaLoading, setMediaLoading] = useState(false)

  const [formData, setFormData] = useState<Partial<Person>>({})

  // Upload states
  const [uploadingAvatar, setUploadingAvatar] = useState(false)
  const [uploadingImage, setUploadingImage] = useState(false)
  const [uploadingVideo, setUploadingVideo] = useState(false)
  const [uploadingAudio, setUploadingAudio] = useState(false)

  const avatarInputRef = useRef<HTMLInputElement>(null)
  const imageInputRef = useRef<HTMLInputElement>(null)
  const videoInputRef = useRef<HTMLInputElement>(null)
  const audioInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchPerson()
    fetchMedia()
  }, [tenantSlug, personId])

  const fetchPerson = async () => {
    try {
      const response = await api.get(`/t/${tenantSlug}/persons/${personId}`)
      if (response.success && response.data) {
        setPerson(response.data)
        setFormData(response.data)
      } else {
        setError("人物不存在")
      }
    } catch (err) {
      setError("加载失败")
    } finally {
      setLoading(false)
    }
  }

  const fetchMedia = async () => {
    setMediaLoading(true)
    try {
      const response = await api.get(`/t/${tenantSlug}/persons/${personId}/media`)
      if (response.success) {
        setMedia(response.data || [])
      }
    } catch (err) {
      console.error("Failed to fetch media:", err)
    } finally {
      setMediaLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError("")
    setSuccess("")

    try {
      const response = await api.put(`/t/${tenantSlug}/persons/${personId}`, formData)
      if (response.success) {
        setSuccess("保存成功")
        setTimeout(() => {
          router.push(`/t/${tenantSlug}/persons/${personId}`)
        }, 1000)
      } else {
        setError(response.message || "保存失败")
      }
    } catch (err: any) {
      setError(err.message || "网络错误")
    } finally {
      setSaving(false)
    }
  }

  // Avatar upload
  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > MAX_AVATAR_SIZE) {
      setError(`头像大小不能超过 ${MAX_AVATAR_SIZE / (1024 * 1024)}MB`)
      return
    }

    setUploadingAvatar(true)
    setError("")

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await api.post(`/t/${tenantSlug}/persons/${personId}/avatar`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
      if (response.success) {
        setPerson(prev => prev ? { ...prev, avatar: response.data.url } : null)
        setSuccess("头像上传成功")
      } else {
        setError(response.message || "上传失败")
      }
    } catch (err: any) {
      setError(err.message || "上传失败")
    } finally {
      setUploadingAvatar(false)
    }
  }

  const handleAvatarDelete = async () => {
    try {
      const response = await api.delete(`/t/${tenantSlug}/persons/${personId}/avatar`)
      if (response.success) {
        setPerson(prev => prev ? { ...prev, avatar: undefined } : null)
        setSuccess("头像已删除")
      }
    } catch (err: any) {
      setError(err.message || "删除失败")
    }
  }

  // Image upload
  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > MAX_IMAGE_SIZE) {
      setError(`图片大小不能超过 ${MAX_IMAGE_SIZE / (1024 * 1024)}MB`)
      return
    }

    setUploadingImage(true)
    setError("")

    const formData = new FormData()
    formData.append("file", file)
    formData.append("title", file.name)

    try {
      const response = await api.post(`/t/${tenantSlug}/persons/${personId}/images`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
      if (response.success) {
        fetchMedia()
        setSuccess("图片上传成功")
      } else {
        setError(response.message || "上传失败")
      }
    } catch (err: any) {
      setError(err.message || "上传失败")
    } finally {
      setUploadingImage(false)
    }
  }

  // Video upload
  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > MAX_VIDEO_SIZE) {
      setError(`视频大小不能超过 ${MAX_VIDEO_SIZE / (1024 * 1024)}MB`)
      return
    }

    setUploadingVideo(true)
    setError("")

    const formData = new FormData()
    formData.append("file", file)
    formData.append("title", file.name)

    try {
      const response = await api.post(`/t/${tenantSlug}/persons/${personId}/videos`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
      if (response.success) {
        fetchMedia()
        setSuccess("视频上传成功")
      } else {
        setError(response.message || "上传失败")
      }
    } catch (err: any) {
      setError(err.message || "上传失败")
    } finally {
      setUploadingVideo(false)
    }
  }

  // Audio upload
  const handleAudioUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > MAX_AUDIO_SIZE) {
      setError(`音频大小不能超过 ${MAX_AUDIO_SIZE / (1024 * 1024)}MB`)
      return
    }

    setUploadingAudio(true)
    setError("")

    const formData = new FormData()
    formData.append("file", file)
    formData.append("title", file.name)

    try {
      const response = await api.post(`/t/${tenantSlug}/persons/${personId}/audios`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })
      if (response.success) {
        fetchMedia()
        setSuccess("音频上传成功")
      } else {
        setError(response.message || "上传失败")
      }
    } catch (err: any) {
      setError(err.message || "上传失败")
    } finally {
      setUploadingAudio(false)
    }
  }

  // Delete media
  const handleDeleteMedia = async (mediaItem: MediaFile) => {
    if (!confirm(`确定要删除这个${mediaItem.type === "image" ? "图片" : mediaItem.type === "video" ? "视频" : "音频"}吗？`)) {
      return
    }

    try {
      const endpoint = mediaItem.type === "image" ? "images" : mediaItem.type === "video" ? "videos" : "audios"
      const response = await api.delete(`/t/${tenantSlug}/persons/${personId}/${endpoint}/${mediaItem.id}`)
      if (response.success) {
        fetchMedia()
        setSuccess("删除成功")
      }
    } catch (err: any) {
      setError(err.message || "删除失败")
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

  if (!person) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-red-500 mb-4">{error || "人物不存在"}</p>
            <Button onClick={() => router.back()}>返回</Button>
          </CardContent>
        </Card>
      </main>
    )
  }

  const images = media.filter(m => m.type === "image")
  const videos = media.filter(m => m.type === "video")
  const audios = media.filter(m => m.type === "audio")

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="bg-white dark:bg-gray-900 border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            返回
          </Button>
          <div className="flex-1">
            <h1 className="text-xl font-bold">编辑人物</h1>
            <p className="text-sm text-gray-500">{person.name}</p>
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? "保存中..." : "保存"}
          </Button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Messages */}
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

        <Tabs defaultValue="basic" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-[400px]">
            <TabsTrigger value="basic">基本信息</TabsTrigger>
            <TabsTrigger value="avatar">头像</TabsTrigger>
            <TabsTrigger value="media">媒体文件</TabsTrigger>
            <TabsTrigger value="bio">生平事迹</TabsTrigger>
          </TabsList>

          {/* Basic Info Tab */}
          <TabsContent value="basic">
            <Card>
              <CardHeader>
                <CardTitle>基本信息</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">姓名 *</label>
                    <Input
                      value={formData.name || ""}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">性别</label>
                    <select
                      value={formData.gender || "M"}
                      onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg"
                    >
                      <option value="M">男</option>
                      <option value="F">女</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">字</label>
                    <Input
                      value={formData.courtesy_name || ""}
                      onChange={(e) => setFormData({ ...formData, courtesy_name: e.target.value })}
                      placeholder="字号"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">号</label>
                    <Input
                      value={formData.art_name || ""}
                      onChange={(e) => setFormData({ ...formData, art_name: e.target.value })}
                      placeholder="号"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">世代</label>
                    <Input
                      type="number"
                      value={formData.generation_id || ""}
                      onChange={(e) => setFormData({ ...formData, generation_id: e.target.value ? Number(e.target.value) : undefined })}
                      placeholder="如：1"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">出生年</label>
                    <Input
                      type="number"
                      value={formData.birth_year || ""}
                      onChange={(e) => setFormData({ ...formData, birth_year: e.target.value ? Number(e.target.value) : undefined })}
                      placeholder="如：1980"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">逝世年</label>
                    <Input
                      type="number"
                      value={formData.death_year || ""}
                      onChange={(e) => setFormData({ ...formData, death_year: e.target.value ? Number(e.target.value) : undefined })}
                      placeholder="如：2050"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">出生地</label>
                  <Input
                    value={formData.birth_place || ""}
                    onChange={(e) => setFormData({ ...formData, birth_place: e.target.value })}
                    placeholder="出生地"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">葬地</label>
                  <Input
                    value={formData.burial_place || ""}
                    onChange={(e) => setFormData({ ...formData, burial_place: e.target.value })}
                    placeholder="葬地"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Avatar Tab */}
          <TabsContent value="avatar">
            <Card>
              <CardHeader>
                <CardTitle>头像设置</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col items-center gap-6">
                  {/* Avatar Preview */}
                  <div className="relative">
                    {person.avatar ? (
                      <img
                        src={person.avatar}
                        alt={person.name}
                        className="w-32 h-32 rounded-full object-cover border-4 border-white shadow-lg"
                      />
                    ) : (
                      <div className={`w-32 h-32 rounded-full flex items-center justify-center text-4xl font-bold text-white border-4 border-white shadow-lg ${person.gender === "F" ? "bg-pink-500" : "bg-blue-500"}`}>
                        {person.name.charAt(0)}
                      </div>
                    )}
                  </div>

                  {/* Upload Actions */}
                  <div className="flex gap-3">
                    <input
                      ref={avatarInputRef}
                      type="file"
                      accept="image/jpeg,image/png,image/gif,image/webp"
                      className="hidden"
                      onChange={handleAvatarUpload}
                    />
                    <Button
                      variant="outline"
                      onClick={() => avatarInputRef.current?.click()}
                      disabled={uploadingAvatar}
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      {uploadingAvatar ? "上传中..." : "上传头像"}
                    </Button>
                    {person.avatar && (
                      <Button variant="outline" onClick={handleAvatarDelete} className="text-red-600">
                        <X className="h-4 w-4 mr-2" />
                        删除头像
                      </Button>
                    )}
                  </div>

                  <p className="text-sm text-gray-500">
                    支持 JPG、PNG、GIF、WebP 格式，最大 {MAX_AVATAR_SIZE / (1024 * 1024)}MB
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Media Tab */}
          <TabsContent value="media">
            <div className="space-y-6">
              {/* Images */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <ImageIcon className="h-5 w-5" />
                    图片 ({images.length})
                  </CardTitle>
                  <div>
                    <input
                      ref={imageInputRef}
                      type="file"
                      accept="image/jpeg,image/png,image/gif,image/webp"
                      className="hidden"
                      onChange={handleImageUpload}
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => imageInputRef.current?.click()}
                      disabled={uploadingImage}
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      {uploadingImage ? "上传中..." : "上传图片"}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {images.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">暂无图片</p>
                  ) : (
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                      {images.map((img) => (
                        <div key={img.id} className="relative group">
                          <img
                            src={img.url}
                            alt={img.title || "图片"}
                            className="w-full h-32 object-cover rounded-lg"
                          />
                          <button
                            onClick={() => handleDeleteMedia(img)}
                            className="absolute top-2 right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <X className="h-4 w-4" />
                          </button>
                          {img.title && (
                            <p className="text-xs text-gray-500 mt-1 truncate">{img.title}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  <p className="text-xs text-gray-400 mt-4">
                    支持 JPG、PNG、GIF、WebP 格式，最大 {MAX_IMAGE_SIZE / (1024 * 1024)}MB
                  </p>
                </CardContent>
              </Card>

              {/* Videos */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Video className="h-5 w-5" />
                    视频 ({videos.length})
                  </CardTitle>
                  <div>
                    <input
                      ref={videoInputRef}
                      type="file"
                      accept="video/mp4,video/webm,video/quicktime"
                      className="hidden"
                      onChange={handleVideoUpload}
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => videoInputRef.current?.click()}
                      disabled={uploadingVideo}
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      {uploadingVideo ? "上传中..." : "上传视频"}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {videos.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">暂无视频</p>
                  ) : (
                    <div className="space-y-3">
                      {videos.map((vid) => (
                        <div key={vid.id} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                          <Video className="h-10 w-10 text-gray-400" />
                          <div className="flex-1">
                            <p className="font-medium">{vid.title || "未命名视频"}</p>
                            <p className="text-sm text-gray-500">
                              {new Date(vid.created_at).toLocaleDateString("zh-CN")}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteMedia(vid)}
                            className="text-red-600"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                  <p className="text-xs text-gray-400 mt-4">
                    支持 MP4、WebM、MOV 格式，最大 {MAX_VIDEO_SIZE / (1024 * 1024)}MB
                  </p>
                </CardContent>
              </Card>

              {/* Audios */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Music className="h-5 w-5" />
                    音频 ({audios.length})
                  </CardTitle>
                  <div>
                    <input
                      ref={audioInputRef}
                      type="file"
                      accept="audio/mpeg,audio/mp3,audio/wav,audio/ogg"
                      className="hidden"
                      onChange={handleAudioUpload}
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => audioInputRef.current?.click()}
                      disabled={uploadingAudio}
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      {uploadingAudio ? "上传中..." : "上传音频"}
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  {audios.length === 0 ? (
                    <p className="text-gray-500 text-center py-8">暂无音频</p>
                  ) : (
                    <div className="space-y-3">
                      {audios.map((audio) => (
                        <div key={audio.id} className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
                          <Music className="h-10 w-10 text-gray-400" />
                          <div className="flex-1">
                            <p className="font-medium">{audio.title || "未命名音频"}</p>
                            <p className="text-sm text-gray-500">
                              {formatDuration(audio.duration)} · {new Date(audio.created_at).toLocaleDateString("zh-CN")}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteMedia(audio)}
                            className="text-red-600"
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                  <p className="text-xs text-gray-400 mt-4">
                    支持 MP3、WAV、OGG 格式，最大 {MAX_AUDIO_SIZE / (1024 * 1024)}MB。适合上传口述历史、访谈录音等。
                  </p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Bio Tab */}
          <TabsContent value="bio">
            <Card>
              <CardHeader>
                <CardTitle>生平事迹</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">生平简介</label>
                  <textarea
                    value={formData.biography || ""}
                    onChange={(e) => setFormData({ ...formData, biography: e.target.value })}
                    rows={6}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="简述人物生平..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">主要事迹</label>
                  <textarea
                    value={formData.achievements || ""}
                    onChange={(e) => setFormData({ ...formData, achievements: e.target.value })}
                    rows={6}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="记录主要成就和事迹..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">备注</label>
                  <textarea
                    value={formData.notes || ""}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    rows={4}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="其他补充信息..."
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </main>
  )
}
