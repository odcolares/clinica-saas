"use client"

import { z } from "zod"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Lead, LeadCreateRequest } from "@/types/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Loader2 } from "lucide-react"

const sourceEnum = ["google", "facebook", "indicacao", "site", "other"] as const

const leadSchema = z.object({
  name: z.string().min(1, "Nome é obrigatório"),
  email: z.string().email("E-mail inválido").optional().or(z.literal("")),
  phone: z.string().optional(),
  source: z.enum(sourceEnum),
  source_detail: z.string().optional(),
})

type LeadFormData = z.infer<typeof leadSchema>
type SourceValue = typeof sourceEnum[number]

const SOURCE_LABELS: Record<SourceValue, string> = {
  google: "Google",
  facebook: "Facebook",
  indicacao: "Indicação",
  site: "Site",
  other: "Outro",
}

const SOURCE_OPTIONS: { value: SourceValue; label: string }[] = sourceEnum.map((value) => ({
  value,
  label: SOURCE_LABELS[value],
}))

interface LeadFormProps {
  initialData?: Partial<Lead>
  onSubmit: (data: LeadCreateRequest) => Promise<void>
  isLoading?: boolean
  submitLabel?: string
}

export function LeadForm({
  initialData,
  onSubmit,
  isLoading = false,
  submitLabel = "Salvar",
}: LeadFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<LeadFormData>({
    resolver: zodResolver(leadSchema),
    defaultValues: {
      name: initialData?.name ?? "",
      email: initialData?.email ?? "",
      phone: initialData?.phone ?? "",
      source: (initialData?.source as SourceValue) ?? "site",
      source_detail: initialData?.source_detail ?? "",
    },
  })

  const handleFormSubmit = async (data: LeadFormData) => {
    const payload: LeadCreateRequest = {
      name: data.name,
      email: data.email || null,
      phone: data.phone || null,
      source: data.source,
      source_detail: data.source_detail || null,
    }
    await onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Informações do Lead</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Nome *</Label>
            <Input
              id="name"
              placeholder="Digite o nome completo"
              {...register("name")}
              aria-invalid={!!errors.name}
            />
            {errors.name && (
              <p className="text-sm text-destructive">{errors.name.message}</p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                type="email"
                placeholder="nome@exemplo.com"
                {...register("email")}
                aria-invalid={!!errors.email}
              />
              {errors.email && (
                <p className="text-sm text-destructive">{errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Telefone</Label>
              <Input
                id="phone"
                type="tel"
                placeholder="(11) 99999-9999"
                {...register("phone")}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="source">Origem *</Label>
            <Select
              value={initialData?.source ?? "site"}
              onValueChange={(value) => setValue("source", value as SourceValue)}
            >
              <SelectTrigger id="source">
                <SelectValue placeholder="Selecione a origem" />
              </SelectTrigger>
              <SelectContent>
                {SOURCE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.source && (
              <p className="text-sm text-destructive">{errors.source.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="source_detail">Detalhes da origem</Label>
            <Textarea
              id="source_detail"
              placeholder="Informações adicionais sobre como o lead foi adquirido"
              {...register("source_detail")}
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      <CardFooter className="flex justify-end gap-3">
        <Button type="button" variant="outline" disabled={isLoading}>
          Cancelar
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Salvando...
            </>
          ) : (
            submitLabel
          )}
        </Button>
      </CardFooter>
    </form>
  )
}
