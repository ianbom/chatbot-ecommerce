import { Link } from "react-router-dom"

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
import { ArrowRightIcon, MailIcon } from "lucide-react"

export function LoginRoute() {
  return (
    <AuthLayout
      eyebrow="Admin sign in"
      title="Welcome back"
      description="Login menggunakan email dan password admin."
    >
      <Card className="rounded-3xl bg-card/95 shadow-sm">
        <CardHeader>
          <CardTitle>Sign in</CardTitle>
          <CardDescription>
            Masuk untuk mengelola produk, order, dan chat customer.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="admin@store.com"
                autoComplete="email"
                className="h-11 rounded-xl"
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                autoComplete="current-password"
                className="h-11 rounded-xl"
              />
            </div>
            <Button type="submit" className="mt-2 h-11 rounded-full">
              <MailIcon data-icon="inline-start" />
              Sign in
              <ArrowRightIcon data-icon="inline-end" />
            </Button>
          </form>
        </CardContent>
        <CardFooter className="justify-center border-t text-sm text-muted-foreground">
          Belum punya akun?{" "}
          <Link to="/register" className="font-medium text-foreground underline-offset-4 hover:underline">
            Create account
          </Link>
        </CardFooter>
      </Card>
    </AuthLayout>
  )
}
