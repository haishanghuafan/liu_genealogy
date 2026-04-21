"use client"

import { useState, useEffect } from "react"
import dynamic from "next/dynamic"
import Link from "next/link"

// Dynamically import FamilyTreeCanvas to avoid SSR issues with react-d3-tree
const FamilyTreeCanvas = dynamic(
  () => import("@/components/family-tree/FamilyTreeCanvas").then((mod) => mod.FamilyTreeCanvas),
  { 
    ssr: false,
    loading: () => (
      <div className="w-full h-full bg-paper-warm animate-pulse flex items-center justify-center">
        <div className="text-ink-muted">正在加载族谱树...</div>
      </div>
    )
  }
)

interface Person {
  id: string
  name: string
  generation: number
  gender: string
  birthYear?: number
  deathYear?: number
  birthPlace?: string
  courtesyName?: string
  biography?: string
  avatar_url?: string
  spouse?: { id: string; name: string }
  children?: { id: string; name: string }[]
  father?: { id: string; name: string }
  mother?: { id: string; name: string }
}

interface FamilyTreePageProps {
  tenantSlug: string
  tenantName: string
}

export function FamilyTreePage({ tenantSlug, tenantName }: FamilyTreePageProps) {
  const [selectedPerson, setSelectedPerson] = useState<Person | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [viewMode, setViewMode] = useState<"tree" | "list">("tree")

  const handleNodeClick = (personId: string) => {
    // Fetch person details
    fetchPersonDetails(personId)
  }

  const fetchPersonDetails = async (personId: string) => {
    try {
      const token = localStorage.getItem("access_token")
      const response = await fetch(`/api/v1/t/${tenantSlug}/persons/${personId}`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      })
      const data = await response.json()
      if (data.success) {
        setSelectedPerson(data.data)
      }
    } catch (error) {
      console.error("Failed to fetch person details:", error)
    }
  }

  return (
    <div className="h-screen flex flex-col bg-paper">
      {/* Header */}
      <header className="glass sticky top-0 z-50 border-b border-ink/5">
        <div className="container-ink flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2 text-ink-muted hover:text-ink transition-colors">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span className="hidden sm:inline">返回</span>
            </Link>
            <div className="w-px h-6 bg-ink/10" />
            <div>
              <h1 className="font-serif text-lg font-semibold">{tenantName}</h1>
              <p className="text-xs text-ink-muted">族谱树</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Search */}
            <div className="relative hidden md:block">
              <svg 
                className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-muted"
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                className="input-ink pl-10 pr-4 py-2 text-sm w-48"
                placeholder="搜索姓名..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            {/* View Toggle */}
            <div className="flex bg-paper-dark rounded-lg p-1">
              <button
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  viewMode === "tree" 
                    ? "bg-white text-ink shadow-sm" 
                    : "text-ink-muted hover:text-ink"
                }`}
                onClick={() => setViewMode("tree")}
              >
                树形图
              </button>
              <button
                className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                  viewMode === "list" 
                    ? "bg-white text-ink shadow-sm" 
                    : "text-ink-muted hover:text-ink"
                }`}
                onClick={() => setViewMode("list")}
              >
                列表
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Tree Canvas */}
        <div className="flex-1 relative bg-paper-warm">
          {viewMode === "tree" ? (
            <FamilyTreeCanvas
              tenantSlug={tenantSlug}
              onNodeClick={handleNodeClick}
            />
          ) : (
            <FamilyListView tenantSlug={tenantSlug} onPersonClick={handleNodeClick} />
          )}
        </div>

        {/* Sidebar - Person Details */}
        {selectedPerson && (
          <aside className="w-96 border-l border-ink/10 bg-paper overflow-y-auto">
            <PersonDetailPanel
              person={selectedPerson}
              tenantSlug={tenantSlug}
              onClose={() => setSelectedPerson(null)}
            />
          </aside>
        )}
      </div>
    </div>
  )
}

