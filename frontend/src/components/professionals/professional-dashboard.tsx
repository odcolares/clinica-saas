"use client"

import useSWR from "swr"
import { fetcher, swrConfig } from "@/lib/swr-config"
import type { Appointment, CommissionEntry, ProfessionalDashboardStats } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { DollarSign, Calendar, CheckCircle, Clock, UserRound } from "lucide-react"
import { format, isSameDay } from "date-fns"
import { ptBR } from "date-fns/locale/pt-BR"
import { useMemo } from "react"

function useProfessionalStats(professionalId: string) {
  const { data, error, isLoading } = useSWR<{
    appointments: Appointment[]
    stats: ProfessionalDashboardStats
  }>(`/api/v1/professionals/${professionalId}/dashboard`, fetcher, swrConfig)

  return {
    data,
    isLoading,
    isError: !!error,
    error,
  }
}

interface ProfessionalDashboardProps {
  professionalId: string
}

export function ProfessionalDashboard({ professionalId }: ProfessionalDashboardProps) {
  const { data, isLoading, isError } = useProfessionalStats(professionalId)

  const today = useMemo(() => new Date(), [])

  const todayAppointments = useMemo(
    () => (data?.appointments || []).filter((a) =>
      isSameDay(new Date(a.start_time), today)
    ),
    [data?.appointments, today]
  )

  if (isLoading) {
    return (
      <div className="container mx-auto py-6 space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="container mx-auto py-6">
        <p className="text-center text-destructive">
          Erro ao carregar dados do profissional
        </p>
      </div>
    )
  }

  if (!data) return null

  const { stats } = data

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
          <UserRound className="h-8 w-4 text-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">{stats.professional_name}</h1>
          <p className="text-sm text-muted-foreground">Painel do Profissional</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Agendamentos</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total_appointments}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Concluídos</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.completed_appointments}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Hoje</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.today_appointments}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Comissões</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R${" "}
              {stats.recent_commissions?.reduce(
                (sum, c) => sum + c.commission_amount,
                0
              ).toFixed(2) ?? "0.00"}
            </div>
            <p className="text-xs text-muted-foreground">Total acumulado</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Agendamentos de Hoje</CardTitle>
          </CardHeader>
          <CardContent>
            {todayAppointments.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">
                Nenhum agendamento hoje
              </p>
            ) : (
              <div className="space-y-4">
                {todayAppointments.map((apt) => (
                  <div key={apt.id} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{apt.service}</p>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(apt.start_time), "HH:mm", { locale: ptBR })}
                      </p>
                    </div>
                    <Badge variant={apt.status === "confirmed" ? "default" : "secondary"}>
                      {apt.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Próximos Agendamentos</CardTitle>
          </CardHeader>
          <CardContent>
            {stats.upcoming_appointments.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">
                Nenhum agendamento futuro
              </p>
            ) : (
              <div className="space-y-4">
                {stats.upcoming_appointments.map((apt) => (
                  <div key={apt.id} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{apt.service}</p>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(apt.start_time), "PPp", { locale: ptBR })}
                      </p>
                    </div>
                    <Badge variant={apt.status === "confirmed" ? "default" : "secondary"}>
                      {apt.status}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {stats.recent_commissions && stats.recent_commissions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Histórico de Comissões</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats.recent_commissions.map((entry: CommissionEntry) => (
                <div
                  key={entry.appointment_id}
                  className="flex items-center justify-between"
                >
                  <div>
                    <p className="font-medium">{entry.service_name}</p>
                    <p className="text-sm text-muted-foreground">
                      {format(new Date(entry.date), "PP", { locale: ptBR })}
                    </p>
                  </div>
                  <Badge variant={entry.status === "completed" ? "default" : "secondary"}>
                    R$ {entry.commission_amount.toFixed(2)}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
