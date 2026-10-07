import { Suspense } from "react"
import { ProfessionalDashboard } from "@/components/professionals/professional-dashboard"
import { Skeleton } from "@/components/ui/skeleton"

export default function ProfessionalDashboardPage() {
  return (
    <Suspense fallback={<Skeleton className="h-[400px] w-full" />}>
      <ProfessionalDashboard professionalId="prof-001" />
    </Suspense>
  )
}
