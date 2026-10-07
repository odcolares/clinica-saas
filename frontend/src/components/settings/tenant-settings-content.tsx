"use client"

import { useTenantSettings } from "@/hooks/use-tenant-settings"
import { TenantSettingsForm } from "@/components/settings/tenant-settings-form"
import { Skeleton } from "@/components/ui/skeleton"

export function TenantSettingsContent() {
  const { settings, isLoading } = useTenantSettings()

  if (isLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-[500px] w-full" />
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Configurações do Tenant</h1>
        <p className="text-sm text-muted-foreground">
          Configure os horários de funcionamento e identidade visual da clínica
        </p>
      </div>
      <TenantSettingsForm settings={settings} />
    </div>
  )
}
