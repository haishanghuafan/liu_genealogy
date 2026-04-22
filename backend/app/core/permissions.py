"""
System permissions definition
"""

SYSTEM_PERMISSIONS = [
    # User management
    {"code": "user:view", "name": "查看用户", "group": "用户管理", "description": "查看系统用户列表和详情"},
    {"code": "user:create", "name": "创建用户", "group": "用户管理", "description": "创建新用户"},
    {"code": "user:edit", "name": "编辑用户", "group": "用户管理", "description": "编辑用户信息"},
    {"code": "user:delete", "name": "删除用户", "group": "用户管理", "description": "删除用户"},
    {"code": "user:disable", "name": "禁用/启用用户", "group": "用户管理", "description": "禁用或启用用户账号"},
    
    # Tenant management
    {"code": "tenant:view", "name": "查看租户", "group": "租户管理", "description": "查看租户列表和详情"},
    {"code": "tenant:create", "name": "创建租户", "group": "租户管理", "description": "创建新租户"},
    {"code": "tenant:edit", "name": "编辑租户", "group": "租户管理", "description": "编辑租户信息"},
    {"code": "tenant:delete", "name": "删除租户", "group": "租户管理", "description": "删除租户"},
    
    # Subscription management
    {"code": "subscription:view", "name": "查看订阅", "group": "订阅管理", "description": "查看订阅信息"},
    {"code": "subscription:edit", "name": "编辑订阅", "group": "订阅管理", "description": "编辑订阅计划和配额"},
    {"code": "subscription:plan_edit", "name": "编辑套餐", "group": "订阅管理", "description": "编辑订阅套餐配置"},
    
    # Role & Permission management
    {"code": "role:view", "name": "查看角色", "group": "角色权限", "description": "查看角色和权限列表"},
    {"code": "role:create", "name": "创建角色", "group": "角色权限", "description": "创建新角色"},
    {"code": "role:edit", "name": "编辑角色", "group": "角色权限", "description": "编辑角色信息和权限"},
    {"code": "role:delete", "name": "删除角色", "group": "角色权限", "description": "删除角色"},
    {"code": "permission:assign", "name": "分配权限", "group": "角色权限", "description": "为角色分配权限"},
    
    # System settings
    {"code": "system:settings", "name": "系统设置", "group": "系统配置", "description": "修改系统全局设置"},
    {"code": "system:analytics", "name": "数据统计", "group": "系统配置", "description": "查看系统数据统计"},
    
    # Tenant-level permissions (for tenant roles)
    {"code": "member:view", "name": "查看成员", "group": "成员管理", "description": "查看族谱成员", "resource_type": "tenant"},
    {"code": "member:create", "name": "创建成员", "group": "成员管理", "description": "创建族谱成员", "resource_type": "tenant"},
    {"code": "member:edit", "name": "编辑成员", "group": "成员管理", "description": "编辑族谱成员信息", "resource_type": "tenant"},
    {"code": "member:delete", "name": "删除成员", "group": "成员管理", "description": "删除族谱成员", "resource_type": "tenant"},
    {"code": "member:import", "name": "导入成员", "group": "成员管理", "description": "批量导入族谱成员", "resource_type": "tenant"},
    {"code": "member:export", "name": "导出数据", "group": "成员管理", "description": "导出族谱数据", "resource_type": "tenant"},
    
    {"code": "tree:view", "name": "查看族谱树", "group": "族谱管理", "description": "查看族谱树", "resource_type": "tenant"},
    {"code": "tree:edit", "name": "编辑族谱树", "group": "族谱管理", "description": "编辑族谱树结构", "resource_type": "tenant"},
    
    {"code": "branch:manage", "name": "管理分支", "group": "族谱管理", "description": "管理族谱分支", "resource_type": "tenant"},
    {"code": "generation:manage", "name": "管理世代", "group": "族谱管理", "description": "管理世代字辈", "resource_type": "tenant"},
    
    {"code": "tenant:settings", "name": "租户设置", "group": "租户设置", "description": "修改租户设置", "resource_type": "tenant"},
    {"code": "tenant:member_manage", "name": "管理成员", "group": "租户设置", "description": "管理租户成员和角色", "resource_type": "tenant"},
]

# Built-in system roles and their permissions
BUILTIN_ROLES = [
    {
        "name": "超级管理员",
        "code": "super_admin",
        "scope": "system",
        "description": "系统最高权限，拥有所有权限",
        "is_builtin": True,
        "permissions": [p["code"] for p in SYSTEM_PERMISSIONS if p.get("resource_type") != "tenant"],
    },
    {
        "name": "运营人员",
        "code": "operator",
        "scope": "system",
        "description": "系统运营人员，可管理租户和订阅",
        "is_builtin": True,
        "permissions": [
            "user:view", "tenant:view", "tenant:edit",
            "subscription:view", "subscription:edit",
            "system:analytics",
        ],
    },
    {
        "name": "普通用户",
        "code": "user",
        "scope": "system",
        "description": "普通系统用户",
        "is_builtin": True,
        "permissions": [],
    },
]

# Built-in tenant roles and their permissions
BUILTIN_TENANT_ROLES = [
    {
        "name": "管理员",
        "code": "tenant_admin",
        "description": "租户管理员，拥有租户内所有权限",
        "is_builtin": True,
        "permissions": [p["code"] for p in SYSTEM_PERMISSIONS if p.get("resource_type") == "tenant"],
    },
    {
        "name": "编辑者",
        "code": "editor",
        "description": "可编辑族谱数据",
        "is_builtin": True,
        "permissions": [
            "member:view", "member:create", "member:edit",
            "tree:view", "tree:edit",
            "branch:manage", "generation:manage",
        ],
    },
    {
        "name": "审核员",
        "code": "reviewer",
        "description": "可查看和审核数据",
        "is_builtin": True,
        "permissions": [
            "member:view", "tree:view",
        ],
    },
    {
        "name": "成员",
        "code": "member",
        "description": "普通成员，仅可查看",
        "is_builtin": True,
        "permissions": [
            "member:view", "tree:view",
        ],
    },
]
