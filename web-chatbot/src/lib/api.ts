const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? DEFAULT_API_BASE_URL

export type UserRole = "superadmin" | "admin" | "staff"

export type AuthUser = {
  id: number
  name: string
  email: string
  role: UserRole
  is_active: boolean
}

export type AuthResponse = {
  access_token: string
  token_type: "bearer"
  user: AuthUser
}

type ApiErrorBody = {
  detail?: string | { msg?: string }[]
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    })
  } catch {
    throw new ApiError("Cannot connect to API server", 0)
  }

  if (!response.ok) {
    const body = (await readJson(response)) as ApiErrorBody | null
    throw new ApiError(getErrorMessage(body, response.status), response.status)
  }

  return response.json() as Promise<T>
}

export function loginRequest(payload: { email: string; password: string }) {
  return apiFetch<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function registerRequest(payload: {
  name: string
  email: string
  password: string
}) {
  return apiFetch<AuthResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

async function readJson(response: Response) {
  try {
    return await response.json()
  } catch {
    return null
  }
}

function getErrorMessage(body: ApiErrorBody | null, status: number) {
  if (typeof body?.detail === "string") {
    return body.detail
  }

  if (Array.isArray(body?.detail)) {
    return body.detail.map((error) => error.msg).filter(Boolean).join(". ")
  }

  if (status === 401) {
    return "Invalid email or password"
  }

  if (status === 409) {
    return "Email already registered"
  }

  return "Request failed"
}
