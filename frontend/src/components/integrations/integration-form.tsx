"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, Globe, Save, Trash2 } from "lucide-react"
import { toast } from "sonner"
import type { IntegrationConfig, IntegrationProvider } from "@/types/api"
import { createIntegration, updateIntegration, deleteIntegration } from "@/hooks/use-integrations"
import { mutate } from "swr"

const INTEGRATIONS_KEY = "/api/v1/settings/integrations"

const integrationSchema = z.object({
  provider: z.enum(["noop", "google_calendar"]),
  professional_email: z.string().email("E-mail inválido").optional(),
  config: z.record(z.unknown()),
})

type IntegrationFormValues = z.infer<typeof integrationSchema>

interface IntegrationFormProps {
  integration?: IntegrationConfig | null
  onSuccess?: () => void
  onCancel?: () => void
}

const PROVIDER_LABELS: Record<IntegrationProvider, string> = {
  noop: "Nenhuma",
  google_calendar: "Google Calendar",
}

export function IntegrationForm({ integration, onSuccess, onCancel }: IntegrationFormProps) {
  const [error, setError] = useState<string | null>(null)
  const isEditing = !!integration

  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
    watch,
    setValue,
  } = useForm<IntegrationFormValues>({
    resolver: zodResolver(integrationSchema),
    defaultValues: {
      provider: integration?.provider ?? "google_calendar",
      professional_email: integration?.professional_email ?? "",
      config: integration?.config ?? {},
    },
  })

  const provider = watch("provider")

  const onSubmit = async (data: IntegrationFormValues) => {
    setError(null)

    try {
      if (isEditing && integration) {
        await updateIntegration(integration.id, data)
        toast.success("Integração atualizada com sucesso!")
      } else {
        await createIntegration(data)
        toast.success("Integração criada com sucesso!")
      }
      mutate(INTEGRATIONS_KEY)
      onSuccess?.()
    } catch (err) {
      const message = err instanceof Error ? err.message : "Falha ao salvar integração"
      setError(message)
      toast.error(message)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="provider">Provedor</Label>
        <Select
          value={provider}
          onValueChange={(val) => setValue("provider", val as IntegrationProvider)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Selecione o provedor" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="google_calendar">Google Calendar</SelectItem>
            <SelectItem value="noop">Nenhuma (desativar)</SelectItem>
          </SelectContent>
        </Select>
        <input type="hidden" {...register("provider")} />
      </div>

      {provider === "google_calendar" && (
        <>
          <div className="space-y-2">
            <Label htmlFor="professional_email">E-mail do Profissional</Label>
            <Input
              id="professional_email"
              type="email"
              placeholder="profissional@clinica.com"
              {...register("professional_email")}
            />
          </div>
          <Alert>
            <Globe className="h-4 w-4" />
            <AlertDescription>
              Clique no botão abaixo para autorizar a conexão com o Google Calendar.
              Uma janela de autorização será aberta.
            </AlertDescription>
          </Alert>
        </>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="flex gap-2">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Salvando...
            </>
          ) : (
            <>
              <Save className="mr-2 h-4 w-4" />
              {isEditing ? "Atualizar" : "Criar"} Integração
            </>
          )}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancelar
          </Button>
        )}
      </div>
    </form>
  )
}

interface IntegrationListProps {
  integrations: IntegrationConfig[]
  onEdit: (integration: IntegrationConfig) => void
}

export function IntegrationList({ integrations, onEdit }: IntegrationListProps) {
  const handleDelete = async (id: string, provider: string) => {
    if (!confirm(`Excluir integração ${PROVIDER_LABELS[provider as IntegrationProvider]}?`))
      return

    try {
      await deleteIntegration(id)
      toast.success("Integração excluída com sucesso!")
    } catch (err) {
      const message = err instanceof Error ? err.message : "Falha ao excluir integração"
      toast.error(message)
    }
  }

  if (integrations.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground py-8">
            Nenhuma integração configurada. Crie uma integração para começar.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {integrations.map((integration) => (
        <Card key={integration.id}>
          <CardHeader className="flex flex-row items-center justify-between">
            <div className="space-y-1">
              <CardTitle>{PROVIDER_LABELS[integration.provider]}</CardTitle>
              <CardDescription>
                Email profissional: {integration.professional_email || "Não configurado"}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onEdit(integration)}
              >
                Editar
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="text-destructive"
                onClick={() => handleDelete(integration.id, integration.provider)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div
                className={`h-3 w-3 rounded-full ${integration.active ? "bg-green-500" : "bg-gray-400"}`}
              />
              <span className="text-sm text-muted-foreground">
                {integration.active ? "Ativo" : "Inativo"}
              </span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
