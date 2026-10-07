import { Suspense } from "react"
import { TenantSettingsContent } from "@/components/settings/tenant-settings-content"
import { Skeleton } from "@/components/ui/skeleton"

export default function TenantSettingsPage() {
  return (
    <Suspense fallback={<Skeleton className="h-[400px] w-full" />}>
      <TenantSettingsContent />
    </Suspense>
  )
}
