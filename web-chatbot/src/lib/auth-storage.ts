import type { AuthResponse } from "@/lib/api"
import { isTokenValid } from "@/lib/jwt"

const AUTH_STORAGE_KEY = "web-chatbot.auth"

export type AuthSession = {
  accessToken: string
  tokenType: "bearer"
  user: AuthResponse["user"]
}

export function createSession(response: AuthResponse): AuthSession {
  return {
    accessToken: response.access_token,
    tokenType: response.token_type,
    user: response.user,
  }
}

export function readAuthSession(): AuthSession | null {
  const rawSession = localStorage.getItem(AUTH_STORAGE_KEY)

  if (!rawSession) {
    return null
  }

  try {
    const session = JSON.parse(rawSession) as AuthSession

    if (!session.accessToken || !session.user || !isTokenValid(session.accessToken)) {
      clearAuthSession()
      return null
    }

    return session
  } catch {
    clearAuthSession()
    return null
  }
}

export function writeAuthSession(session: AuthSession) {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session))
}

export function clearAuthSession() {
  localStorage.removeItem(AUTH_STORAGE_KEY)
}
