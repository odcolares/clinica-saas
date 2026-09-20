"use client"

import { useAppointments, useProfessionals, useServices } from "@/hooks/use-appointments"
import type { Appointment } from "@/types/api"
import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Clock, User, UserRound } from "lucide-react"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale/pt-BR"

const STATUS_LABELS: Record<string, string> = {
  agendado: "Agendado",
  confirmado: "Confirmado",
  cancelado: "Cancelado",
  concluido: "Concluído",
}

const STATUS_COLORS: Record<string, string> = {
  agendado: "bg-blue-100 text-blue-800",
  confirmado: "bg-green-100 text-green-800",
  cancelado: "bg-red-100 text-red-800",
  concluido: "bg-gray-100 text-gray-800",
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
      </CardContent>
    </Card>
  )
}
