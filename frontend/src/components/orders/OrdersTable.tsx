"use client"

import PlatformBadge from "@/components/ui/PlatformBadge"
import { STATUS_CONFIG } from "@/lib/constants"

interface Order {
  id: number
  platform: "MELI" | "SHOPEE"
  external_order_id: string
  status: keyof typeof STATUS_CONFIG
  total_amount: number
  buyer_name: string
  created_at: string
}

interface OrdersPage {
  total: number
  page: number
  page_size: number
  items: Order[]
}

interface Props {
  data?: OrdersPage
  page: number
  onPageChange: (p: number) => void
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("pt-BR", {
    day: "2-digit", month: "2-digit", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  })
}

export default function OrdersTable({ data, page, onPageChange }: Props) {
  if (!data) return <div className="text-gray-400 py-8 text-center">Carregando...</div>

  const totalPages = Math.ceil(data.total / data.page_size)
  const start = (page - 1) * data.page_size + 1
  const end = Math.min(page * data.page_size, data.total)

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {["Pedido", "Plataforma", "Comprador", "Status", "Valor", "Data"].map((h) => (
                <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {data.items.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center py-8 text-gray-400">
                  Nenhum pedido encontrado
                </td>
              </tr>
            )}
            {data.items.map((order) => {
              const statusCfg = STATUS_CONFIG[order.status] ?? { label: order.status, className: "bg-gray-100 text-gray-600" }
              return (
                <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">
                    #{order.external_order_id.slice(-8)}
                  </td>
                  <td className="px-4 py-3">
                    <PlatformBadge platform={order.platform} />
                  </td>
                  <td className="px-4 py-3 text-gray-700">{order.buyer_name || "—"}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusCfg.className}`}>
                      {statusCfg.label}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {order.total_amount.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{formatDate(order.created_at)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Paginação */}
      <div className="flex items-center justify-between text-sm text-gray-500">
        <span>
          {data.total > 0 ? `Exibindo ${start}–${end} de ${data.total} pedidos` : "0 pedidos"}
        </span>
        <div className="flex gap-2">
          <button
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
            className="px-3 py-1.5 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            ← Anterior
          </button>
          <span className="px-3 py-1.5">{page} / {totalPages || 1}</span>
          <button
            disabled={page >= totalPages}
            onClick={() => onPageChange(page + 1)}
            className="px-3 py-1.5 rounded border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Próxima →
          </button>
        </div>
      </div>
    </div>
  )
}
