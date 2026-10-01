"use client"

import { useState } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import type { Conversation } from "@/types/api"

const PROMPT_TEMPLATES = {
  default: "Default",
  conciso: "Resposta curta e direta",
  educativo: "Tom educativo e explicativo",
  profissional: "Tom profissional corporativo",
  urgente: "Tom de urgência"
} as const

type PromptTemplate = keyof typeof PROMPT_TEMPLATES

export function PromptAdjustmentPanel({ 
  conversationId,
  onApplyPrompt 
}: {
  conversationId: string
  onApplyPrompt: (template: PromptTemplate, customPrompt?: string) => void
}) {
  const [selectedTemplate, setSelectedTemplate] = useState<PromptTemplate>("default")
  const [customPrompt, setCustomPrompt] = useState("")
  const [isSaving, setIsSaving] = useState(false)

  const applyPrompt = async (template: PromptTemplate) => {
    setIsSaving(true)
    try {
      const res = await fetch(`/api/v1/ai/apply-prompt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: conversationId,
          template,
          custom_prompt: selectedTemplate === "default" && customPrompt.trim() ? customPrompt : undefined,
        }),
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        toast.error(err.detail || "Falha ao aplicar prompt")
        return
      }
      const data = await res.json()
      toast.success("Prompt aplicado com sucesso!")
      onApplyPrompt(template, customPrompt || undefined)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao aplicar prompt")
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <ScrollArea className="h-[calc(100vh-12rem)] p-4">
      <h2 className="mb-4 text-lg font-semibold border-b pb-2">
        Ajustes de Prompt da IA
      </h2>

      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault()
          applyPrompt(selectedTemplate as PromptTemplate)
        }}
      >
        <div>
          <label className="block text-sm font-medium mb-2">Selecionar modelo</label>
          <Select>
            <SelectTrigger>
              <SelectValue className="h-10 px-3 text-sm font-medium" defaultValue="default">
                {Object.keys(PROMPT_TEMPLATES).map((template) => (
                  <SelectItem key={template} value={template}>
                    {PROMPT_TEMPLATES[template as PromptTemplate]}
                  </SelectItem>
                ))}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {Object.keys(PROMPT_TEMPLATES).map((template) => (
                <SelectItem key={template} value={template}>
                  {PROMPT_TEMPLATES[template as PromptTemplate]}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {selectedTemplate !== "default" ? (
          <div>
            <label className="block text-sm font-medium mb-2">Prompt personalizado</label>
            <Input
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              placeholder="Digite um prompt personalizado (opcional)"
              disabled={isSaving}
            />
          </div>
        ) : (
          <div>
            <p className="text-sm text-muted-foreground">
              Prompt personalizado disponível ao selecionar um modelo diferente
            </p>
          </div>
        )}

        <div className="flex items-center justify-between">
          <Badge variant="outline" className="text-sm">
            {PROMPT_TEMPLATES[selectedTemplate as PromptTemplate]}
          </Badge>
          <Button
            onClick={() => applyPrompt(selectedTemplate as PromptTemplate)}
            disabled={isSaving}
            className="px-4 py-2"
          >
            {isSaving ? ("Aplicando...") : ("Aplicar Prompt")}
          </Button>
        </div>
      </form>
    </ScrollArea>
  )
}