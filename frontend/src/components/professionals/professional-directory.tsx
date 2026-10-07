"use client"

import useSWR from "swr"
import { Professional } from "@/types/api"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Search, Phone, Mail, Stethoscope, Plus, Edit, Trash2, MoreVertical } from "lucide-react"
import { useState, useMemo } from "react"
import { fetcher } from "@/lib/swr-config"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { toast } from "sonner"
import { ProfessionalForm } from "./professional-form"
import { deleteProfessional } from "@/hooks/use-professionals"
import { mutate } from "swr"

const PROFESSIONALS_KEY = "/api/v1/professionals"

export function ProfessionalDirectory() {
  const { data: allProfessionals, error, isLoading } = useSWR<Professional[]>(PROFESSIONALS_KEY, fetcher)
  const [search, setSearch] = useState("")
  const [editingProfessional, setEditingProfessional] = useState<Professional | null>(null)
  const [deletingProfessional, setDeletingProfessional] = useState<Professional | null>(null)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const filtered = useMemo(() => {
    if (!allProfessionals) return []
    const q = search.toLowerCase()
    return allProfessionals.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.specialty_list?.join(", ").toLowerCase().includes(q) ||
        (p.email || "").toLowerCase().includes(q)
    )
  }, [allProfessionals, search])

  const handleDelete = async () => {
    if (!deletingProfessional) return

    try {
      await deleteProfessional(deletingProfessional.id)
      mutate(PROFESSIONALS_KEY)
      toast.success("Profissional excluído com sucesso!")
    } catch (err) {
      const message = err instanceof Error ? err.message : "Falha ao excluir profissional"
      toast.error(message)
    } finally {
      setDeletingProfessional(null)
      setIsDeleteDialogOpen(false)
    }
  }

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
        <div className="flex items-center gap-4">
          <div className="relative w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar profissionais..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Novo Profissional
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Novo Profissional</DialogTitle>
                <DialogDescription>Preencha os dados do novo profissional</DialogDescription>
              </DialogHeader>
              <ProfessionalForm
                onSuccess={() => {
                  mutate(PROFESSIONALS_KEY)
                }}
              />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((prof) => (
          <Card key={prof.id}>
            <CardHeader className="flex flex-row items-center justify-between gap-4 pb-2">
              <div className="flex items-center gap-4">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(prof.name)}`} alt={prof.name} />
                  <AvatarFallback>
                    <Stethoscope className="h-6 w-6" />
                  </AvatarFallback>
                </Avatar>
                <div className="space-y-1">
                  <CardTitle className="text-lg">{prof.name}</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {prof.specialty_list && prof.specialty_list.length > 0 ? prof.specialty_list.join(", ") : "Sem especialidade"}
                  </p>
                </div>
              </div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem
                    onClick={() => setEditingProfessional(prof)}
                  >
                    <Edit className="mr-2 h-4 w-4" />
                    Editar
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="text-destructive"
                    onClick={() => {
                      setDeletingProfessional(prof)
                      setIsDeleteDialogOpen(true)
                    }}
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Excluir
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
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
              {prof.commission_type !== "none" && (
                <div className="mt-2 text-xs text-muted-foreground">
                  Comissão: {prof.commission_type === "percent" ? `${prof.commission_percent}%` : `R$ ${prof.commission_fixed.toFixed(2)}`}
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

      {filtered.length === 0 && (search || allProfessionals?.length === 0) && (
        <div className="text-center py-8 text-muted-foreground">
          {search ? `Nenhum profissional encontrado para "${search}"` : "Nenhum profissional cadastrado"}
        </div>
      )}

      <Dialog open={!!editingProfessional} onOpenChange={() => setEditingProfessional(null)}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Editar Profissional</DialogTitle>
            <DialogDescription>Atualize os dados do profissional</DialogDescription>
          </DialogHeader>
          {editingProfessional && (
            <ProfessionalForm
              professional={editingProfessional}
              onSuccess={() => {
                setEditingProfessional(null)
                mutate(PROFESSIONALS_KEY)
              }}
            />
          )}
        </DialogContent>
      </Dialog>

      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir profissional?</AlertDialogTitle>
            <AlertDialogDescription>
              Esta ação não pode ser desfeita. O profissional {deletingProfessional?.name} será removido permanentemente.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground"
              onClick={handleDelete}
            >
              Excluir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
