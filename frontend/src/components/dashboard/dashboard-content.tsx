"use client"

import { ReactElement } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DollarSign, Users, Calendar, TrendingUp, TrendingDown, Clock } from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip, Legend } from "recharts"
import { appointments, leads, cashTransactions } from "@/mocks/data"
import { format, startOfWeek, endOfWeek } from "date-fns"
import { ptBR } from "date-fns/locale/pt-BR"

const now = new Date("2025-09-19")

const dashboardData = {
  totalRevenue: cashTransactions
    .filter((t) => t.type === "income")
    .reduce((sum, t) => sum + t.amount, 0),
  totalCustomers: leads.filter((l) => l.status === "CONVERTED").length,
  activeLeads: leads.filter((l) => l.status !== "CONVERTED" && l.status !== "LOST").length,
  todaysAppointments: appointments.filter((a) =>
    a.start_time.startsWith(format(now, "yyyy-MM-dd"))
  ).length,
}

const MONTHLY_DATA = [
  { month: "Mar", receita: 18500, despesas: 8200 },
  { month: "Abr", receita: 21200, despesas: 9800 },
  { month: "Mai", receita: 19800, despesas: 7600 },
  { month: "Jun", receita: 23400, despesas: 10200 },
  { month: "Jul", receita: 25600, despesas: 11800 },
  { month: "Ago", receita: 22100, despesas: 9400 },
  { month: "Set", receita: dashboardData.totalRevenue, despesas: 0 },
]

interface KPICardProps {
  title: string
  value: string
  icon: ReactElement
  change: string
  trend: "up" | "down" | "neutral"
}

function KPICard({ title, value, icon, change, trend }: KPICardProps) {
  const trendColor = trend === "up" ? "text-green-600" : trend === "down" ? "text-red-600" : "text-muted-foreground"
  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Clock

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <div className="flex items-center text-xs text-muted-foreground mt-1">
          <TrendIcon className={`h-3 w-3 mr-1 ${trendColor}`} />
          {change}
        </div>
      </CardContent>
    </Card>
  )
}

export function DashboardContent() {
  return (
    <div className="container mx-auto py-6 space-y-6">
      <h1 className="text-2xl font-bold">Painel de Controle</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Receita Total"
          value={`R$ ${dashboardData.totalRevenue.toLocaleString("pt-BR", { minimumFractionDigits: 2 })}`}
          icon={<DollarSign className="h-4 w-4 text-muted-foreground" />}
          change="+12% vs mês passado"
          trend="up"
        />
        <KPICard
          title="Clientes Ativos"
          value={dashboardData.totalCustomers.toString()}
          icon={<Users className="h-4 w-4 text-muted-foreground" />}
          change="+8 novos este mês"
          trend="up"
        />
        <KPICard
          title="Leads Ativos"
          value={dashboardData.activeLeads.toString()}
          icon={<TrendingUp className="h-4 w-4 text-muted-foreground" />}
          change="-3 vs semana passada"
          trend="down"
        />
        <KPICard
          title="Agendamentos Hoje"
          value={dashboardData.todaysAppointments.toString()}
          icon={<Calendar className="h-4 w-4 text-muted-foreground" />}
          change="3 concluídos"
          trend="neutral"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Receita Mensal</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={MONTHLY_DATA} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis tickFormatter={(v: any) => `R$ ${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(value: any) => [
                    `R$ ${(value as number).toLocaleString("pt-BR")}`,
                    "",
                  ]}
                />
                <Legend />
                <Bar dataKey="receita" fill="#2563eb" name="Receita" radius={[4, 4, 0, 0]} />
                <Bar dataKey="despesas" fill="#ef4444" name="Despesas" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
