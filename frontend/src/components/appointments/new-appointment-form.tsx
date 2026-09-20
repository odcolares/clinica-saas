"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, CalendarIcon } from "lucide-react"
import { customers, professionals, services } from "@/mocks/data"

const appointmentSchema = z.object({
  customer: z.string().min(1, "Cliente é obrigatório"),
  professional: z.string().min(1, "Profissional é obrigatório"),
  service: z.string().min(1, "Serviço é obrigatório"),
  start_time: z.string().min(1, "Data e hora são obrigatórias"),
  notes: z.string().optional(),
})

type AppointmentFormValues = z.infer<typeof appointmentSchema>

export function NewAppointmentForm() {
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<AppointmentFormValues>({
    resolver: zodResolver(appointmentSchema),
  })

  const onSubmit = async (data: AppointmentFormValues) => {
    setError(null)
    setSuccess(false)

    try {
      const res = await fetch("/api/v1/appointments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })

      if (!res.ok) {
        const errorData = await res.json()
        setError(errorData.detail || "Falha ao criar agendamento")
        return
      }

      setSuccess(true)
    } catch (err) {
      setError("Falha na conexão")
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Novo Agendamento</CardTitle>
          <CardDescription>Preencha os dados do agendamento</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="customer">Cliente</Label>
            <Select onValueChange={(val) => register("customer").onChange({ target: { value: val } })}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione um cliente" />
              </SelectTrigger>
              <SelectContent>
                {customers.map((c) => (
                  <SelectItem key={c.id} value={c.id}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <input type="hidden" {...register("customer")} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="professional">Profissional</Label>
            <Select onValueChange={(val) => register("professional").onChange({ target: { value: val } })}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione um profissional" />
              </SelectTrigger>
              <SelectContent>
                {professionals.map((p) => (
                  <SelectItem key={p.id} value={p.id}>
                    {p.name} - {p.specialty}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <input type="hidden" {...register("professional")} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="service">Serviço</Label>
            <Select onValueChange={(val) => register("service").onChange({ target: { value: val } })}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione um serviço" />
              </SelectTrigger>
              <SelectContent>
                {services.map((s) => (
                  <SelectItem key={s.id} value={s.id}>
                    {s.name} - R$ {s.price.toFixed(2)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <input type="hidden" {...register("service")} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="start_time">Data e Hora</Label>
            <div className="relative">
              <Input
                id="start_time"
                type="datetime-local"
                {...register("start_time")}
              />
              <CalendarIcon className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Observações</Label>
            <Textarea
              id="notes"
              placeholder="Observações sobre o agendamento..."
              rows={3}
              {...register("notes")}
            />
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert>
              <AlertDescription>Agendamento criado com sucesso!</AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardFooter>
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Salvando...
              </>
            ) : (
              "Criar Agendamento"
            )}
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
