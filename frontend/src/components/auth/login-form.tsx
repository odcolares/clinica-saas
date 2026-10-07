"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2 } from "lucide-react"

const loginSchema = z.object({
  email: z.string().email("E-mail inválido"),
  password: z.string().min(1, "Senha é obrigatória"),
  tenant: z.string().min(1, "Tenant é obrigatório"),
})

type LoginFormValues = z.infer<typeof loginSchema>

export function LoginForm() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "admin@clinica.local", tenant: "demo" },
  })

  const onSubmit = async (data: LoginFormValues) => {
    setError(null)

    try {
      const res = await fetch("/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Tenant-Id": data.tenant,
        },
        body: JSON.stringify({ email: data.email, password: data.password }),
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => null)
        setError(errorData?.detail || "Credenciais inválidas")
        return
      }

      const response = await res.json()

      document.cookie = `access_token=${response.access}; path=/; max-age=604800; SameSite=Lax`
      document.cookie = `refresh_token=${response.refresh}; path=/; max-age=2592000; SameSite=Lax`

      router.push("/dashboard")
    } catch (err) {
      setError("Falha na conexão")
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Card className="w-full max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Clínica SaaS</CardTitle>
          <CardDescription>Digite suas credenciais para continuar</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="tenant">Clínica (tenant)</Label>
            <Input
              id="tenant"
              placeholder="demo"
              autoComplete="off"
              {...register("tenant")}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">E-mail</Label>
            <Input
              id="email"
              type="email"
              placeholder="admin@clinica.local"
              autoComplete="email"
              {...register("email")}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Senha</Label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              {...register("password")}
            />
          </div>
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
        </CardContent>
        <CardFooter>
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Entrando...
              </>
            ) : (
              "Entrar"
            )}
          </Button>
        </CardFooter>
      </Card>
    </form>
  )
}
