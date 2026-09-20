"use client"

import { useState } from "react"
import { format, parseISO } from "date-fns"
import { ptBR } from "date-fns/locale/pt-BR"
import { useProfessionalAvailability } from "@/hooks/use-appointments"
import { useProfessionals } from "@/hooks/use-appointments"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Calendar, Clock, UserCheck, UserX, ChevronLeft, ChevronRight } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface ProfessionalAvailabilityProps {
  selectedDate?: string
  onDateChange?: (date: string) => void
  onSlotSelect?: (professionalId: string, slot: { start: string; end: string }) => void
}

export function ProfessionalAvailability({
  selectedDate = format(new Date(), "yyyy-MM-dd"),
  onDateChange,
  onSlotSelect,
}: ProfessionalAvailabilityProps) {
  const [viewDate, setViewDate] = useState(selectedDate)
  const { professionals } = useProfessionals()
  const { availability, isLoading, isError, error } = useProfessionalAvailability({
    date: viewDate,
  })

  const handlePrevDay = () => {
    const newDate = format(new Date(new Date(viewDate).setDate(new Date(viewDate).getDate() - 1)), "yyyy-MM-dd")
    setViewDate(newDate)
    onDateChange?.(newDate)
  }

  const handleNextDay = () => {
    const newDate = format(new Date(new Date(viewDate).setDate(new Date(viewDate).getDate() + 1)), "yyyy-MM-dd")
    setViewDate(newDate)
    onDateChange?.(newDate)
  }

  const handleToday = () => {
    const today = format(new Date(), "yyyy-MM-dd")
    setViewDate(today)
    onDateChange?.(today)
  }

  const getAvailableSlots = (slots: { start: string; end: string; available: boolean }[]) => {
    return slots.filter((s) => s.available)
  }

  const getBookedSlots = (slots: { start: string; end: string; available: boolean }[]) => {
    return slots.filter((s) => !s.available)
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8 text-center">
          <div className="text-muted-foreground">Carregando disponibilidade...</div>
        </CardContent>
      </Card>
    )
  }

  if (isError) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-destructive">
          Erro ao carregar disponibilidade: {error?.message}
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={handlePrevDay}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={handleToday}>
            <Calendar className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={handleNextDay}>
            <ChevronRight className="h-4 w-4" />
          </Button>
          <div className="px-4">
            <span className="font-medium">
              {format(parseISO(viewDate), "EEEE, dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
            </span>
          </div>
          <Button variant="outline" size="icon" onClick={handleNextDay}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {availability.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            <p>Nenhum profissional com disponibilidade cadastrada para esta data.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {availability.map((prof) => {
            const availableSlots = getAvailableSlots(prof.slots)
            const bookedSlots = getBookedSlots(prof.slots)

            return (
              <Card key={prof.professional} className="overflow-hidden">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <span className="text-primary font-medium">
                          {prof.professional_name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-semibold">{prof.professional_name}</h3>
                        <p className="text-sm text-muted-foreground">
                          {availableSlots.length} horários livres · {bookedSlots.length} ocupados
                        </p>
                      </div>
                    </div>
                    <Badge variant="secondary" className="bg-green-100 text-green-800">
                      {availableSlots.length} disponíveis
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                    {prof.slots.map((slot) => (
                      <Button
                        key={`${prof.professional}-${slot.start}`}
                        variant={slot.available ? "outline" : "secondary"}
                        className={`h-10 w-full text-xs ${slot.available ? "bg-white hover:bg-green-50 border-green-200 text-green-700" : "bg-gray-100 text-gray-500 cursor-not-allowed"}`}
                        disabled={!slot.available}
                        onClick={() => slot.available && onSlotSelect?.(prof.professional, slot)}
                      >
                        <div className="flex flex-col items-center">
                          <span className="font-medium">
                            {format(parseISO(slot.start), "HH:mm", { locale: ptBR })}
                          </span>
                          <span className="text-[10px] text-muted-foreground">
                            {format(parseISO(slot.start), "HH:mm", { locale: ptBR })} -{" "}
                            {format(parseISO(slot.end), "HH:mm", { locale: ptBR })}
                          </span>
                        </div>
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}

export function ProfessionalAvailabilitySelector({
  date,
  onSelect,
}: {
  date: string
  onSelect: (professionalId: string, slot: { start: string; end: string }) => void
}) {
  const { professionals } = useProfessionals()
  const { availability, isLoading } = useProfessionalAvailability({ date })

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Carregando profissionais...</div>
  }

  return (
    <div className="space-y-4">
      <h3 className="font-semibold">Selecione o profissional e horário</h3>
      {availability.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          Nenhum profissional disponível para esta data.
        </div>
      )}
      <div className="grid gap-4 md:grid-cols-2">
        {availability.map((prof) => {
          const availableSlots = prof.slots.filter((s) => s.available)
          return (
            <Card key={prof.professional}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{prof.professional_name}</CardTitle>
                <p className="text-sm text-muted-foreground">
                  {availableSlots.length} horários disponíveis
                </p>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {availableSlots.map((slot) => (
                    <Button
                      key={`${prof.professional}-${slot.start}`}
                      variant="outline"
                      size="sm"
                      className="h-8 px-3"
                      onClick={() => onSelect(prof.professional, slot)}
                    >
                      {format(parseISO(slot.start), "HH:mm", { locale: ptBR })}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}