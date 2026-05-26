"use client"

import useSWR from "swr"
import { fetcher } from "@/lib/api"
import KpiCard from "@/components/dashboard/KpiCard"
import OrdersBarChart from "@/components/dashboard/OrdersBarChart"
import RevenueTrendChart from "@/components/dashboard/RevenueTrendChart"
import SyncStatusBar from "@/components/dashboard/SyncStatusBar"

interface KpisData {
  today: { orders: number; revenue: number }
  week:  { orders: number; revenue: number }
  month: { orders: number; revenue: number }
}

export default function DashboardPage() {
  const { data: kpis }    = useSWR<KpisData>("/dashboard/kpis", fetcher, { refreshInterval: 30000 })
  const { data: chart }   = useSWR("/dashboard/chart-data?days=30", fetcher)
  const { data: revenue } = useSWR("/dashboard/revenue-trend?days=30", fetcher)

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <SyncStatusBar />
      </div>

      {/* KPI Cards */}
      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Pedidos</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard label="Hoje"          value={kpis?.today.orders} color="blue" />
          <KpiCard label="Últimos 7 dias" value={kpis?.week.orders}  color="blue" />
          <KpiCard label="Últimos 30 dias" value={kpis?.month.orders} color="blue" />
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Faturamento</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard label="Hoje"           value={kpis?.today.revenue} format="currency" color="green" />
          <KpiCard label="Últimos 7 dias"  value={kpis?.week.revenue}  format="currency" color="green" />
          <KpiCard label="Últimos 30 dias" value={kpis?.month.revenue} format="currency" color="green" />
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Pedidos por dia (últimos 30 dias)</h2>
          <OrdersBarChart data={chart as any} />
        </div>
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-4">Receita por dia (últimos 30 dias)</h2>
          <RevenueTrendChart data={revenue as any} />
        </div>
      </div>
    </div>
  )
}
