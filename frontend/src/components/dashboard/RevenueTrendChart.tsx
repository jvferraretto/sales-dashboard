"use client"

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts"
import { PLATFORM_COLORS } from "@/lib/constants"

interface RevenuePoint {
  day: string
  platform: "MELI" | "SHOPEE"
  revenue: number
}

interface TransformedPoint {
  day: string
  MELI: number
  SHOPEE: number
}

function transform(data: RevenuePoint[]): TransformedPoint[] {
  const map = new Map<string, TransformedPoint>()
  for (const row of data) {
    if (!map.has(row.day)) map.set(row.day, { day: row.day, MELI: 0, SHOPEE: 0 })
    map.get(row.day)![row.platform] = row.revenue
  }
  return Array.from(map.values()).sort((a, b) => a.day.localeCompare(b.day))
}

function formatBRL(v: number) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
}

export default function RevenueTrendChart({ data }: { data?: RevenuePoint[] }) {
  const transformed = data ? transform(data) : []

  if (!data) return <div className="h-64 flex items-center justify-center text-gray-400">Carregando...</div>
  if (!transformed.length) return <div className="h-64 flex items-center justify-center text-gray-400">Sem dados no período</div>

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={transformed} margin={{ top: 4, right: 8, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="day" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
        <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
        <Tooltip formatter={(v: number) => formatBRL(v)} />
        <Legend />
        <Line type="monotone" dataKey="MELI"   name="Mercado Livre" stroke={PLATFORM_COLORS.MELI}   strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="SHOPEE" name="Shopee"         stroke={PLATFORM_COLORS.SHOPEE} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}
