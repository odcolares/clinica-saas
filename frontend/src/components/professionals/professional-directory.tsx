"use client"

import useSWR from "swr"
import { Professional } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Search, Phone, Mail, Stethoscope } from "lucide-react"
import { useState, useMemo } from "react"
import { fetcher } from "@/lib/swr-config"

export function ProfessionalDirectory() {
  const { data: allProfessionals, error, isLoading } = useSWR<Professional[]>("/api/v1/professionals", fetcher)
  const [search, setSearch] = useState("")

  const filtered = useMemo(() => {
    if (!allProfessionals) return []
    const q = search.toLowerCase()
    return allProfessionals.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.specialty.toLowerCase().includes(q) ||
        (p.email || "").toLowerCase().includes(q)
    )
  }, [allProfessionals, search])

  if (error) {
    return <div className="text-center py-8 text-muted-foreground">Erro ao carregar profissionais</div>
  }

  if (isLoading) {
    return <div className="text-center py-8 text-muted-foreground">Carregando profissionais...</div>
  }

  return (
    <div className="container mx-auto py-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Profissionais</h1>
        <div className="relative w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar profissionais..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((prof) => (
          <Card key={prof.id}>
            <CardHeader className="flex flex-row items-center gap-4 pb-2">
              <Avatar className="h-12 w-12">
                <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(prof.name)}`} alt={prof.name} />
                <AvatarFallback>
                  <Stethoscope className="h-6 w-6" />
                </AvatarFallback>
              </Avatar>
              <div className="space-y-1">
                <CardTitle className="text-lg">{prof.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{prof.specialty}</p>
              </div>
            </CardHeader>
            <CardContent>
              {prof.email && (
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span>{prof.email}</span>
                </div>
              )}
              {prof.phone && (
                <div className="flex items-center gap-2 text-sm mt-1">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <span>{prof.phone}</span>
                </div>
              )}
              <Badge
                variant={prof.active ? "default" : "secondary"}
                className="mt-3"
              >
                {prof.active ? "Ativo" : "Inativo"}
              </Badge>
            </CardContent>
          </Card>
        ))}
      </div>

      {filtered.length === 0 && search && (
        <div className="text-center py-8 text-muted-foreground">
          Nenhum profissional encontrado para "{search}"
        </div>
      )}
    </div>
  )
}
