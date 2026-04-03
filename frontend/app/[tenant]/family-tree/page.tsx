import { FamilyTreePage } from "@/components/family-tree/FamilyTreePage"

interface PageProps {
  params: {
    tenant: string
  }
}

export default function TenantFamilyTreePage({ params }: PageProps) {
  const tenantSlug = params.tenant
  
  // TODO: Fetch tenant info from API
  const tenantName = `${tenantSlug}家族`
  
  return (
    <FamilyTreePage
      tenantSlug={tenantSlug}
      tenantName={tenantName}
    />
  )
}
