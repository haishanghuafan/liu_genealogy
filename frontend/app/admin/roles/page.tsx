"use client"

import { useState, useEffect } from "react"
import Link from "next/link"

interface Permission {
  id: string
  code: string
  name: string
  group: string
  description: string | null
  resource_type: string
}

interface PermissionGroup {
  [key: string]: Permission[]
}

interface Role {
  id: string
  name: string
  code: string
  scope: string
  tenant_id: string | null
  description: string | null
  is_builtin: boolean
  permission_count: number
  permission_codes: string[]
}

export default function AdminRolesPage() {
  const [permissionGroups, setPermissionGroups] = useState<PermissionGroup>({})
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  // Role editing
  const [editingRole, setEditingRole] = useState<string | null>(null)
  const [roleForm, setRoleForm] = useState<{
    name: string
    description: string
    permission_codes: string[]
  } | null>(null)
  const [saving, setSaving] = useState(false)

  // Role creating
  const [creatingRole, setCreatingRole] = useState(false)
  const [newRoleForm, setNewRoleForm] = useState({
    name: "",
    code: "",
    description: "",
    permission_codes: [] as string[],
  })

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    const token = localStorage.getItem("access_token") || ""
    try {
      const [permsRes, rolesRes] = await Promise.all([
        fetch("http://localhost:8012/api/v1/admin/permissions/list", {
          headers: { "Authorization": `Bearer ${token}` }
        }),
        fetch("http://localhost:8012/api/v1/admin/permissions/roles?scope=system", {
          headers: { "Authorization": `Bearer ${token}` }
        }),
      ])

      const permsData = await permsRes.json()
      if (permsData.success) setPermissionGroups(permsData.data.groups)

      const rolesData = await rolesRes.json()
      if (rolesData.success) setRoles(rolesData.data)
    } catch (err) {
      setError("加载失败")
    } finally {
      setLoading(false)
    }
  }

  const openEditRole = (role: Role) => {
    setEditingRole(role.id)
    setRoleForm({
      name: role.name,
      description: role.description || "",
      permission_codes: [...role.permission_codes],
    })
    setError("")
    setSuccess("")
  }

  const handleSaveRole = async () => {
    if (!roleForm || !editingRole) return

    const role = roles.find(r => r.id === editingRole)
    if (role?.is_builtin) {
      setError("内置角色不可编辑")
      return
    }

    setSaving(true)
    setError("")
    setSuccess("")

    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8012/api/v1/admin/permissions/roles/${editingRole}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify(roleForm)
      })

      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        setEditingRole(null)
        fetchData()
      } else {
        setError(data.detail || data.message || "更新失败")
      }
    } catch (err) {
      setError("网络错误")
    } finally {
      setSaving(false)
    }
  }

  const handleCreateRole = async () => {
    if (!newRoleForm.name || !newRoleForm.code) {
      setError("名称和编码不能为空")
      return
    }

    setSaving(true)
    setError("")
    setSuccess("")

    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch("http://localhost:8012/api/v1/admin/permissions/roles", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          ...newRoleForm,
          scope: "system",
        })
      })

      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        setCreatingRole(false)
        setNewRoleForm({ name: "", code: "", description: "", permission_codes: [] })
        fetchData()
      } else {
        setError(data.detail || data.message || "创建失败")
      }
    } catch (err) {
      setError("网络错误")
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteRole = async (roleId: string) => {
    if (!confirm("确定要删除此角色吗？")) return

    try {
      const token = localStorage.getItem("access_token") || ""
      const res = await fetch(`http://localhost:8012/api/v1/admin/permissions/roles/${roleId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      })

      const data = await res.json()
      if (data.success) {
        setSuccess(data.message)
        fetchData()
      } else {
        setError(data.detail || data.message || "删除失败")
      }
    } catch (err) {
      setError("网络错误")
    }
  }

  const togglePermission = (code: string) => {
    if (!roleForm) return
    const codes = roleForm.permission_codes.includes(code)
      ? roleForm.permission_codes.filter(c => c !== code)
      : [...roleForm.permission_codes, code]
    setRoleForm({ ...roleForm, permission_codes: codes })
  }

  const toggleNewRolePermission = (code: string) => {
    const codes = newRoleForm.permission_codes.includes(code)
      ? newRoleForm.permission_codes.filter(c => c !== code)
      : [...newRoleForm.permission_codes, code]
    setNewRoleForm({ ...newRoleForm, permission_codes: codes })
  }

  const selectAllPermissions = () => {
    if (!roleForm) return
    const allCodes = Object.values(permissionGroups).flat().map(p => p.code)
    setRoleForm({ ...roleForm, permission_codes: allCodes })
  }

  const clearAllPermissions = () => {
    if (!roleForm) return
    setRoleForm({ ...roleForm, permission_codes: [] })
  }

  const selectAllNewRolePermissions = () => {
    const allCodes = Object.values(permissionGroups).flat().map(p => p.code)
    setNewRoleForm({ ...newRoleForm, permission_codes: allCodes })
  }

  const clearAllNewRolePermissions = () => {
    setNewRoleForm({ ...newRoleForm, permission_codes: [] })
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-paper pt-20 px-4">
        <div className="max-w-6xl mx-auto text-center py-20">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-ink-muted">加载中...</p>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-paper">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-ink/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl">📜</span>
            <span className="font-serif text-xl font-bold text-vermillion">族谱云</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/admin/permissions" className="text-ink-muted hover:text-ink flex items-center gap-1">
              <span>📋</span> 权限列表
            </Link>
            <Link href="/dashboard" className="text-ink-muted hover:text-ink flex items-center gap-1">
              <span>←</span> 返回控制台
            </Link>
          </div>
        </div>
      </nav>

      <div className="pt-24 px-4 max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-serif font-semibold mb-2">🔐 角色管理</h1>
          <p className="text-ink-muted">创建角色、分配权限、管理系统角色体系</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-vermillion/5 border border-vermillion/20 text-vermillion">
            ⚠️ {error}
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 rounded-lg bg-green-50 border border-green-200 text-green-700">
            ✅ {success}
          </div>
        )}

        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold">系统角色</h2>
            <button
              onClick={() => setCreatingRole(true)}
              className="bg-vermillion text-white px-4 py-2 rounded-lg hover:bg-vermillion-dark transition-colors"
            >
              + 创建角色
            </button>
          </div>

          <div className="space-y-4">
            {roles.map((role) => (
              <div key={role.id} className="bg-white rounded-xl border border-ink/5 p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-xl ${
                      role.is_builtin ? "bg-amber-100" : "bg-blue-100"
                    }`}>
                      {role.is_builtin ? "🔒" : "👤"}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-lg">{role.name}</h3>
                        {role.is_builtin && (
                          <span className="text-xs px-2 py-0.5 rounded bg-amber-100 text-amber-700">内置</span>
                        )}
                      </div>
                      <div className="text-sm text-ink-muted font-mono">{role.code}</div>
                      {role.description && (
                        <div className="text-sm text-ink-muted mt-1">{role.description}</div>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-ink-muted">
                      {role.permission_count} 个权限
                    </span>
                    <button
                      onClick={() => openEditRole(role)}
                      className="text-vermillion hover:underline text-sm"
                    >
                      {role.is_builtin ? "查看" : "编辑"}
                    </button>
                    {!role.is_builtin && (
                      <button
                        onClick={() => handleDeleteRole(role.id)}
                        className="text-red-600 hover:underline text-sm"
                      >
                        删除
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Edit Role Modal */}
      {editingRole && roleForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-semibold mb-6">
              {roles.find(r => r.id === editingRole)?.is_builtin ? "查看角色" : "编辑角色"}
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">角色名称</label>
                <input
                  type="text"
                  value={roleForm.name}
                  onChange={(e) => setRoleForm({ ...roleForm, name: e.target.value })}
                  disabled={roles.find(r => r.id === editingRole)?.is_builtin}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 disabled:bg-gray-100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">描述</label>
                <textarea
                  value={roleForm.description}
                  onChange={(e) => setRoleForm({ ...roleForm, description: e.target.value })}
                  disabled={roles.find(r => r.id === editingRole)?.is_builtin}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 disabled:bg-gray-100"
                  rows={2}
                />
              </div>

              {!roles.find(r => r.id === editingRole)?.is_builtin && (
                <div className="flex gap-2 mb-2">
                  <button onClick={selectAllPermissions} className="text-sm text-vermillion hover:underline">
                    全选
                  </button>
                  <button onClick={clearAllPermissions} className="text-sm text-gray-500 hover:underline">
                    清空
                  </button>
                </div>
              )}

              <div className="space-y-4">
                {Object.entries(permissionGroups).map(([group, perms]) => (
                  <div key={group}>
                    <h4 className="text-sm font-medium mb-2 text-ink-muted">{group}</h4>
                    <div className="grid grid-cols-2 gap-2">
                      {perms.map((perm) => (
                        <label key={perm.id} className="flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            checked={roleForm.permission_codes.includes(perm.code)}
                            onChange={() => togglePermission(perm.code)}
                            disabled={roles.find(r => r.id === editingRole)?.is_builtin}
                            className="w-4 h-4"
                          />
                          <span>{perm.name}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-3 mt-6 pt-6 border-t">
              {!roles.find(r => r.id === editingRole)?.is_builtin && (
                <button
                  onClick={handleSaveRole}
                  disabled={saving}
                  className="flex-1 bg-vermillion text-white py-3 rounded-lg hover:bg-vermillion-dark transition-colors disabled:opacity-50"
                >
                  {saving ? "保存中..." : "保存"}
                </button>
              )}
              <button
                onClick={() => setEditingRole(null)}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg hover:bg-gray-200 transition-colors"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Role Modal */}
      {creatingRole && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-semibold mb-6">创建角色</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">角色名称 *</label>
                <input
                  type="text"
                  value={newRoleForm.name}
                  onChange={(e) => setNewRoleForm({ ...newRoleForm, name: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  placeholder="如：数据管理员"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">角色编码 *</label>
                <input
                  type="text"
                  value={newRoleForm.code}
                  onChange={(e) => setNewRoleForm({ ...newRoleForm, code: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 font-mono"
                  placeholder="如：data_admin"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">描述</label>
                <textarea
                  value={newRoleForm.description}
                  onChange={(e) => setNewRoleForm({ ...newRoleForm, description: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  rows={2}
                  placeholder="角色描述..."
                />
              </div>

              <div className="flex gap-2 mb-2">
                <button onClick={selectAllNewRolePermissions} className="text-sm text-vermillion hover:underline">
                  全选
                </button>
                <button onClick={clearAllNewRolePermissions} className="text-sm text-gray-500 hover:underline">
                  清空
                </button>
              </div>

              <div className="space-y-4">
                {Object.entries(permissionGroups).map(([group, perms]) => (
                  <div key={group}>
                    <h4 className="text-sm font-medium mb-2 text-ink-muted">{group}</h4>
                    <div className="grid grid-cols-2 gap-2">
                      {perms.map((perm) => (
                        <label key={perm.id} className="flex items-center gap-2 text-sm">
                          <input
                            type="checkbox"
                            checked={newRoleForm.permission_codes.includes(perm.code)}
                            onChange={() => toggleNewRolePermission(perm.code)}
                            className="w-4 h-4"
                          />
                          <span>{perm.name}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-3 mt-6 pt-6 border-t">
              <button
                onClick={handleCreateRole}
                disabled={saving}
                className="flex-1 bg-vermillion text-white py-3 rounded-lg hover:bg-vermillion-dark transition-colors disabled:opacity-50"
              >
                {saving ? "创建中..." : "创建"}
              </button>
              <button
                onClick={() => setCreatingRole(false)}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-lg hover:bg-gray-200 transition-colors"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
