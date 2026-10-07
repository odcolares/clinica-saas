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
import { Loader2, Upload, Palette } from "lucide-react"
import { toast } from "sonner"
import type { TenantSettings, TenantSettingsUpdateRequest } from "@/types/api"
import { updateTenantSettings } from "@/hooks/use-tenant-settings"

const tenantSettingsSchema = z.object({
  business_start: z.string().min(1, "Horário de abertura é obrigatório"),
  business_end: z.string().min(1, "Horário de fechamento é obrigatório"),
  timezone: z.string().min(1, "Fuso horário é obrigatório"),
  brand_name: z.string().min(1, "Nome da marca é obrigatório"),
  primary_color: z.string().min(1, "Cor primária é obrigatória"),
  logo_url: z.string().url("URL inválida").optional(),
})

type TenantSettingsFormValues = z.infer<typeof tenantSettingsSchema>

const TIMEZONES = [
  "America/Sao_Paulo",
  "America/Bahia",
  "America/Fortaleza",
  "America/Manaus",
  "America/Argentina/Buenos_Aires",
  "Europe/Lisbon",
  "UTC",
]

interface TenantSettingsFormProps {
  settings?: TenantSettings | null
  onSuccess?: () => void
}

export function TenantSettingsForm({ settings, onSuccess }: TenantSettingsFormProps) {
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<TenantSettingsFormValues>({
    resolver: zodResolver(tenantSettingsSchema),
    defaultValues: {
      business_start: settings?.business_start ?? "08:00",
      business_end: settings?.business_end ?? "18:00",
      timezone: settings?.timezone ?? "America/Sao_Paulo",
      brand_name: settings?.brand_name ?? "",
      primary_color: settings?.primary_color ?? "#0F766E",
      logo_url: settings?.logo_url ?? "",
    },
  })

  const onSubmit = async (data: TenantSettingsFormValues) => {
    setError(null)

    try {
      await updateTenantSettings(data as TenantSettingsUpdateRequest)
      toast.success("Configurações atualizadas com sucesso!")
      onSuccess?.()
    } catch (err) {
      const message = err instanceof Error ? err.message : "Falha ao atualizar configurações"
      setError(message)
      toast.error(message)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card>
        <CardHeader>
          <CardTitle>Configurações do Tenant</CardTitle>
          <CardDescription>Configure os horários de funcionamento e identidade visual</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="brand_name">Nome da Marca</Label>
            <Input
              id="brand_name"
              placeholder="Clínica Saúde"
              {...register("brand_name")}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="logo_url">URL do Logo</Label>
            <div className="relative">
              <Input
                id="logo_url"
                type="url"
                placeholder="https://exemplo.com/logo.png"
                {...register("logo_url")}
              />
              <Upload className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="business_start">Horário de Abertura</Label>
              <Input
                id="business_start"
                type="time"
                {...register("business_start")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="business_end">Horário de Fechamento</Label>
              <Input
                id="business_end"
                type="time"
                {...register("business_end")}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="timezone">Fuso Horário</Label>
            <Select
              onValueChange={(val) =>
                register("timezone").onChange({ target: { value: val } })
              }
              defaultValue={settings?.timezone ?? "America/Sao_Paulo"}
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione o fuso horário" />
              </SelectTrigger>
              <SelectContent>
                {TIMEZONES.map((tz) => (
                  <SelectItem key={tz} value={tz}>
                    {tz}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <input type="hidden" {...register("timezone")} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="primary_color">Cor Primária</Label>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Palette className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="primary_color"
                  type="color"
                  className="w-12 h-10 p-1"
                  {...register("primary_color")}
                />
              </div>
              <Input
                placeholder="#0F766E"
                {...register("primary_color")}
              />
            </div>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardContent>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Salvando...
              </>
            ) : (
              "Salvar Configurações"
            )}
          </Button>
        </CardContent>
      </Card>
    </form>
  )
}
