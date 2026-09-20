"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { LeadForm } from "@/components/leads/lead-form"
import { LeadCreateRequest } from "@/types/api"
import { toast } from "sonner"

export default function NewLeadPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (data: LeadCreateRequest) => {
    setIsSubmitting(true)
    try {
      const res = await fetch("/api/v1/leads", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      })

      if (!res.ok) {
        throw new Error("Falha ao criar lead")
      }

      toast.success("Lead criado com sucesso!")
      router.push("/leads")
    } catch (err) {
      toast.error("Erro ao criar lead")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="container mx-auto py-6">
      <LeadForm
        onSubmit={handleSubmit}
        isLoading={isSubmitting}
        submitLabel="Criar Lead"
      />
    </div>
  )
}
