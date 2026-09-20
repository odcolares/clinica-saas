"use client"

import { useState } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Suspense } from "react"
import { AppointmentCalendar, AppointmentCalendarLegend } from "@/components/appointments/appointment-calendar"
import { NewAppointmentForm } from "@/components/appointments/new-appointment-form"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Plus, Calendar } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export default function AppointmentsPage() {
  return (
    <Suspense fallback={<div className="container mx-auto py-6">Carregando agendamentos...</div>}>
      <AppointmentsContent />
    </Suspense>
  )
}

function AppointmentsContent() {
  const searchParams = useSearchParams()
  const router = useRouter()

  const professionalFilter = searchParams.get("professional") ?? ""
  const [dialogOpen, setDialogOpen] = useState(false)

  const handleNewAppointment = () => {
    setDialogOpen(true)
  }

  const handleAppointmentCreated = () => {
    setDialogOpen(false)
    router.refresh()
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Agendamentos</h1>
          <p className="text-sm text-muted-foreground">Gerencie a agenda da clínica</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={handleNewAppointment}>
              <Plus className="mr-2 h-4 w-4" />
              Novo Agendamento
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Novo Agendamento</DialogTitle>
              <DialogDescription>Preencha os dados do agendamento</DialogDescription>
            </DialogHeader>
            <NewAppointmentForm onSuccess={handleAppointmentCreated} />
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 space-y-6">
          <AppointmentCalendar professionalId={professionalFilter || undefined} />
        </div>
        <div className="lg:col-span-1 space-y-6">
          <AppointmentCalendarLegend />
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Ações Rápidas
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full justify-start" onClick={handleNewAppointment}>
                <Plus className="mr-2 h-4 w-4" />
                Novo Agendamento
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Calendar className="mr-2 h-4 w-4" />
                Ver Hoje
              </Button>
              <Button variant="outline" className="w-full justify-start">
                Ver Semana
              </Button>
              <Button variant="outline" className="w-full justify-start">
                Ver Mês
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}