"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Lead } from "@/types/api"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface LeadConversionProps {
  lead: Lead
  trigger?: React.ReactNode
  onConverted?: () => void
}

export function LeadConversion({ lead, trigger, onConverted }: LeadConversionProps) {
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [isConverting, setIsConverting] = useState(false)
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null)

  const handleConvert = async () => {
    setIsConverting(true)
    setResult(null)

    try {
      const res = await fetch(`/api/v1/leads/${lead.id}/convert`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      })

      if (!res.ok) {
        throw new Error("Falha ao converter lead")
      }

      const customer = await res.json()
      setResult({ success: true, message: `Cliente criado com sucesso! ID: ${customer.id}` })
      onConverted?.()

      setTimeout(() => {
        router.push(`/customers/${customer.id}`)
      }, 500)
    } catch (err) {
      setResult({ success: false, message: "Não foi possível converter o lead. Tente novamente." })
    } finally {
      setIsConverting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger ?? <Button size="sm">Converter para Cliente</Button>}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Converter Lead para Cliente</DialogTitle>
          <DialogDescription>
            Este lead será convertido para um cliente no sistema. Os dados de contato
            serão transferidos automaticamente.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div>
            <span className="font-medium">Nome:</span> {lead.name}
          </div>
          {lead.email && (
            <div>
              <span className="font-medium">E-mail:</span> {lead.email}
            </div>
          )}
          {lead.phone && (
            <div>
              <span className="font-medium">Telefone:</span> {lead.phone}
            </div>
          )}
        </div>

        {result && (
          <Alert variant={result.success ? "default" : "destructive"}>
            <AlertDescription>{result.message}</AlertDescription>
          </Alert>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)} disabled={isConverting}>
            Cancelar
          </Button>
          <Button onClick={handleConvert} disabled={isConverting || lead.status === "convertido"}>
            {isConverting ? "Convertendo..." : "Confirmar Conversão"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
