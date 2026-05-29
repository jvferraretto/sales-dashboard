const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api"

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init)
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `HTTP ${res.status}`)
  }
  return res.json()
}

export const fetcher = (path: string) => apiFetch(path)

export async function triggerSync(platform?: string) {
  return apiFetch("/sync/trigger", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(platform ? { platform } : {}),
  })
}
