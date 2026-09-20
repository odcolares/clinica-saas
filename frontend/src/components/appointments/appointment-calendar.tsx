"use client"

import { useMemo } from "react"
import FullCalendar from "@fullcalendar/react"
import dayGridPlugin from "@fullcalendar/daygrid"
import timeGridPlugin from "@fullcalendar/timegrid"
import interactionPlugin from "@fullcalendar/interaction"
import listPlugin from "@fullcalendar/list"
import ptBrLocale from "@fullcalendar/react/locales/pt-br"
import { Calendar, Clock, User, UserRound, ChevronLeft, ChevronRight } from "lucide-react"
import { useAppointments, useProfessionals, useServices } from "@/hooks/use-appointments"
import type { Appointment } from "@/types/api"
import { Badge } from "@/components/ui/badge"

import { format } from "date-fns"
import { ptBR } from "date-fns/locale/pt-BR"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const STATUS_LABELS: Record<string, string> = {
  scheduled: "Agendado",
  confirmed: "Confirmado",
  cancelled: "Cancelado",
  completed: "Concluído",
}

const STATUS_COLORS: Record<string, string> = {
  scheduled: "bg-blue-500",
  confirmed: "bg-green-500",
  cancelled: "bg-red-500",
  completed: "bg-gray-500",
}

const STATUS_BADGE_COLORS: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-800",
  confirmed: "bg-green-100 text-green-800",
  cancelled: "bg-red-100 text-red-800",
  completed: "bg-gray-100 text-gray-800",
}

interface AppointmentCalendarProps {
  professionalId?: string
  onAppointmentClick?: (appointment: Appointment & { professionalName: string; serviceName: string }) => void
}

export function AppointmentCalendar({ professionalId, onAppointmentClick }: AppointmentCalendarProps) {
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

  const events = useMemo(() => {
    return enrichedAppointments.map((apt) => ({
      id: apt.id,
      title: `${apt.serviceName} - ${apt.professionalName}`,
      start: apt.start_time,
      end: apt.end_time,
      backgroundColor: STATUS_COLORS[apt.status] ?? "#6b7280",
      borderColor: STATUS_COLORS[apt.status] ?? "#6b7280",
      extendedProps: {
        status: apt.status,
        customer: apt.customer,
        professionalName: apt.professionalName,
        serviceName: apt.serviceName,
        notes: apt.notes,
      },
    }))
  }, [enrichedAppointments])

  const professionalOptions = useMemo(() => [
    { value: "", label: "Todos os profissionais" },
    ...professionals.map((p) => ({ value: p.id, label: p.name })),
  ], [professionals])

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <div className="text-muted-foreground">Carregando calendário...</div>
        </CardContent>
      </Card>
    )
  }

  if (isError) {
    return (
      <Card>
        <CardContent className="py-12 text-center text-destructive">
          Erro ao carregar agendamentos: {error?.message}
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Calendário de Agendamentos</h2>
          <p className="text-sm text-muted-foreground">
            {enrichedAppointments.length} agendamento{enrichedAppointments.length !== 1 ? "s" : ""}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
          <Select value={professionalId ?? ""} onValueChange={(v) => { window.location.href = v ? `/appointments?professional=${v}` : "/appointments" }}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Filtrar por profissional" />
            </SelectTrigger>
            <SelectContent>
              {professionalOptions.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card>
        <CardContent className="p-0">
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin]}
            initialView="timeGridWeek"
            locale={ptBrLocale}
            headerToolbar={{
              left: "prev,next today",
              center: "title",
              right: "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
            }}
            events={events}
            slotMinTime="07:00:00"
            slotMaxTime="20:00:00"
            slotDuration="00:30:00"
            allDaySlot={false}
            height="auto"
            eventTimeFormat={{
              hour: "2-digit",
              minute: "2-digit",
              meridiem: false,
              hour12: false,
            }}
            eventDisplay="block"
            eventContent={(eventInfo) => (
              <div className="p-1 overflow-hidden">
                <div className="font-medium text-xs truncate">{eventInfo.timeText} {eventInfo.event.title}</div>
                <div className="text-xs opacity-90 truncate">
                  {eventInfo.event.extendedProps.professionalName}
                </div>
              </div>
            )}
            eventClick={(info) => {
              const apt = enrichedAppointments.find((a) => a.id === info.event.id)
              if (apt && onAppointmentClick) {
                onAppointmentClick(apt)
              }
            }}
            dayHeaderFormat={{ weekday: "short" }}
            dayMaxEvents={3}
            moreLinkClick="popover"
            selectable={false}
            selectMirror={false}
            weekends={true}
            nowIndicator={true}
          />
        </CardContent>
      </Card>

      {enrichedAppointments.length === 0 && (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Nenhum agendamento encontrado.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export function AppointmentCalendarLegend() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Legenda de Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-4">
          {Object.entries(STATUS_LABELS).map(([status, label]) => (
            <div key={status} className="flex items-center gap-2">
              <Badge variant="secondary" className={STATUS_BADGE_COLORS[status]}>
                {label}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}