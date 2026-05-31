import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react"

import { loginRequest, registerRequest, type AuthUser } from "@/lib/api"
import {
  clearAuthSession,
  createSession,
  readAuthSession,
  writeAuthSession,
  type AuthSession,
} from "@/lib/auth-storage"

type AuthContextValue = {
  session: AuthSession | null
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  login: (payload: { email: string; password: string }) => Promise<void>
  register: (payload: {
    name: string
    email: string
    password: string
  }) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(() => readAuthSession())

  const login = useCallback(async (payload: { email: string; password: string }) => {
    const authResponse = await loginRequest(payload)
    const nextSession = createSession(authResponse)
    writeAuthSession(nextSession)
    setSession(nextSession)
  }, [])

  const register = useCallback(
    async (payload: { name: string; email: string; password: string }) => {
      const authResponse = await registerRequest(payload)
      const nextSession = createSession(authResponse)
      writeAuthSession(nextSession)
      setSession(nextSession)
    },
    []
  )

  const logout = useCallback(() => {
    clearAuthSession()
    setSession(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      user: session?.user ?? null,
      token: session?.accessToken ?? null,
      isAuthenticated: Boolean(session),
      login,
      register,
      logout,
    }),
    [login, logout, register, session]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)

  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider")
  }

  return value
}
