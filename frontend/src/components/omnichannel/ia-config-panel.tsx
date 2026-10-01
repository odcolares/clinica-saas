"use client"

import { useState, useEffect } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import type { Conversation } from "@/types/api"

const AI_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"] as const
type AIModel = typeof AI_MODELS[number]

const AI_SYSTEMS = ["default", "conciso", "educativo", "profissional"] as const
type AISystem = typeof AI_SYSTEMS[number]

export interface IAConfig {
  model: AIModel
  systemPrompt: AISystem
  temperature: number
  maxTokens: number
  isEnabled: boolean
}

export function IAConfigPanel({ initialConfig }: { initialConfig: IAConfig }) {
  const [config, setConfig] = useState<IAConfig>(initialConfig)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    // Load config from API on mount
    loadConfig()
  }, [])

  const loadConfig = async () => {
    setIsLoading(true)
    try {
      const res = await fetch("/api/v1/ai/config", {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      })
      if (res.ok) {
        const data = await res.json()
        setConfig(data)
      }
    } catch (err) {
      console.error("Failed to load AI config:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const saveConfig = async () => {
    setIsLoading(true)
    try {
      const res = await fetch("/api/v1/ai/config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      })
      if (res.ok) {
        toast.success("Configurações de IA salvas com sucesso!")
      } else {
        const err = await res.json().catch(() => ({}))
        toast.error(err.detail || "Falha ao salvar configurações")
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Falha ao salvar configurações")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <ScrollArea className="h-[calc(100vh-12rem)] p-4">
      <h2 className="mb-4 text-lg font-semibold border-b pb-2">
        Configurações de IA
      </h2>

      <form
        className="space-y-4"
        onSubmit={(e) => {
          e.preventDefault()
          saveConfig()
        }}
      >
        <div>
          <label className="block text-sm font-medium mb-2">Modelo</label>
          <Select>
            <SelectTrigger>
              <SelectValue
                className="h-10 px-3 text-sm font-medium"
                defaultValue={config.model}
              >
                {AI_MODELS.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {AI_MODELS.map((model) => (
                <SelectItem key={model} value={model}>
                  {model}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Sistema de prompt</label>
          <Select>
            <SelectTrigger>
              <SelectValue
                className="h-10 px-3 text-sm font-medium"
                defaultValue={config.systemPrompt}
              >
                {AI_SYSTEMS.map((system) => (
                  <SelectItem key={system} value={system}>
                    {system}
                  </SelectItem>
                ))}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {AI_SYSTEMS.map((system) => (
                <SelectItem key={system} value={system}>
                  {system}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Temperatura</label>
            <Input
              type="number"
              value={config.temperature.toString()}
              onChange={(e) =>
                setConfig((prev) => ({
                  ...prev,
                  temperature: Math.max(0, Math.min(2, Number(e.target.value))),
                }))
              }
              min="0"
              max="2"
              step="0.1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Max Tokens</label>
            <Input
              type="number"
              value={config.maxTokens.toString()}
              onChange={(e) =>
                setConfig((prev) => ({
                  ...prev,
                  maxTokens: Math.max(100, Math.min(4000, Number(e.target.value))),
                }))
              }
              min="100"
              max="4000"
            />
          </div>
        </div>

        <div className="flex items-center justify-between">
          <Badge
            variant={config.isEnabled ? "default" : "outline"}
            className="text-sm"
          >
            {config.isEnabled ? "IA Ativa" : "IA Desativada"}
          </Badge>
          <Button
            onClick={saveConfig}
            disabled={isLoading}
            className="px-4 py-2"
          >
            {isLoading ? (
              <span>"Salvando..."</span>
            ) : (
              "Salvar Configurações"
            )}
          </Button>
        </div>
      </form>
    </ScrollArea>
  )
}