"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Plus, Pencil, Trash2, MessageSquare } from "lucide-react"
import { useTemplates, createTemplateItem, updateTemplateItem, deleteTemplateItem } from "@/hooks/use-conversations"
import type { Template } from "@/types/api"

const CHANNEL_LABELS: Record<string, string> = {
  telegram: "Telegram",
  whatsapp: "WhatsApp",
}

export function MessageTemplates() {
  const { templates, isLoading } = useTemplates()
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Template | null>(null)
  const [name, setName] = useState("")
  const [channel, setChannel] = useState("telegram")
  const [body, setBody] = useState("")
  const [active, setActive] = useState(true)

  function resetForm() {
    setName("")
    setChannel("telegram")
    setBody("")
    setActive(true)
    setEditing(null)
  }

  function openCreate() {
    resetForm()
    setOpen(true)
  }

  function openEdit(t: Template) {
    setEditing(t)
    setName(t.name)
    setChannel(t.channel)
    setBody(t.body)
    setActive(t.active)
    setOpen(true)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (editing) {
      await updateTemplateItem(editing.id, { name, channel, body, active })
    } else {
      await createTemplateItem({ name, channel, body, active })
    }
    setOpen(false)
    resetForm()
  }

  async function handleDelete(id: string) {
    if (confirm("Excluir este template?")) {
      await deleteTemplateItem(id)
    }
  }

  if (isLoading) {
    return (
      <div className="container mx-auto py-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">Carregando templates...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Mensagens Automáticas</h1>
          <p className="text-sm text-muted-foreground">
            Templates de resposta rápida para agilizar o atendimento.
          </p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button onClick={openCreate}>
              <Plus className="mr-2 h-4 w-4" />
              Novo Template
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editing ? "Editar Template" : "Novo Template"}</DialogTitle>
              <DialogDescription>
                {editing
                  ? "Atualize o template de resposta."
                  : "Crie um template para resposta automática."}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nome</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Ex: Saudação inicial"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="channel">Canal</Label>
                <select
                  id="channel"
                  value={channel}
                  onChange={(e) => setChannel(e.target.value)}
                  className="w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
                >
                  <option value="telegram">Telegram</option>
                  <option value="whatsapp">WhatsApp</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="body">Mensagem</Label>
                <Textarea
                  id="body"
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  placeholder="Texto da mensagem..."
                  rows={4}
                  required
                />
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  id="active"
                  checked={active}
                  onCheckedChange={setActive}
                />
                <Label htmlFor="active">Ativo</Label>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit">
                  {editing ? "Atualizar" : "Criar"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {templates.length === 0 ? (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            Nenhum template encontrado. Crie o primeiro.
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {templates.map((t) => (
            <Card key={t.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <MessageSquare className="h-5 w-5 text-muted-foreground" />
                    <CardTitle>{t.name}</CardTitle>
                    <Badge variant={t.active ? "default" : "secondary"}>
                      {CHANNEL_LABELS[t.channel] || t.channel}
                    </Badge>
                    {!t.active && <Badge variant="outline">Inativo</Badge>}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="ghost" size="icon" onClick={() => openEdit(t)}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(t.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                  {t.body}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}