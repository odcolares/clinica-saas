"use client"

import { Switch } from "@/components/ui/switch"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MessageSquare } from "lucide-react"

const CHANNELS = [
  {
    id: "telegram",
    name: "Telegram",
    description: "Receba e responda mensagens do Telegram Bot.",
    active: true,
    webhook: "Configurado",
  },
  {
    id: "whatsapp",
    name: "WhatsApp",
    description: "Canal em desenvolvimento (Etapa futura).",
    active: false,
    webhook: "Indisponível",
  },
]

/**
 * Painel de gestão de canais.
 *
 * Toggles por canal. Telegram já está integrado (backend pronto).
 * WhatsApp é apenas visual — o adapter existe no backend mas não está
 * configurado em produção.
 */
export function ChannelManagement() {
  return (
    <div className="container mx-auto py-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Canais de Atendimento</h1>
        <p className="text-sm text-muted-foreground">
          Gerencie os canais de comunicação com clientes.
        </p>
      </div>

      <div className="grid gap-4">
        {CHANNELS.map((channel) => (
          <Card key={channel.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <MessageSquare className="h-5 w-5 text-muted-foreground" />
                  <CardTitle>{channel.name}</CardTitle>
                  {channel.active ? (
                    <Badge variant="default">Ativo</Badge>
                  ) : (
                    <Badge variant="secondary">Em breve</Badge>
                  )}
                </div>
                <Switch checked={channel.active} disabled={!channel.active} />
              </div>
              <CardDescription>{channel.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Webhook:</span>
                <Badge variant="outline">{channel.webhook}</Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}