import type { ReactNode } from "react"

import { Badge } from "@/components/ui/badge"
import { BotMessageSquareIcon, SparklesIcon } from "lucide-react"

type AuthLayoutProps = {
  eyebrow: string
  title: string
  description: string
  children: ReactNode
}

export function AuthLayout({
  eyebrow,
  title,
  description,
  children,
}: AuthLayoutProps) {
  return (
    <main className="min-h-svh bg-background text-foreground">
      <div className="grid min-h-svh lg:grid-cols-[1.05fr_0.95fr]">
        <section className="hidden flex-col justify-between border-r bg-card/30 p-10 lg:flex">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
              <BotMessageSquareIcon />
            </div>
            <div>
              <div className="font-semibold">CommerceBot</div>
              <div className="text-sm text-muted-foreground">
                WhatsApp fashion sales assistant
              </div>
            </div>
          </div>

          <div className="max-w-2xl">
            <Badge variant="secondary" className="mb-6 rounded-full">
              <SparklesIcon />
              {eyebrow}
            </Badge>
            <h1 className="text-6xl font-semibold leading-none tracking-normal xl:text-7xl">
              Sell fashion through conversation.
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground">
              Manage products, orders, customers, and chat-driven checkout from
              one dark admin workspace.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3 text-sm text-muted-foreground">
            <div className="rounded-2xl bg-muted/40 p-4">
              <div className="text-2xl font-semibold text-foreground">24/7</div>
              <div>chat response</div>
            </div>
            <div className="rounded-2xl bg-muted/40 p-4">
              <div className="text-2xl font-semibold text-foreground">WAHA</div>
              <div>WhatsApp gateway</div>
            </div>
            <div className="rounded-2xl bg-muted/40 p-4">
              <div className="text-2xl font-semibold text-foreground">IDR</div>
              <div>Midtrans ready</div>
            </div>
          </div>
        </section>

        <section className="flex min-h-svh items-center justify-center p-4 sm:p-6 lg:p-10">
          <div className="w-full max-w-md">
            <div className="mb-8 lg:hidden">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground">
                  <BotMessageSquareIcon />
                </div>
                <div>
                  <div className="font-semibold">CommerceBot</div>
                  <div className="text-sm text-muted-foreground">
                    WhatsApp fashion dashboard
                  </div>
                </div>
              </div>
              <h1 className="text-3xl font-semibold tracking-normal">{title}</h1>
              <p className="mt-2 text-sm text-muted-foreground">{description}</p>
            </div>
            <div className="hidden lg:block">
              <h2 className="text-3xl font-semibold tracking-normal">{title}</h2>
              <p className="mt-2 text-sm text-muted-foreground">{description}</p>
            </div>
            <div className="mt-6">{children}</div>
          </div>
        </section>
      </div>
    </main>
  )
}
