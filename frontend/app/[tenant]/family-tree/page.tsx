import { FamilyTreePage } from "@/components/family-tree/FamilyTreePage"
import { Suspense } from "react"

interface PageProps {
  params: Promise<{
    tenant: string
  }>
}

export default async function TenantFamilyTreePage({ params }: PageProps) {
  const { tenant: tenantSlug } = await params
  const tenantName = `${tenantSlug}家族`

  return (
    <Suspense fallback={<div>加载中...</div>}>
      <FamilyTreePage
        tenantSlug={tenantSlug}
        tenantName={tenantName}
      />
    </Suspense>
  )
}
