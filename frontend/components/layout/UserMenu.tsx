"use client"

import { useState, useEffect, useRef } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"

interface UserInfo {
  id: string
  email: string
  nickname: string | null
  system_role: string
}

interface UserMenuProps {
  variant?: "default" | "transparent"
}

export function UserMenu({ variant = "default" }: UserMenuProps) {
  const router = useRouter()
  const [user, setUser] = useState<UserInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchUserInfo()
  }, [])

  useEffect(() => {
    // Close dropdown when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const fetchUserInfo = async () => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const response = await fetch("http://localhost:8012/api/v1/auth/me", {
        headers: { "Authorization": `Bearer ${token}` }
      })
      const data = await response.json()
      if (data.id) {
        setUser(data)
      }
    } catch (err) {
      console.error("Failed to fetch user info:", err)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    router.push("/login")
  }

  const getInitials = (name: string) => {
    return name.charAt(0).toUpperCase()
  }

  const getDisplayName = () => {
    return user?.nickname || user?.email?.split("@")[0] || "用户"
  }

  if (loading) {
    return (
      <div className="w-8 h-8 rounded-full bg-gray-200 animate-pulse" />
    )
  }

  if (!user) {
    return (
      <Link
        href="/login"
        className={`text-sm font-medium transition-colors ${
          variant === "transparent"
            ? "text-white/90 hover:text-white"
            : "text-ink-muted hover:text-ink"
        }`}
      >
        登录
      </Link>
    )
  }

  const isSuperAdmin = user.system_role === "super_admin"

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-2 rounded-lg transition-colors ${
          variant === "transparent"
            ? "hover:bg-white/10"
            : "hover:bg-gray-100"
        }`}
      >
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium text-white ${
          isSuperAdmin ? "bg-gradient-to-br from-amber-400 to-orange-500" : "bg-gradient-to-br from-vermillion to-red-600"
        }`}>
          {getInitials(getDisplayName())}
        </div>

        {/* Name & Arrow */}
        <div className={`hidden sm:flex items-center gap-1 text-sm ${
          variant === "transparent" ? "text-white/90" : "text-ink"
        }`}>
          <span className="max-w-[100px] truncate">{getDisplayName()}</span>
          <svg
            className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-56 rounded-xl bg-white shadow-lg border border-ink/5 py-2 z-50">
          {/* User Info Header */}
          <div className="px-4 py-3 border-b border-ink/5">
            <p className="font-medium text-ink truncate">{getDisplayName()}</p>
            <p className="text-xs text-ink-muted truncate">{user.email}</p>
            {isSuperAdmin && (
              <span className="inline-flex items-center gap-1 mt-1 text-xs text-amber-600">
                <span>👑</span> 超级管理员
              </span>
            )}
          </div>

          {/* Menu Items */}
          <div className="py-1">
            <Link
              href="/dashboard"
              className="flex items-center gap-2 px-4 py-2 text-sm text-ink hover:bg-gray-50 transition-colors"
              onClick={() => setIsOpen(false)}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              我的家族
            </Link>

            <Link
              href="/profile"
              className="flex items-center gap-2 px-4 py-2 text-sm text-ink hover:bg-gray-50 transition-colors"
              onClick={() => setIsOpen(false)}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              个人信息
            </Link>

            <Link
              href="/change-password"
              className="flex items-center gap-2 px-4 py-2 text-sm text-ink hover:bg-gray-50 transition-colors"
              onClick={() => setIsOpen(false)}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              修改密码
            </Link>

            {isSuperAdmin && (
              <Link
                href="/admin/tenants"
                className="flex items-center gap-2 px-4 py-2 text-sm text-ink hover:bg-gray-50 transition-colors"
                onClick={() => setIsOpen(false)}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                系统管理
              </Link>
            )}
          </div>

          {/* Divider */}
          <div className="border-t border-ink/5 my-1" />

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            退出登录
          </button>
        </div>
      )}
    </div>
  )
}
