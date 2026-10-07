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
import { Switch } from "@/components/ui/switch"
import { Loader2 } from "lucide-react"
import { toast } from "sonner"
import type { Professional } from "@/types/api"
import { createProfessional, updateProfessional } from "@/hooks/use-professionals"

const professionalSchema = z.object({
  name: z.string().min(1, "Nome é obrigatório"),
  email: z.string().email("E-mail inválido").optional().or(z.literal("")),
  phone: z.string().optional(),
  specialties: z.string().min(1, "Especialidade é obrigatória"),
  active: z.boolean().default(true),
  commission_type: z.enum(["none", "percent", "fixed"]).default("none"),
  commission_percent: z.number().min(0).max(100).optional(),
  commission_fixed: z.number().min(0).optional(),
})

type ProfessionalFormValues = z.infer<typeof professionalSchema>

interface ProfessionalFormProps {
  professional?: Professional | null
  onSuccess?: () => void
}

export function ProfessionalForm({ professional, onSuccess }: ProfessionalFormProps) {
  const [error, setError] = useState<string | null>(null)
  const isEditing = !!professional

  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
    watch,
    setValue,
  } = useForm<ProfessionalFormValues>({
    resolver: zodResolver(professionalSchema),
    defaultValues: {
      name: professional?.name ?? "",
      email: professional?.email ?? "",
      phone: professional?.phone ?? "",
      specialties: professional?.specialties ?? "",      active: professional?.active ?? true,
      commission_type: professional?.commission_type ?? "none",
      commission_percent: professional?.commission_percent ?? undefined,
      commission_fixed: professional?.commission_fixed ?? undefined,
    },
  })

  const commissionType = watch("commission_type")

  const onSubmit = async (data: ProfessionalFormValues) => {
    setError(null)

    try {
      if (isEditing && professional) {
        await updateProfessional(professional.id, data)
        toast.success("Profissional atualizado com sucesso!")
      } else {
        await createProfessional(data)
        toast.success("Profissional criado com sucesso!")
      }
      onSuccess?.()
    } catch (err) {
      const message = err instanceof Error ? err.message : "Falha ao salvar profissional"
      setError(message)
      toast.error(message)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>{isEditing ? "Editar Profissional" : "Novo Profissional"}</CardTitle>
          <CardDescription>Preencha os dados do profissional</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Nome *</Label>
            <Input
              id="name"
              placeholder="Nome completo"
              {...register("name")}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                type="email"
                placeholder="email@exemplo.com"
                {...register("email")}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Telefone</Label>
              <Input
                id="phone"
                placeholder="(11) 98765-4321"
                {...register("phone")}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="specialties">Especialidades</Label>
            <Textarea
              id="specialties"
              placeholder="Ex: Odontologia, Ortodontia, Estética Dental (separe por vírgula)"
              {...register("specialties")}
            />
          </div>

          <div className="flex items-center justify-between space-x-2">
            <Label htmlFor="active">Ativo</Label>
            <Switch
              id="active"
              checked={watch("active")}
              onCheckedChange={(checked) => setValue("active", checked)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="commission_type">Tipo de Comissão</Label>
            <Select
              value={commissionType}
              onValueChange={(val) =>
                setValue("commission_type", val as "none" | "percent" | "fixed")
              }
            >
              <SelectTrigger>
                <SelectValue placeholder="Selecione o tipo de comissão" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">Sem comissão</SelectItem>
                <SelectItem value="percent">Percentual (%)</SelectItem>
                <SelectItem value="fixed">Valor fixo</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {commissionType === "percent" && (
            <div className="space-y-2">
              <Label htmlFor="commission_percent">Percentual de Comissão</Label>
              <Input
                id="commission_percent"
                type="number"
                min={0}
                max={100}
                step={0.01}
                placeholder="0.00"
                {...register("commission_percent", { valueAsNumber: true })}
              />
            </div>
          )}

          {commissionType === "fixed" && (
            <div className="space-y-2">
              <Label htmlFor="commission_fixed">Valor Fixo de Comissão</Label>
              <Input
                id="commission_fixed"
                type="number"
                min={0}
                step={0.01}
                placeholder="0.00"
                {...register("commission_fixed", { valueAsNumber: true })}
              />
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
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
            ) : isEditing ? (
              "Atualizar Profissional"
            ) : (
              "Criar Profissional"
            )}
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
