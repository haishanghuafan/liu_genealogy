"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Users,
  TreeDeciduous,
  Settings,
  Home,
  Menu,
  X,
} from "lucide-react"
import { useState } from "react"

interface AdminLayoutProps {
  children: React.ReactNode
  tenantSlug: string
  tenantName: string
}

const navItems = [
  { href: "/admin", label: "概览", icon: Home },
  { href: "/admin/persons", label: "人物管理", icon: Users },
  { href: "/admin/tree", label: "族谱树", icon: TreeDeciduous },
  { href: "/admin/settings", label: "设置", icon: Settings },
]

export function AdminLayout({ children, tenantSlug, tenantName }: AdminLayoutProps) {
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Mobile Header */}
      <header className="lg:hidden bg-white dark:bg-gray-900 border-b px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <span className="font-semibold">{tenantName}</span>
        </div>
        <Link href={`/${tenantSlug}/family-tree`}>
          <Button variant="outline" size="sm">查看族谱</Button>
        </Link>
      </header>
      
      <div className="flex">
        {/* Sidebar */}
        <aside
          className={cn(
            "fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-900 border-r transform transition-transform lg:translate-x-0 lg:static",
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          )}
        >
          {/* Logo */}
          <div className="p-4 border-b">
            <Link href="/" className="flex items-center gap-2">
              <TreeDeciduous className="h-6 w-6 text-primary-600" />
              <span className="font-bold text-lg">族谱云</span>
            </Link>
            <p className="text-sm text-gray-500 mt-1">{tenantName}</p>
          </div>
          
          {/* Navigation */}
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || 
                (item.href !== "/admin" && pathname.startsWith(item.href))
              
              return (
                <Link
                  key={item.href}
                  href={`/t/${tenantSlug}${item.href}`}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                    isActive
                      ? "bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300"
                      : "text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
                  )}
                  onClick={() => setSidebarOpen(false)}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>
          
          {/* Back to site */}
          <div className="absolute bottom-4 left-4 right-4">
            <Link href={`/${tenantSlug}/family-tree`}>
              <Button variant="outline" className="w-full">
                查看族谱
              </Button>
            </Link>
          </div>
        </aside>
        
        {/* Overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
        
        {/* Main Content */}
        <main className="flex-1 p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}