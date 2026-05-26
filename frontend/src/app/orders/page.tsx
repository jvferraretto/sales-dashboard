"use client"

import { useCallback, useState } from "react"
import useSWR from "swr"
import { fetcher } from "@/lib/api"
import OrdersTable from "@/components/orders/OrdersTable"

const PLATFORMS = [
  { value: "", label: "Todas" },
  { value: "MELI", label: "Mercado Livre" },
  { value: "SHOPEE", label: "Shopee" },
]

const STATUSES = [
  { value: "", label: "Todos" },
  { value: "paid", label: "Pago" },
  { value: "shipped", label: "Enviado" },
  { value: "delivered", label: "Entregue" },
  { value: "cancelled", label: "Cancelado" },
  { value: "pending", label: "Pendente" },
]

export default function OrdersPage() {
  const [platform, setPlatform] = useState("")
  const [status, setStatus]     = useState("")
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo]     = useState("")
  const [page, setPage]         = useState(1)

  const buildKey = useCallback(() => {
    const params = new URLSearchParams({ page: String(page), page_size: "20" })
    if (platform) params.set("platform", platform)
    if (status)   params.set("status", status)
    if (dateFrom) params.set("date_from", new Date(dateFrom).toISOString())
    if (dateTo)   params.set("date_to", new Date(dateTo + "T23:59:59").toISOString())
    return `/orders?${params}`
  }, [platform, status, dateFrom, dateTo, page])

  const { data } = useSWR(buildKey(), fetcher)

  function handleFilterChange(setter: (v: string) => void) {
    return (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
      setter(e.target.value)
      setPage(1)
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Pedidos</h1>

      {/* Filtros */}
      <div className="flex flex-wrap gap-3 bg-white rounded-xl shadow-sm p-4">
        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500 font-medium">Plataforma</label>
          <select
            value={platform}
            onChange={handleFilterChange(setPlatform)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {PLATFORMS.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500 font-medium">Status</label>
          <select
            value={status}
            onChange={handleFilterChange(setStatus)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500 font-medium">De</label>
          <input
            type="date"
            value={dateFrom}
            onChange={handleFilterChange(setDateFrom)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-xs text-gray-500 font-medium">Até</label>
          <input
            type="date"
            value={dateTo}
            onChange={handleFilterChange(setDateTo)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {(platform || status || dateFrom || dateTo) && (
          <div className="flex flex-col justify-end">
            <button
              onClick={() => {
                setPlatform(""); setStatus(""); setDateFrom(""); setDateTo(""); setPage(1)
              }}
              className="px-3 py-2 text-sm text-gray-500 hover:text-gray-700 underline"
            >
              Limpar filtros
            </button>
          </div>
        )}
      </div>

      <OrdersTable data={data as any} page={page} onPageChange={setPage} />
    </div>
  )
}
