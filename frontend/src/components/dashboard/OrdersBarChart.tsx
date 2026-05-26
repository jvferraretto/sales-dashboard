"use client"

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts"
import { PLATFORM_COLORS } from "@/lib/constants"

interface ChartPoint {
  day: string
  platform: "MELI" | "SHOPEE"
  count: number
}

interface TransformedPoint {
  day: string
  MELI: number
  SHOPEE: number
}

function transform(data: ChartPoint[]): TransformedPoint[] {
  const map = new Map<string, TransformedPoint>()
  for (const row of data) {
    if (!map.has(row.day)) map.set(row.day, { day: row.day, MELI: 0, SHOPEE: 0 })
    map.get(row.day)![row.platform] = row.count
  }
  return Array.from(map.values()).sort((a, b) => a.day.localeCompare(b.day))
}

export default function OrdersBarChart({ data }: { data?: ChartPoint[] }) {
  const transformed = data ? transform(data) : []

  if (!data) return <div className="h-64 flex items-center justify-center text-gray-400">Carregando...</div>
  if (!transformed.length) return <div className="h-64 flex items-center justify-center text-gray-400">Sem dados no período</div>

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={transformed} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="day" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Legend />
        <Bar dataKey="MELI"   name="Mercado Livre" stackId="a" fill={PLATFORM_COLORS.MELI} />
        <Bar dataKey="SHOPEE" name="Shopee"         stackId="a" fill={PLATFORM_COLORS.SHOPEE} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
