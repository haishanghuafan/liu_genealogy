import { AdminLayout } from "@/components/admin/AdminLayout"
import { AdminDashboard } from "@/components/admin/AdminDashboard"

interface PageProps {
  params: {
    tenant: string
  }
}

export default function AdminHomePage({ params }: PageProps) {
  const tenantSlug = params.tenant
  const tenantName = `${tenantSlug}家族`
  
  return (
    <AdminLayout tenantSlug={tenantSlug} tenantName={tenantName}>
      <AdminDashboard tenantSlug={tenantSlug} />
    </AdminLayout>
  )
}
