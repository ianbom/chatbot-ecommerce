type JwtPayload = {
  exp?: number
}

export function isTokenValid(token: string) {
  const payload = decodeJwtPayload(token)

  if (!payload?.exp) {
    return false
  }

  return payload.exp > Math.floor(Date.now() / 1000)
}

function decodeJwtPayload(token: string): JwtPayload | null {
  const [, payload] = token.split(".")

  if (!payload) {
    return null
  }

  try {
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/")
    const padded = normalized.padEnd(
      normalized.length + ((4 - (normalized.length % 4)) % 4),
      "="
    )

    return JSON.parse(atob(padded)) as JwtPayload
  } catch {
    return null
  }
}
