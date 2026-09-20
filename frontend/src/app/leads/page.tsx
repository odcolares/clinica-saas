"use client"

import { useSearchParams, useRouter } from "next/navigation"
import useSWR from "swr"
import { Suspense } from "react"
import { swrConfig, fetcher } from "@/lib/swr-config"
import { Lead, LeadStatus } from "@/types/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale/pt-BR"

const STATUS_LABELS: Record<LeadStatus, string> = {
  NEW: "Novo",
  CONTACTED: "Contatado",
  QUALIFIED: "Qualificado",
  CONVERTED: "Convertido",
  LOST: "Desativado",
}

const SOURCE_LABELS: Record<string, string> = {
  google: "Google",
  facebook: "Facebook",
  indicacao: "Indicação",
  site: "Site",
  other: "Outro",
}

const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: "all", label: "Todos os status" },
  ...Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label })),
]

const SOURCE_OPTIONS: { value: string; label: string }[] = [
  { value: "all", label: "Todas as origens" },
  ...Object.entries(SOURCE_LABELS).map(([value, label]) => ({ value, label })),
]

function buildQueryString(params: Record<string, string | undefined>) {
  const qs = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value && value !== "all") qs.set(key, value)
  })
  return qs.toString()
}

export default function LeadsListPage() {
  return (
    <Suspense fallback={<div>Carregando leads...</div>}>
      <LeadsListContent />
    </Suspense>
  )
}

function LeadsListContent() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const statusFilter = searchParams.get("status") ?? "all"
  const sourceFilter = searchParams.get("source") ?? "all"
  const searchFilter = searchParams.get("search") ?? ""
  const dateStart = searchParams.get("date_start") ?? ""
  const dateEnd = searchParams.get("date_end") ?? ""
  const page = parseInt(searchParams.get("page") ?? "1", 10)

  const queryString = buildQueryString({
    status: statusFilter,
    source: sourceFilter,
    search: searchFilter || undefined,
    date_start: dateStart || undefined,
    date_end: dateEnd || undefined,
    page: page.toString(),
  })

  const { data, error } = useSWR<{
    count: number
    next: string | null
    previous: string | null
    results: Lead[]
  }>(`/api/v1/leads?${queryString}`, fetcher, swrConfig)

  const leads = data?.results ?? []
  const total = data?.count ?? 0
  const hasNext = data?.next !== null
  const hasPrevious = data?.previous !== null

  const updateParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (value && value !== "all") {
      params.set(key, value)
    } else {
      params.delete(key)
    }
    params.set("page", "1")
    router.push(`?${params.toString()}`)
  }

  const handleSearch = (value: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (value) {
      params.set("search", value)
    } else {
      params.delete("search")
    }
    params.set("page", "1")
    router.push(`?${params.toString()}`)
  }

  const handlePage = (newPage: number) => {
    const params = new URLSearchParams(searchParams.toString())
    params.set("page", newPage.toString())
    router.push(`?${params.toString()}`)
  }

  const handlePeriod = (start: string, end: string) => {
    const params = new URLSearchParams(searchParams.toString())
    if (start) params.set("date_start", start)
    else params.delete("date_start")
    if (end) params.set("date_end", end)
    else params.delete("date_end")
    params.set("page", "1")
    router.push(`?${params.toString()}`)
  }

  const isLoading = !data && !error

  return (
    <div className="container mx-auto py-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Leads</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <Input
              placeholder="Buscar por nome ou e-mail..."
              defaultValue={searchFilter}
              onChange={(e) => handleSearch(e.target.value)}
              className="sm:max-w-xs"
            />
            <Select value={statusFilter} onValueChange={(v) => updateParam("status", v)}>
              <SelectTrigger className="w-full sm:w-[200px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                {STATUS_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={sourceFilter} onValueChange={(v) => updateParam("source", v)}>
              <SelectTrigger className="w-full sm:w-[200px]">
                <SelectValue placeholder="Origem" />
              </SelectTrigger>
              <SelectContent>
                {SOURCE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <div className="flex gap-2">
              <Input
                type="date"
                value={dateStart}
                onChange={(e) => handlePeriod(e.target.value, dateEnd)}
                className="w-full sm:w-auto"
              />
              <Input
                type="date"
                value={dateEnd}
                onChange={(e) => handlePeriod(dateStart, e.target.value)}
                className="w-full sm:w-auto"
              />
            </div>
          </div>

          <div className="text-sm text-muted-foreground">
            {total} lead{total !== 1 ? "s" : ""} encontrado{total !== 1 ? "s" : ""}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          {isLoading ? (
            <div className="py-8 text-center text-muted-foreground">Carregando leads...</div>
          ) : error ? (
            <div className="py-8 text-center text-destructive">
              Erro ao carregar leads: {error.message}
            </div>
          ) : leads.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              Nenhum lead encontrado.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>E-mail</TableHead>
                  <TableHead>Telefone</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Origem</TableHead>
                  <TableHead>Criado em</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leads.map((lead) => (
                  <TableRow key={lead.id}>
                    <TableCell className="font-medium">{lead.name}</TableCell>
                    <TableCell>{lead.email ?? "—"}</TableCell>
                    <TableCell>{lead.phone ?? "—"}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{STATUS_LABELS[lead.status]}</Badge>
                    </TableCell>
                    <TableCell>{SOURCE_LABELS[lead.source]}</TableCell>
                    <TableCell>
                      {format(new Date(lead.created_at), "dd/MM/yyyy", { locale: ptBR })}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {total > 0 && (
        <div className="flex justify-between items-center">
          <Button
            variant="outline"
            size="sm"
            disabled={!hasPrevious || isLoading}
            onClick={() => handlePage(page - 1)}
          >
            Anterior
          </Button>
          <span className="text-sm text-muted-foreground">
            Página {page}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={!hasNext || isLoading}
            onClick={() => handlePage(page + 1)}
          >
            Próxima
          </Button>
        </div>
      )}
    </div>
  )
}
