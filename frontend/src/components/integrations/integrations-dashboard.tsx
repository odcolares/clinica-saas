"use client"

import { useState } from "react"
import { Plus, Globe } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { IntegrationForm, IntegrationList } from "@/components/integrations/integration-form"
import { useIntegrations } from "@/hooks/use-integrations"
import { Skeleton } from "@/components/ui/skeleton"
import type { IntegrationConfig } from "@/types/api"

export function IntegrationsDashboard() {
  const { integrations, isLoading, isError } = useIntegrations()
  const [editingIntegration, setEditingIntegration] = useState<IntegrationConfig | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  if (isLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="container mx-auto py-6">
        <p className="text-center text-muted-foreground">
          Erro ao carregar integrações
        </p>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Integrações</h1>
          <p className="text-sm text-muted-foreground">
            Gerencie conexões com serviços externos
          </p>
        </div>
        <Dialog
          open={isDialogOpen || !!editingIntegration}
          onOpenChange={(open) => {
            if (!open) {
              setIsDialogOpen(false)
              setEditingIntegration(null)
            }
          }}
        >
          <DialogTrigger asChild>
            <Button onClick={() => setIsDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Nova Integração
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>
                {editingIntegration ? "Editar Integração" : "Nova Integração"}
              </DialogTitle>
            </DialogHeader>
            <IntegrationForm
              integration={editingIntegration}
              onSuccess={() => {
                setIsDialogOpen(false)
                setEditingIntegration(null)
              }}
              onCancel={() => {
                setIsDialogOpen(false)
                setEditingIntegration(null)
              }}
            />
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Google Calendar</CardTitle>
          <CardDescription>
            Sincronize agendamentos bidirecionalmente com o Google Calendar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
              <Globe className="h-6 w-6 text-blue-600" />
            </div>
            <div className="flex-1">
              <p className="font-medium">Integração Google Calendar</p>
              <p className="text-sm text-muted-foreground">
                {integrations.some(i => i.provider === "google_calendar")
                  ? "Conectado"
                  : "Não conectado"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Integrações Configuradas</CardTitle>
          <CardDescription>
            Gerencie suas integrações ativas
          </CardDescription>
        </CardHeader>
        <CardContent>
          <IntegrationList
            integrations={integrations}
            onEdit={(integration) => setEditingIntegration(integration)}
          />
        </CardContent>
      </Card>
    </div>
  )
}
