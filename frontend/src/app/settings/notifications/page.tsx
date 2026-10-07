import { Suspense } from "react"
import { NotificationSettingsForm } from "@/components/settings/notification-settings"
import { Skeleton } from "@/components/ui/skeleton"

export default function NotificationSettingsPage() {
  return (
    <Suspense fallback={<Skeleton className="h-[400px] w-full" />}>
      <div className="container mx-auto py-6 space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Configurações de Notificação</h1>
          <p className="text-sm text-muted-foreground">
            Configure como e quando você receberá notificações
          </p>
        </div>
        <NotificationSettingsForm />
      </div>
    </Suspense>
  )
}
