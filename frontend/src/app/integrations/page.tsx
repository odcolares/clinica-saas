import { Suspense } from "react"
import { IntegrationsDashboard } from "@/components/integrations/integrations-dashboard"
import { Skeleton } from "@/components/ui/skeleton"

export default function IntegrationsPage() {
  return (
    <Suspense fallback={<Skeleton className="h-[400px] w-full" />}>
      <IntegrationsDashboard />
    </Suspense>
  )
}
