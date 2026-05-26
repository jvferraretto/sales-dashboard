export const PLATFORM_COLORS = {
  MELI: "#F7DC6F",
  SHOPEE: "#EE4D2D",
} as const

export const PLATFORM_LABELS = {
  MELI: "Mercado Livre",
  SHOPEE: "Shopee",
} as const

export const STATUS_CONFIG = {
  paid:      { label: "Pago",      className: "bg-blue-100 text-blue-800" },
  shipped:   { label: "Enviado",   className: "bg-purple-100 text-purple-800" },
  delivered: { label: "Entregue",  className: "bg-green-100 text-green-800" },
  cancelled: { label: "Cancelado", className: "bg-red-100 text-red-800" },
  pending:   { label: "Pendente",  className: "bg-yellow-100 text-yellow-800" },
} as const
