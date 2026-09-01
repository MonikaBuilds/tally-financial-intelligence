const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export async function apiGet(path) {
  const response = await fetch(`${BASE_URL}${path}`)

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }

  return response.json()
}

export async function downloadFile(path, fallbackFilename) {
  const response = await fetch(`${BASE_URL}${path}`)

  if (!response.ok) {
    let detail = `Download failed with status ${response.status}`
    try {
      const data = await response.json()
      if (data?.detail) detail = data.detail
    } catch {
      // ignore non-JSON error bodies
    }
    throw new Error(detail)
  }

  const blob = await response.blob()

  const disposition = response.headers.get('Content-Disposition') || ''
  const match = disposition.match(/filename="?([^"]+)"?/)
  const filename = match ? match[1] : fallbackFilename

  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export async function apiPost(path, body) {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const data = await response.json()
      if (data?.detail) detail = data.detail
    } catch {
      // ignore non-JSON error bodies
    }
    throw new Error(detail)
  }

  return response.json()
}