function FamilyListView({ 
  tenantSlug, 
  onPersonClick 
}: { 
  tenantSlug: string
  onPersonClick: (id: string) => void 
}) {
  const [persons, setPersons] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
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

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

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
  
  if (loading) {
    return <div className="p-8 text-center text-ink-muted">加载中...</div>
  }
  
  return (
    <div className="p-8 overflow-y-auto h-full">
      <p className="text-sm text-ink-muted mb-4">共 {totalCount} 位成员</p>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {persons.map((person) => (
          <button
            key={person.id}
            onClick={() => onPersonClick(person.id)}
            className="paper-card p-4 text-left hover:border-vermillion/20 bg-white rounded-xl border border-ink/5"
          >
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-medium ${
                person.gender === "F" ? "bg-pink-400" : "bg-blue-500"
              }`}>
                {person.name.charAt(0)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium truncate">{person.name}</div>
                <div className="text-xs text-ink-muted">
                  {person.generation_id ? `第${person.generation_id}世 · ` : ""}
                  {person.gender === "F" ? "女" : "男"}
                </div>
              </div>
            </div>
            <div className="mt-2 text-xs text-ink-muted">
              {person.birth_year && `生卒: ${person.birth_year}${person.death_year ? `-${person.death_year}` : ""}`}
            </div>
          </button>
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
        第 {currentPage} / {totalPages} 页
      </p>
    </div>
  )
}

interface PersonDetailPanelProps {
  person: Person
  tenantSlug: string
  onClose: () => void
}

function PersonDetailPanel({ person, tenantSlug, onClose }: PersonDetailPanelProps) {
  return (
    <div className="h-full">
      {/* Header */}
      <div className="sticky top-0 bg-paper border-b border-ink/5 px-6 py-4 flex items-center justify-between">
        <h2 className="font-semibold">人物详情</h2>
        <button 
          onClick={onClose}
          className="w-8 h-8 rounded-full hover:bg-paper-dark flex items-center justify-center text-ink-muted hover:text-ink transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Content */}
      <div className="p-6 space-y-6">
        {/* Avatar & Basic Info */}
        <div className="flex items-start gap-4">
          <div className={`w-16 h-16 rounded-xl flex items-center justify-center text-2xl font-bold text-white ${
            person.gender === "F" ? "bg-gradient-to-br from-pink-400 to-rose-500" : "bg-gradient-to-br from-blue-500 to-indigo-600"
          }`}>
            {person.name.charAt(0)}
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-serif font-semibold">{person.name}</h3>
            {person.courtesyName && (
              <p className="text-ink-muted text-sm">字 {person.courtesyName}</p>
            )}
            <div className="flex gap-2 mt-2">
              <span className="badge-vermillion">
                第{person.generation}世
              </span>
              <span className="badge-ink">
                {person.gender === "F" ? "女" : "男"}
              </span>
            </div>
          </div>
        </div>

        {/* Life Info Card */}
        <div className="p-4 rounded-xl bg-paper-warm border border-ink/5">
          <h4 className="text-sm font-medium text-ink-muted mb-3 flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            生平信息
          </h4>
          <div className="space-y-2 text-sm">
            {person.birthYear && (
              <div className="flex justify-between">
                <span className="text-ink-muted">出生年份</span>
                <span className="font-medium">{person.birthYear}年</span>
              </div>
            )}
            {person.deathYear && (
              <div className="flex justify-between">
                <span className="text-ink-muted">逝世年份</span>
                <span className="font-medium">{person.deathYear}年</span>
              </div>
            )}
            {person.birthPlace && (
              <div className="flex justify-between">
                <span className="text-ink-muted">出生地</span>
                <span className="font-medium">{person.birthPlace}</span>
              </div>
            )}
            {person.birthYear && (
              <div className="flex justify-between">
                <span className="text-ink-muted">享年</span>
                <span className="font-medium">
                  {person.deathYear 
                    ? `${person.deathYear - person.birthYear}岁` 
                    : "在世"
                  }
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Biography */}
        {person.biography && (
          <div>
            <h4 className="text-sm font-medium text-ink-muted mb-2">生平简介</h4>
            <p className="text-sm text-ink leading-relaxed whitespace-pre-wrap">
              {person.biography}
            </p>
          </div>
        )}

        {/* Family Relations */}
        <div>
          <h4 className="text-sm font-medium text-ink-muted mb-3">家族关系</h4>
          <div className="space-y-2">
            {person.father && (
              <RelationItem icon="👤" label="父亲" name={person.father.name} href={`/${tenantSlug}/persons/${person.father.id}`} />
            )}
            {person.mother && (
              <RelationItem icon="👩" label="母亲" name={person.mother.name} href={`/${tenantSlug}/persons/${person.mother.id}`} />
            )}
            {person.spouse && (
              <RelationItem icon="💑" label="配偶" name={person.spouse.name} href={`/${tenantSlug}/persons/${person.spouse.id}`} />
            )}
            {person.children && person.children.length > 0 && (
              <div className="pt-2 border-t border-ink/5">
                <div className="text-xs text-ink-muted mb-2">子女 ({person.children.length})</div>
                <div className="flex flex-wrap gap-2">
                  {person.children.map((child) => (
                    <Link 
                      key={child.id}
                      href={`/${tenantSlug}/persons/${child.id}`}
                      className="px-2 py-1 rounded bg-paper-dark text-sm hover:bg-ink/5 transition-colors"
                    >
                      {child.name}
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-4">
          <Link 
            href={`/${tenantSlug}/persons/${person.id}`}
            className="btn-ink-secondary flex-1 text-center py-2"
          >
            查看完整信息
          </Link>
        </div>
      </div>
    </div>
  )
}

function RelationItem({ icon, label, name, href }: { icon: string; label: string; name: string; href: string }) {
  return (
    <Link 
      href={href}
      className="flex items-center gap-3 p-2 rounded-lg hover:bg-paper-warm transition-colors group"
    >
      <span className="text-lg">{icon}</span>
      <div className="flex-1">
        <div className="text-xs text-ink-muted">{label}</div>
        <div className="text-sm font-medium group-hover:text-vermillion transition-colors">{name}</div>
      </div>
      <svg className="w-4 h-4 text-ink-muted group-hover:text-vermillion transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
      </svg>
    </Link>
  )
}