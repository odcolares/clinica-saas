"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock } from "lucide-react"
import { addMonths, format, startOfMonth, endOfMonth, startOfWeek, addDays } from "date-fns"
import { ptBR } from "date-fns/locale/pt-BR"
import { Appointment, Professional, Service, Customer } from "@/types/api"
import { appointments, professionals, services, customers } from "@/mocks/data"

const DAYS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
const today = new Date("2025-09-19")

export function CalendarView() {
  const [currentDate, setCurrentDate] = useState(today)

  const monthStart = startOfMonth(currentDate)
  const monthEnd = endOfMonth(currentDate)
  const startDate = startOfWeek(monthStart, { locale: ptBR, weekStartsOn: 0 })

  const days = []
  let date = startDate
  while (date <= monthEnd) {
    days.push(date)
    date = addDays(date, 1)
  }

  const monthAppointments = appointments.filter((a) =>
    a.start_time.startsWith(format(currentDate, "yyyy-MM"))
  )

  const appointmentsByDate = useMemo(() => {
    const map: Record<string, Appointment[]> = {}
    monthAppointments.forEach((apt) => {
      const day = apt.start_time.split("T")[0]
      if (!map[day]) map[day] = []
      map[day].push(apt)
    })
    return map
  }, [monthAppointments])

  const prevMonth = () => setCurrentDate(addMonths(currentDate, -1))
  const nextMonth = () => setCurrentDate(addMonths(currentDate, 1))

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">
          {format(currentDate, "MMMM yyyy", { locale: ptBR })}
        </h2>
        <div className="flex gap-2">
          <button
            onClick={prevMonth}
            className="rounded-md p-2 hover:bg-accent"
            aria-label="Mês anterior"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            onClick={() => setCurrentDate(today)}
            className="rounded-md p-2 hover:bg-accent"
            aria-label="Hoje"
          >
            Hoje
          </button>
          <button
            onClick={nextMonth}
            className="rounded-md p-2 hover:bg-accent"
            aria-label="Próximo mês"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1 text-center text-xs font-medium text-muted-foreground">
        {DAYS.map((day) => (
          <div key={day}>{day}</div>
        ))}
      </div>

      {days.map((date, i) => {
        const dateStr = format(date, "yyyy-MM-dd")
        const dayAppointments = appointmentsByDate[dateStr] || []
        const isCurrentMonth = date.getMonth() === currentDate.getMonth()
        const isToday = format(date, "yyyy-MM-dd") === format(today, "yyyy-MM-dd")

        return (
          <div
            key={date.toISOString()}
            className="relative min-h-[60px] border-t border-l first:border-t-0"
          >
            <div
              className={
                "absolute top-1 left-1 text-sm" +
                (isToday ? " rounded-full bg-primary text-primary-foreground w-6 h-6 flex items-center justify-center" : "") +
                (!isCurrentMonth ? " text-muted-foreground/30" : "")
              }
            >
              {format(date, "d")}
            </div>
            {dayAppointments.length > 0 && (
              <div className="absolute top-6 left-1 w-full space-y-1">
                {dayAppointments.slice(0, 2).map((apt) => {
                  const prof = professionals.find((p) => p.id === apt.professional)
                  return (
                    <div
                      key={apt.id}
                      className="text-xs truncate rounded bg-blue-100 px-1 py-0.5"
                      title={`${apt.customer} - ${prof?.name || apt.professional}`}
                    >
                      {apt.customer}
                    </div>
                  )
                })}
                {dayAppointments.length > 2 && (
                  <div className="text-xs text-muted-foreground">
                    +{dayAppointments.length - 2} mais
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export function CalendarPageContent() {
  return (
    <div className="container mx-auto py-6 space-y-4">
      <div className="flex items-center gap-2">
        <CalendarIcon className="h-6 w-6" />
        <h1 className="text-2xl font-bold">Calendário</h1>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Agendamentos</CardTitle>
        </CardHeader>
        <CardContent>
          <CalendarView />
        </CardContent>
      </Card>
    </div>
  )
}

// Re-export types for convenience
export type { Appointment, Professional, Service, Customer, Clock }
