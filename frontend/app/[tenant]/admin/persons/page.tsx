import { AdminLayout } from "@/components/admin/AdminLayout"
import { PersonsList } from "@/components/admin/PersonsList"

interface PageProps {
  params: {
    tenant: string
  }
}

export default function PersonsPage({ params }: PageProps) {
  const tenantSlug = params.tenant
  const tenantName = `${tenantSlug}家族`
  
  return (
    <AdminLayout tenantSlug={tenantSlug} tenantName={tenantName}>
      <PersonsList tenantSlug={tenantSlug} />
    </AdminLayout>
  )
}
