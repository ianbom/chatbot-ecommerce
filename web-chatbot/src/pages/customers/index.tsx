import type { ReactNode } from "react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { DashboardLayout } from "@/layouts/dashboard-layout"
import {
  BanknoteIcon,
  MessageCircleIcon,
  RepeatIcon,
  UserRoundIcon,
} from "lucide-react"

type CustomerSource = "chatbot_web" | "whatsapp" | "manual_admin"

type Customer = {
  id: number
  name?: string
  email?: string
  phone?: string
  source: CustomerSource
  firstSeenAt?: string
  lastSeenAt?: string
  totalOrders: number
  totalSpent: number
  createdAt: string
}

const customers: Customer[] = [
  {
    id: 1,
    name: "Nadia Putri",
    email: "nadia.putri@example.com",
    phone: "+62 812-4400-1188",
    source: "whatsapp",
    firstSeenAt: "2026-05-21T13:12:00+07:00",
    lastSeenAt: "2026-05-31T01:20:00+07:00",
    totalOrders: 3,
    totalSpent: 824000,
    createdAt: "2026-05-21T13:12:00+07:00",
  },
  {
    id: 2,
    name: "Raka Mahendra",
    email: "raka@example.com",
    phone: "+62 857-2100-9021",
    source: "whatsapp",
    firstSeenAt: "2026-05-18T08:44:00+07:00",
    lastSeenAt: "2026-05-30T20:42:00+07:00",
    totalOrders: 2,
    totalSpent: 514000,
    createdAt: "2026-05-18T08:44:00+07:00",
  },
  {
    id: 3,
    name: "Sinta Amelia",
    phone: "+62 813-9000-3321",
    source: "whatsapp",
    firstSeenAt: "2026-05-25T18:10:00+07:00",
    lastSeenAt: "2026-05-30T15:11:00+07:00",
    totalOrders: 1,
    totalSpent: 338000,
    createdAt: "2026-05-25T18:10:00+07:00",
  },
  {
    id: 4,
    name: "Dimas Ardi",
    email: "dimas.ardi@example.com",
    phone: "+62 821-7700-6611",
    source: "chatbot_web",
    firstSeenAt: "2026-05-27T10:03:00+07:00",
    lastSeenAt: "2026-05-29T11:08:00+07:00",
    totalOrders: 1,
    totalSpent: 217000,
    createdAt: "2026-05-27T10:03:00+07:00",
  },
  {
    id: 5,
    name: "Maya Lestari",
    phone: "+62 878-1200-4477",
    source: "manual_admin",
    firstSeenAt: "2026-05-29T09:34:00+07:00",
    lastSeenAt: "2026-05-29T09:34:00+07:00",
    totalOrders: 0,
    totalSpent: 0,
    createdAt: "2026-05-29T09:34:00+07:00",
  },
]

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(value)

const formatDate = (value?: string) => {
  if (!value) return "-"

  return new Intl.DateTimeFormat("id-ID", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value))
}

const sourceLabel: Record<CustomerSource, string> = {
  chatbot_web: "Web Chatbot",
  whatsapp: "WhatsApp",
  manual_admin: "Manual Admin",
}

function CustomerSourceBadge({ source }: { source: CustomerSource }) {
  return <Badge variant={source === "whatsapp" ? "default" : "secondary"}>{sourceLabel[source]}</Badge>
}

function CustomerStat({
  title,
  value,
  description,
  icon,
}: {
  title: string
  value: string
  description: string
  icon: ReactNode
}) {
  return (
    <Card className="bg-card/90">
      <CardHeader className="flex flex-row items-start justify-between gap-3 pb-2">
        <div>
          <CardDescription>{title}</CardDescription>
          <CardTitle className="mt-2 text-2xl tabular-nums">{value}</CardTitle>
        </div>
        <div className="flex size-10 items-center justify-center rounded-full bg-muted">
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}

export function CustomersRoute() {
  const whatsappCustomers = customers.filter(
    (customer) => customer.source === "whatsapp"
  ).length
  const repeatBuyers = customers.filter((customer) => customer.totalOrders > 1).length
  const totalSpent = customers.reduce(
    (total, customer) => total + customer.totalSpent,
    0
  )

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-5 p-4 lg:p-6">
        <section className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold tracking-normal">Customers</h1>
          <p className="text-sm text-muted-foreground">
            Customer dari WhatsApp, web chatbot, dan input manual admin.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <CustomerStat
            title="Total customers"
            value={String(customers.length)}
            description="Seluruh customer yang tersimpan."
            icon={<UserRoundIcon />}
          />
          <CustomerStat
            title="WhatsApp customers"
            value={String(whatsappCustomers)}
            description="Customer otomatis dari pesan WAHA."
            icon={<MessageCircleIcon />}
          />
          <CustomerStat
            title="Repeat buyers"
            value={String(repeatBuyers)}
            description="Customer dengan lebih dari satu order."
            icon={<RepeatIcon />}
          />
          <CustomerStat
            title="Total spent"
            value={formatCurrency(totalSpent)}
            description="Akumulasi revenue dari customer."
            icon={<BanknoteIcon />}
          />
        </section>

        <Card className="bg-card/95">
          <CardHeader className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Customer list</CardTitle>
              <CardDescription>
                Data mock mengikuti struktur Customers dari ERD MVP.
              </CardDescription>
            </div>
            <Badge variant="outline">{customers.length} records</Badge>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Customer</TableHead>
                  <TableHead>Phone</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Source</TableHead>
                  <TableHead className="text-right">Orders</TableHead>
                  <TableHead className="text-right">Total spent</TableHead>
                  <TableHead>First seen</TableHead>
                  <TableHead>Last seen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {customers.map((customer) => (
                  <TableRow key={customer.id}>
                    <TableCell>
                      <div className="font-medium">{customer.name ?? "Unknown customer"}</div>
                      <div className="text-xs text-muted-foreground">ID #{customer.id}</div>
                    </TableCell>
                    <TableCell>{customer.phone ?? "-"}</TableCell>
                    <TableCell>{customer.email ?? "-"}</TableCell>
                    <TableCell>
                      <CustomerSourceBadge source={customer.source} />
                    </TableCell>
                    <TableCell className="text-right tabular-nums">
                      {customer.totalOrders}
                    </TableCell>
                    <TableCell className="text-right font-medium tabular-nums">
                      {formatCurrency(customer.totalSpent)}
                    </TableCell>
                    <TableCell>{formatDate(customer.firstSeenAt)}</TableCell>
                    <TableCell>{formatDate(customer.lastSeenAt)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
