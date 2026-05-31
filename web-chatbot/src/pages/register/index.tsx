import { useState, type FormEvent } from "react"
import { Link, useNavigate } from "react-router-dom"

import { useAuth } from "@/auth/auth-context"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AuthLayout } from "@/layouts/auth-layout"
import { ArrowRightIcon, UserPlusIcon } from "lucide-react"

export function RegisterRoute() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (password.length < 8) {
      setError("Password must be at least 8 characters")
      return
    }

    setIsSubmitting(true)

    try {
      await register({ name, email, password })
      navigate("/dashboard", { replace: true })
    } catch (error) {
      setError(error instanceof Error ? error.message : "Registration failed")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <AuthLayout
      eyebrow="Create admin account"
      title="Start your dashboard"
      description="Buat akun admin untuk mengakses CommerceBot dashboard."
    >
      <Card className="rounded-3xl bg-card/95 shadow-sm">
        <CardHeader>
          <CardTitle>Create account</CardTitle>
          <CardDescription>
            Data mengikuti tabel Users: name, email, password.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Store Admin"
                autoComplete="name"
                className="h-11 rounded-xl"
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="register-email">Email</Label>
              <Input
                id="register-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="admin@store.com"
                autoComplete="email"
                className="h-11 rounded-xl"
                required
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="register-password">Password</Label>
              <Input
                id="register-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••"
                autoComplete="new-password"
                className="h-11 rounded-xl"
                minLength={8}
                required
              />
            </div>
            {error ? (
              <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {error}
              </div>
            ) : null}
            <Button
              type="submit"
              className="mt-2 h-11 rounded-full"
              disabled={isSubmitting}
            >
              <UserPlusIcon data-icon="inline-start" />
              {isSubmitting ? "Creating account..." : "Create account"}
              <ArrowRightIcon data-icon="inline-end" />
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center border-t text-sm text-muted-foreground">
          Sudah punya akun?{" "}
          <Link to="/login" className="font-medium text-foreground underline-offset-4 hover:underline">
            Sign in
          </Link>
        </CardFooter>
      </Card>
    </AuthLayout>
  )
}
