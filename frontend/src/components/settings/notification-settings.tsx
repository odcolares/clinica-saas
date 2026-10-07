"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, Bell, Save } from "lucide-react"
import { toast } from "sonner"
import type { NotificationSettings } from "@/types/api"
import { mutate } from "swr"

const NOTIFICATIONS_KEY = "/api/v1/settings/notifications"

interface NotificationSettingsFormProps {
  settings?: NotificationSettings
  onSuccess?: () => void
}

export function NotificationSettingsForm({ settings, onSuccess }: NotificationSettingsFormProps) {
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  const [localSettings, setLocalSettings] = useState<NotificationSettings>({
    appointment_confirmation: settings?.appointment_confirmation ?? true,
    appointment_reminder: settings?.appointment_reminder ?? true,
    appointment_reminder_time: settings?.appointment_reminder_time ?? 24,
    appointment_cancellation: settings?.appointment_cancellation ?? true,
    new_lead_alert: settings?.new_lead_alert ?? true,
    payment_received: settings?.payment_received ?? true,
    email_notifications: settings?.email_notifications ?? true,
    sms_notifications: settings?.sms_notifications ?? false,
    push_notifications: settings?.push_notifications ?? false,
  })

  const handleToggle = (key: keyof NotificationSettings) => {
    setLocalSettings((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  const handleReminderTimeChange = (value: number) => {
    setLocalSettings((prev) => ({
      ...prev,
      appointment_reminder_time: value,
    }))
  }

  const handleSubmit = async () => {
    setError(null)
    setIsSaving(true)

    try {
      const res = await fetch(NOTIFICATIONS_KEY, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(localSettings),
      })

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || "Falha ao salvar configurações de notificação")
      }

      mutate(NOTIFICATIONS_KEY)
      toast.success("Configurações de notificação atualizadas com sucesso!")
      onSuccess?.()
    } catch (err) {
      const message = err instanceof Error ? err.message : "Falha desconhecida"
      setError(message)
      toast.error(message)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <form onSubmit={(e) => e.preventDefault()}>
      <Card>
        <CardHeader>
          <CardTitle>Configurações de Notificação</CardTitle>
          <CardDescription>
            Configure como e quando você receberá notificações
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-sm font-medium">E-mail</h3>
            <div className="flex items-center justify-between">
              <Label htmlFor="email_notifications" className="text-sm">
                Ativar notificações por e-mail
              </Label>
              <Switch
                id="email_notifications"
                checked={localSettings.email_notifications}
                onCheckedChange={() => handleToggle("email_notifications")}
              />
            </div>

            <div className="space-y-4 pt-4 border-t">
              <h3 className="text-sm font-medium flex items-center gap-2">
                <Bell className="h-4 w-4" />
                Notificações de Agendamento
              </h3>

              <div className="flex items-center justify-between">
                <Label htmlFor="appointment_confirmation" className="text-sm">
                  Confirmação de agendamento
                </Label>
                <Switch
                  id="appointment_confirmation"
                  checked={localSettings.appointment_confirmation}
                  onCheckedChange={() => handleToggle("appointment_confirmation")}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="appointment_reminder" className="text-sm">
                  Lembrete de agendamento
                </Label>
                <Switch
                  id="appointment_reminder"
                  checked={localSettings.appointment_reminder}
                  onCheckedChange={() => handleToggle("appointment_reminder")}
                />
              </div>

              {localSettings.appointment_reminder && (
                <div className="flex items-center gap-2 ml-6">
                  <Input
                    type="number"
                    min={0}
                    max={168}
                    value={localSettings.appointment_reminder_time}
                    onChange={(e) =>
                      handleReminderTimeChange(Number(e.target.value))
                    }
                    className="w-20"
                  />
                  <Label className="text-sm">minutos antes</Label>
                </div>
              )}

              <div className="flex items-center justify-between">
                <Label htmlFor="appointment_cancellation" className="text-sm">
                  Cancelamento de agendamento
                </Label>
                <Switch
                  id="appointment_cancellation"
                  checked={localSettings.appointment_cancellation}
                  onCheckedChange={() => handleToggle("appointment_cancellation")}
                />
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t">
              <h3 className="text-sm font-medium">Outras Notificações</h3>

              <div className="flex items-center justify-between">
                <Label htmlFor="new_lead_alert" className="text-sm">
                  Novo lead
                </Label>
                <Switch
                  id="new_lead_alert"
                  checked={localSettings.new_lead_alert}
                  onCheckedChange={() => handleToggle("new_lead_alert")}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="payment_received" className="text-sm">
                  Pagamento recebido
                </Label>
                <Switch
                  id="payment_received"
                  checked={localSettings.payment_received}
                  onCheckedChange={() => handleToggle("payment_received")}
                />
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t">
              <h3 className="text-sm font-medium">Canais Alternativos</h3>

              <div className="flex items-center justify-between">
                <Label htmlFor="sms_notifications" className="text-sm">
                  Notificações por SMS
                </Label>
                <Switch
                  id="sms_notifications"
                  checked={localSettings.sms_notifications}
                  onCheckedChange={() => handleToggle("sms_notifications")}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="push_notifications" className="text-sm">
                  Notificações push
                </Label>
                <Switch
                  id="push_notifications"
                  checked={localSettings.push_notifications}
                  onCheckedChange={() => handleToggle("push_notifications")}
                />
              </div>
            </div>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardContent>
          <Button onClick={handleSubmit} disabled={isSaving}>
            {isSaving ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Salvando...
              </>
            ) : (
              <>
                <Save className="mr-2 h-4 w-4" />
                Salvar Configurações
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </form>
  )
}
