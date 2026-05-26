"use client"

import { useState } from "react"
import useSWR, { useSWRConfig } from "swr"
import { fetcher, triggerSync } from "@/lib/api"
import Button from "@/components/ui/Button"

interface SyncEntry {
  last_synced_at: string | null
  status: string
  orders_fetched: number
  error_message: string | null
}

interface SyncStatus {
  MELI: SyncEntry
  SHOPEE: SyncEntry
}

function timeAgo(iso: string) {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return "agora"
  if (mins < 60) return `${mins}min atrás`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h atrás`
  return `${Math.floor(hrs / 24)}d atrás`
}

export default function SyncStatusBar() {
  const [syncing, setSyncing] = useState(false)
  const { mutate } = useSWRConfig()
  const { data } = useSWR<SyncStatus>("/sync/status", fetcher, {
    refreshInterval: syncing ? 3000 : 60000,
  })

  async function handleSync() {
    setSyncing(true)
    await triggerSync()
    // Poll until both platforms are no longer "running"
    const interval = setInterval(async () => {
      const status = await fetcher("/sync/status") as SyncStatus
      const running = Object.values(status).some((e) => e.status === "running")
      if (!running) {
        clearInterval(interval)
        setSyncing(false)
        mutate("/sync/status")
        mutate("/dashboard/kpis")
        mutate("/dashboard/chart-data?days=30")
        mutate("/dashboard/revenue-trend?days=30")
      }
    }, 3000)
  }

  const statusIcon = (s: string) =>
    s === "success" ? "✓" : s === "error" ? "✗" : s === "running" ? "⟳" : "—"

  return (
    <div className="flex items-center gap-4 text-sm text-gray-500">
      {data && (
        <span>
          ML: <strong>{statusIcon(data.MELI.status)}</strong>
          {data.MELI.last_synced_at && ` ${timeAgo(data.MELI.last_synced_at)}`}
          {" · "}
          Shopee: <strong>{statusIcon(data.SHOPEE.status)}</strong>
          {data.SHOPEE.last_synced_at && ` ${timeAgo(data.SHOPEE.last_synced_at)}`}
        </span>
      )}
      <Button variant="secondary" loading={syncing} onClick={handleSync}>
        {syncing ? "Sincronizando..." : "Sync Agora"}
      </Button>
    </div>
  )
}
