"use client"

import { useEffect, useState } from "react"
import useSWR from "swr"
import { fetcher } from "@/lib/api"
import Button from "@/components/ui/Button"

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"

interface CredStatus {
  connected: boolean
  seller_id?: string
  shop_id?: string
  expires_at?: string
}

interface CredentialsData {
  MELI: CredStatus
  SHOPEE: CredStatus
}

function daysUntil(iso: string) {
  const diff = new Date(iso).getTime() - Date.now()
  return Math.max(0, Math.floor(diff / 86400000))
}

export default function SettingsPage() {
  const { data, mutate } = useSWR<CredentialsData>("/credentials", fetcher, { refreshInterval: 5000 })
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get("meli") === "connected")   setToast("Mercado Livre conectado com sucesso!")
    if (params.get("shopee") === "connected") setToast("Shopee conectada com sucesso!")
    if (toast) {
      mutate()
      const t = setTimeout(() => setToast(null), 4000)
      return () => clearTimeout(t)
    }
  }, [toast])

  return (
    <div className="space-y-8 max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900">Configurações</h1>

      {toast && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg text-sm">
          {toast}
        </div>
      )}

      {/* Mercado Livre */}
      <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-yellow-400 flex items-center justify-center text-blue-900 font-bold text-xs">ML</div>
          <div>
            <h2 className="font-semibold text-gray-900">Mercado Livre</h2>
            <p className="text-sm text-gray-500">Conecte sua conta de vendedor via OAuth</p>
          </div>
        </div>

        {data?.MELI.connected ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-green-700 text-sm font-medium">
              <span>✓</span> Conectado
            </div>
            {data.MELI.seller_id && (
              <p className="text-sm text-gray-500">Seller ID: <code className="bg-gray-100 px-1 rounded">{data.MELI.seller_id}</code></p>
            )}
            {data.MELI.expires_at && (
              <p className="text-sm text-gray-500">
                Token expira em <strong>{daysUntil(data.MELI.expires_at)} dias</strong>
                {daysUntil(data.MELI.expires_at) < 7 && (
                  <span className="ml-2 text-orange-600 font-medium">Renovação em breve necessária</span>
                )}
              </p>
            )}
            <Button
              variant="secondary"
              onClick={() => { window.location.href = `${API_BASE}/auth/mercadolivre/login` }}
            >
              Reconectar
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-gray-500">
              Você precisará de um App registrado no{" "}
              <a href="https://developers.mercadolibre.com.br" target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                Portal de Desenvolvedores do ML
              </a>
              {" "}com as credenciais configuradas no <code className="bg-gray-100 px-1 rounded">.env</code>.
            </p>
            <Button onClick={() => { window.location.href = `${API_BASE}/auth/mercadolivre/login` }}>
              Conectar com Mercado Livre
            </Button>
          </div>
        )}
      </div>

      {/* Shopee */}
      <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-orange-500 flex items-center justify-center text-white font-bold text-xs">SP</div>
          <div>
            <h2 className="font-semibold text-gray-900">Shopee</h2>
            <p className="text-sm text-gray-500">Conecte sua loja via Shopee Open Platform</p>
          </div>
        </div>

        {data?.SHOPEE.connected ? (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-green-700 text-sm font-medium">
              <span>✓</span> Conectado
            </div>
            {data.SHOPEE.shop_id && (
              <p className="text-sm text-gray-500">Shop ID: <code className="bg-gray-100 px-1 rounded">{data.SHOPEE.shop_id}</code></p>
            )}
            {data.SHOPEE.expires_at && (
              <p className="text-sm text-gray-500">
                Token expira em <strong>{daysUntil(data.SHOPEE.expires_at)} dias</strong>
              </p>
            )}
            <Button
              variant="secondary"
              onClick={() => { window.location.href = `${API_BASE}/auth/shopee/login` }}
            >
              Reconectar
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            <p className="text-sm text-gray-500">
              Você precisará de um app registrado no{" "}
              <a href="https://open.shopee.com" target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">
                Shopee Open Platform
              </a>
              {" "}com Partner ID e Partner Key configurados no <code className="bg-gray-100 px-1 rounded">.env</code>.
            </p>
            <Button
              className="bg-orange-500 hover:bg-orange-600 text-white"
              onClick={() => { window.location.href = `${API_BASE}/auth/shopee/login` }}
            >
              Conectar com Shopee
            </Button>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800 space-y-1">
        <p className="font-medium">Sincronização automática</p>
        <p>Os pedidos são sincronizados automaticamente todos os dias às 02:00 UTC. Você também pode disparar uma sincronização manual no Dashboard.</p>
      </div>
    </div>
  )
}
