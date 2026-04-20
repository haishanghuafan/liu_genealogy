"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"

interface Person {
  id: string
  name: string
  gender: string
  courtesy_name?: string
  generation_id?: number
}

export default function PersonsPage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  const [persons, setPersons] = useState<Person[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")

  useEffect(() => {
    fetchPersons()
  }, [tenantSlug])

  const fetchPersons = async () => {
    try {
      const res = await fetch(`/api/v1/t/${tenantSlug}/persons`)
      const data = await res.json()
      if (data.success && data.data) {
        setPersons(data.data)
      }
    } catch (error) {
      console.error("Failed to fetch persons:", error)
    } finally {
      setLoading(false)
    }
  }

  const filteredPersons = persons.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <main className="min-h-screen bg-paper">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <div className="hidden md:flex items-center gap-6">
            <Link href={`/${tenantSlug}`} className="text-ink-muted hover:text-ink">首页</Link>
            <Link href={`/${tenantSlug}/family-tree`} className="text-ink-muted hover:text-ink">族谱树</Link>
            <Link href={`/${tenantSlug}/persons`} className="text-vermillion font-medium">家族成员</Link>
          </div>
        </div>
      </nav>

      <div className="pt-24 px-4 max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-serif font-semibold mb-2">👥 家族成员</h1>
          <p className="text-ink-muted">共 {persons.length} 位成员</p>
        </div>

        <div className="mb-6">
          <input
            type="text"
            className="w-full max-w-md px-4 py-3 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none"
            placeholder="搜索姓名..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-4 animate-bounce">⏳</div>
            <p className="text-ink-muted">加载中...</p>
          </div>
        ) : filteredPersons.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl border border-ink/5">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-ink-muted">{searchQuery ? "未找到匹配的成员" : "暂无成员数据"}</p>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredPersons.map((person) => (
              <div key={person.id} className="bg-white rounded-xl border border-ink/5 p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
                    person.gender === "M" ? "bg-blue-100 text-blue-600" : "bg-pink-100 text-pink-600"
                  }`}>
                    {person.gender === "M" ? "👨" : "👩"}
                  </div>
                  <div>
                    <h3 className="font-semibold">{person.name}</h3>
                    {person.courtesy_name && (
                      <p className="text-sm text-ink-muted">字: {person.courtesy_name}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
