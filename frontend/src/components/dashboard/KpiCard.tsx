interface KpiCardProps {
  label: string
  value?: number
  format?: "number" | "currency"
  color?: "blue" | "green" | "purple"
}

const colors = {
  blue:   "border-l-blue-500",
  green:  "border-l-green-500",
  purple: "border-l-purple-500",
}

function formatValue(value: number, format: "number" | "currency") {
  if (format === "currency") {
    return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })
  }
  return value.toLocaleString("pt-BR")
}

export default function KpiCard({ label, value, format = "number", color = "blue" }: KpiCardProps) {
  return (
    <div className={`bg-white rounded-xl shadow-sm p-6 border-l-4 ${colors[color]}`}>
      <p className="text-sm text-gray-500 mb-1">{label}</p>
      <p className="text-2xl font-bold text-gray-900">
        {value === undefined ? "—" : formatValue(value, format)}
      </p>
    </div>
  )
}
