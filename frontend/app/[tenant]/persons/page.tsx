"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"

interface Person {
  id: string
  name: string
  gender: string
  courtesy_name?: string
  generation_id?: number
}

export default function PersonsPage() {
  const params = useParams()
  const router = useRouter()
  const tenantSlug = params.tenant as string
  const [persons, setPersons] = useState<Person[]>([])
  const [totalCount, setTotalCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const pageSize = 30

  useEffect(() => {
    fetchPersons(currentPage)
  }, [tenantSlug, currentPage])

  const fetchPersons = async (page: number) => {
    try {
      setLoading(true)
      const res = await fetch(`/api/v1/t/${tenantSlug}/persons?page=${page}&page_size=${pageSize}`)
      const data = await res.json()
      if (data.success && data.data) {
        setPersons(data.data)
        setTotalCount(data.meta?.total ?? data.data.length)
        setTotalPages(data.meta?.total_pages ?? 1)
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

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages: (number | string)[] = []
    const maxVisible = 5
    
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) pages.push(i)
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i)
        pages.push('...')
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 2) {
        pages.push(1)
        pages.push('...')
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i)
      } else {
        pages.push(1)
        pages.push('...')
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i)
        pages.push('...')
        pages.push(totalPages)
      }
    }
    return pages
  }

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
          <p className="text-ink-muted">共 {totalCount} 位成员</p>
        </div>

        <div className="mb-6">
          <input
            type="text"
            className="w-full max-w-md px-4 py-3 rounded-lg border border-ink/10 bg-white focus:border-vermillion focus:ring-2 focus:ring-vermillion/20 outline-none"
            placeholder="搜索当前页姓名..."
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
          <>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredPersons.map((person) => (
                <Link
                  key={person.id}
                  href={`/${tenantSlug}/persons/${person.id}`}
                  className="bg-white rounded-xl border border-ink/5 p-4 hover:shadow-md transition-shadow cursor-pointer block"
                >
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
                      {person.generation_id && (
                        <p className="text-xs text-gray-400">第{person.generation_id}世</p>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>

            {/* Pagination */}
            <div className="mt-8 flex items-center justify-center gap-2">
              <button
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-3 py-2 rounded-lg border border-ink/10 bg-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                ← 上一页
              </button>
              
              <div className="flex items-center gap-1">
                {getPageNumbers().map((page, idx) => (
                  page === '...' ? (
                    <span key={idx} className="px-3 py-2 text-ink-muted">...</span>
                  ) : (
                    <button
                      key={idx}
                      onClick={() => goToPage(page as number)}
                      className={`px-3 py-2 rounded-lg ${
                        currentPage === page
                          ? 'bg-vermillion text-white'
                          : 'border border-ink/10 bg-white hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  )
                ))}
              </div>

              <button
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-3 py-2 rounded-lg border border-ink/10 bg-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                下一页 →
              </button>
            </div>

            <p className="text-center text-sm text-ink-muted mt-4">
              第 {currentPage} / {totalPages} 页，共 {totalCount} 位成员
            </p>
          </>
        )}
      </div>
    </main>
  )
}
