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
import { ArrowRightIcon, UserPlusIcon } from "lucide-react"

export function RegisterRoute() {
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
          <form className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="Store Admin"
                autoComplete="name"
                className="h-11 rounded-xl"
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="register-email">Email</Label>
              <Input
                id="register-email"
                type="email"
                placeholder="admin@store.com"
                autoComplete="email"
                className="h-11 rounded-xl"
              />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="register-password">Password</Label>
              <Input
                id="register-password"
                type="password"
                placeholder="••••••••"
                autoComplete="new-password"
                className="h-11 rounded-xl"
              />
            </div>
            <Button type="submit" className="mt-2 h-11 rounded-full">
              <UserPlusIcon data-icon="inline-start" />
              Create account
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
