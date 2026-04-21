"use client"

import { FamilyTreePage } from "@/components/family-tree/FamilyTreePage"
import { useParams } from "next/navigation"

export default function TenantFamilyTreePage() {
  const params = useParams()
  const tenantSlug = params.tenant as string
  const tenantName = `${tenantSlug}家族`

  return (
    <FamilyTreePage
      tenantSlug={tenantSlug}
      tenantName={tenantName}
    />
  )
}
