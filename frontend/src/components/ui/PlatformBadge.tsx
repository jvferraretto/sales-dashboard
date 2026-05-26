import { PLATFORM_LABELS } from "@/lib/constants"

type Platform = "MELI" | "SHOPEE"

const CONFIG: Record<Platform, { className: string }> = {
  MELI:   { className: "bg-yellow-400 text-blue-900 border border-blue-800" },
  SHOPEE: { className: "bg-orange-500 text-white border border-orange-600" },
}

export default function PlatformBadge({ platform }: { platform: Platform }) {
  const cfg = CONFIG[platform]
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${cfg.className}`}>
      {PLATFORM_LABELS[platform]}
    </span>
  )
}
