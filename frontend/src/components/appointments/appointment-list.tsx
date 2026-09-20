"use client"

import { useAppointments, useProfessionals, useServices, cancelAppointment, confirmAppointment } from "@/hooks/use-appointments"
import type { Appointment } from "@/types/api"
import { useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Clock, User, UserRound, CheckCircle, XCircle, Loader2 } from "lucide-react"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale/pt-BR"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"

const STATUS_LABELS: Record<string, string> = {
  scheduled: "Agendado",
  confirmed: "Confirmado",
  cancelled: "Cancelado",
  completed: "Concluído",
}

const STATUS_COLORS: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-800",
  confirmed: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-800",
  completed: "bg-gray-100 text-gray-800",
}

export function AppointmentList({
  professionalId,
}: {
  professionalId?: string
}) {
  const { appointments, isLoading, isError, error } = useAppointments({
    professional: professionalId,
  })
  const { professionals } = useProfessionals()
  const { services } = useServices()

  const enrichedAppointments = useMemo(() => {
    return appointments.map((apt) => ({
      ...apt,
      professionalName: professionals.find((p) => p.id === apt.professional)?.name ?? apt.professional,
      serviceName: services.find((s) => s.id === apt.service)?.name ?? apt.service,
    }))
  }, [appointments, professionals, services])

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Carregando agendamentos...</div>
  }

  if (isError) {
    return <div className="text-center py-8 text-destructive">Erro ao carregar agendamentos: {error?.message}</div>
  }

  if (appointments.length === 0) {
    return <div className="text-center py-8 text-muted-foreground">Nenhum agendamento encontrado.</div>
  }

  return (
    <div className="space-y-4">
      {enrichedAppointments.map((apt) => (
        <AppointmentCard
          key={apt.id}
          appointment={apt}
          professionalName={apt.professionalName}
          serviceName={apt.serviceName}
        />
      ))}
    </div>
  )
}

interface AppointmentCardProps {
  appointment: Appointment & { professionalName: string; serviceName: string }
  professionalName: string
  serviceName: string
}

function AppointmentCard({ appointment, professionalName, serviceName }: AppointmentCardProps) {
  const status = appointment.status
  const statusClass = STATUS_COLORS[status] ?? "bg-gray-100 text-gray-800"
  const statusLabel = STATUS_LABELS[status] ?? status
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const canConfirm = status === "scheduled"
  const canCancel = status === "scheduled" || status === "confirmed"

  const handleConfirm = async () => {
    setActionLoading("confirm")
    try {
      await confirmAppointment(appointment.id)
      toast.success("Agendamento confirmado com sucesso!")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao confirmar agendamento")
    } finally {
      setActionLoading(null)
    }
  }

  const handleCancel = async () => {
    setActionLoading("cancel")
    try {
      await cancelAppointment(appointment.id)
      toast.success("Agendamento cancelado com sucesso!")
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao cancelar agendamento")
    } finally {
      setActionLoading(null)
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{serviceName}</CardTitle>
          <Badge className={statusClass}>{statusLabel}</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm">
            {format(new Date(appointment.start_time), "PPp", { locale: ptBR })}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <User className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm">Cliente: {appointment.customer}</span>
        </div>
        <div className="flex items-center gap-2">
          <UserRound className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm">Profissional: {professionalName}</span>
        </div>
        {appointment.notes && <p className="text-sm text-muted-foreground">{appointment.notes}</p>}
        {(canConfirm || canCancel) && (
          <div className="flex gap-2 pt-2 border-t">
            {canConfirm && (
              <Button
                variant="default"
                size="sm"
                className="flex-1"
                onClick={handleConfirm}
                disabled={actionLoading !== null}
              >
                {actionLoading === "confirm" ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Confirmando...
                  </>
                ) : (
                  <>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Confirmar
                  </>
                )}
              </Button>
            )}
            {canCancel && (
              <Button
                variant="destructive"
                size="sm"
                className="flex-1"
                onClick={handleCancel}
                disabled={actionLoading !== null}
              >
                {actionLoading === "cancel" ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Cancelando...
                  </>
                ) : (
                  <>
                    <XCircle className="mr-2 h-4 w-4" />
                    Cancelar
                  </>
                )}
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
