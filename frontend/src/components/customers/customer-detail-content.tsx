"use client"

import { ReactElement } from "react"
import { notFound } from "next/navigation"
import useSWR from "swr"
import { swrConfig, fetcher } from "@/lib/swr-config"
import { Customer, Appointment, TimelineEntry, InteractionType } from "@/types/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { CalendarDays, Phone, Mail, MapPin, FileText, Clock } from "lucide-react"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale/pt-BR"

const INTERACTION_ICONS: Record<InteractionType, ReactElement> = {
  call: <Phone className="h-4 w-4" />,
  email: <Mail className="h-4 w-4" />,
  visit: <CalendarDays className="h-4 w-4" />,
  note: <FileText className="h-4 w-4" />,
}

const APPOINTMENT_STATUS_LABELS = {
  scheduled: "Agendado",
  confirmed: "Confirmado",
  cancelled: "Cancelado",
  completed: "Concluído",
}

const APPOINTMENT_STATUS_COLORS = {
  scheduled: "secondary",
  confirmed: "default",
  cancelled: "destructive",
  completed: "outline",
} as const

interface CustomerDetailContentProps {
  customerId: string
}

export function CustomerDetailContent({ customerId }: CustomerDetailContentProps) {
  const { data: customer, error: customerError } = useSWR<Customer>(
    `/api/v1/customers/${customerId}`,
    fetcher,
    swrConfig
  )

  const { data: appointmentsData, error: appointmentsError } = useSWR<{
    count: number
    next: string | null
    previous: string | null
    results: Appointment[]
  }>(`/api/v1/customers/${customerId}/appointments`, fetcher, swrConfig)

  const { data: timelineData, error: timelineError } = useSWR<{
    count: number
    next: string | null
    previous: string | null
    results: TimelineEntry[]
  }>(`/api/v1/customers/${customerId}/timeline`, fetcher, swrConfig)

  if (customerError || appointmentsError || timelineError) {
    notFound()
  }

  if (!customer) {
    return (
      <div className="container mx-auto py-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">Carregando cliente...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const appointments = appointmentsData?.results ?? []
  const timeline = timelineData?.results ?? []

  const initials = customer.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)

  return (
    <div className="container mx-auto py-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{customer.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-start gap-6">
            <Avatar className="h-20 w-20">
              <AvatarImage src="" alt={customer.name} />
              <AvatarFallback className="text-lg">{initials}</AvatarFallback>
            </Avatar>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span>{customer.email ?? "—"}</span>
                </div>
                <div className="flex items-center gap-3">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <span>{customer.phone ?? "—"}</span>
                </div>
                {customer.document && (
                  <div className="flex items-center gap-3">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span>{customer.document}</span>
                  </div>
                )}
                {customer.birth_date && (
                  <div className="flex items-center gap-3">
                    <CalendarDays className="h-4 w-4 text-muted-foreground" />
                    <span>
                      {format(new Date(customer.birth_date), "dd/MM/yyyy", { locale: ptBR })}
                    </span>
                  </div>
                )}
              </div>

              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span>Endereço não cadastrado</span>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>
                    Cliente desde {format(new Date(customer.created_at), "dd/MM/yyyy", { locale: ptBR })}
                  </span>
                </div>
                {customer.lead_id && (
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">Lead #{customer.lead_id}</Badge>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Próximos Atendimentos</CardTitle>
          </CardHeader>
          <CardContent>
            {appointments.length === 0 ? (
              <p className="text-sm text-muted-foreground">Nenhum atendimento agendado.</p>
            ) : (
              <div className="space-y-3">
                {appointments.map((apt) => (
                  <div key={apt.id} className="border rounded-lg p-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{apt.service}</p>
                        <p className="text-sm text-muted-foreground">
                          {format(new Date(apt.start_time), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                        </p>
                      </div>
                      <Badge variant={APPOINTMENT_STATUS_COLORS[apt.status]}>
                        {APPOINTMENT_STATUS_LABELS[apt.status]}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Histórico de Atividades</CardTitle>
          </CardHeader>
          <CardContent>
            {timeline.length === 0 ? (
              <p className="text-sm text-muted-foreground">Nenhuma atividade registrada.</p>
            ) : (
              <div className="space-y-4">
                {timeline.map((entry) => (
                  <div key={entry.id} className="flex gap-3">
                    <div className="flex-shrink-0 mt-0.5">
                      {INTERACTION_ICONS[entry.kind]}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm">{entry.description}</p>
                      <p className="text-xs text-muted-foreground">
                        {format(new Date(entry.timestamp), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
