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
  ClockIcon,
  PackageCheckIcon,
  ShoppingCartIcon,
  TruckIcon,
} from "lucide-react"

type OrderStatus =
  | "draft"
  | "waiting_payment"
  | "paid"
  | "processing"
  | "shipped"
  | "completed"
  | "cancelled"
  | "expired"

type PaymentStatus =
  | "unpaid"
  | "pending"
  | "paid"
  | "failed"
  | "expired"
  | "cancelled"
  | "refunded"

type ShippingStatus =
  | "not_created"
  | "waiting_pickup"
  | "picked_up"
  | "in_transit"
  | "delivered"
  | "failed"
  | "cancelled"

type Order = {
  id: number
  orderNumber: string
  customerName: string
  customerPhone: string
  status: OrderStatus
  paymentStatus: PaymentStatus
  shippingStatus: ShippingStatus
  subtotal: number
  shippingCost: number
  discountTotal: number
  serviceFee: number
  grandTotal: number
  currency: "IDR"
  itemsCount: number
  createdAt: string
  expiredAt?: string
  paidAt?: string
}

const orders: Order[] = [
  {
    id: 1,
    orderNumber: "ORD-20260531-0001",
    customerName: "Nadia Putri",
    customerPhone: "+62 812-4400-1188",
    status: "waiting_payment",
    paymentStatus: "pending",
    shippingStatus: "not_created",
    subtotal: 368000,
    shippingCost: 18000,
    discountTotal: 0,
    serviceFee: 4000,
    grandTotal: 390000,
    currency: "IDR",
    itemsCount: 2,
    createdAt: "2026-05-31T01:20:00+07:00",
    expiredAt: "2026-05-31T03:20:00+07:00",
  },
  {
    id: 2,
    orderNumber: "ORD-20260530-0018",
    customerName: "Raka Mahendra",
    customerPhone: "+62 857-2100-9021",
    status: "processing",
    paymentStatus: "paid",
    shippingStatus: "waiting_pickup",
    subtotal: 249000,
    shippingCost: 22000,
    discountTotal: 10000,
    serviceFee: 4000,
    grandTotal: 265000,
    currency: "IDR",
    itemsCount: 1,
    createdAt: "2026-05-30T20:42:00+07:00",
    paidAt: "2026-05-30T20:51:00+07:00",
  },
  {
    id: 3,
    orderNumber: "ORD-20260530-0017",
    customerName: "Sinta Amelia",
    customerPhone: "+62 813-9000-3321",
    status: "shipped",
    paymentStatus: "paid",
    shippingStatus: "in_transit",
    subtotal: 318000,
    shippingCost: 16000,
    discountTotal: 0,
    serviceFee: 4000,
    grandTotal: 338000,
    currency: "IDR",
    itemsCount: 2,
    createdAt: "2026-05-30T15:11:00+07:00",
    paidAt: "2026-05-30T15:19:00+07:00",
  },
  {
    id: 4,
    orderNumber: "ORD-20260529-0042",
    customerName: "Dimas Ardi",
    customerPhone: "+62 821-7700-6611",
    status: "completed",
    paymentStatus: "paid",
    shippingStatus: "delivered",
    subtotal: 199000,
    shippingCost: 14000,
    discountTotal: 0,
    serviceFee: 4000,
    grandTotal: 217000,
    currency: "IDR",
    itemsCount: 1,
    createdAt: "2026-05-29T11:08:00+07:00",
    paidAt: "2026-05-29T11:15:00+07:00",
  },
  {
    id: 5,
    orderNumber: "ORD-20260529-0039",
    customerName: "Maya Lestari",
    customerPhone: "+62 878-1200-4477",
    status: "cancelled",
    paymentStatus: "cancelled",
    shippingStatus: "cancelled",
    subtotal: 289000,
    shippingCost: 21000,
    discountTotal: 0,
    serviceFee: 4000,
    grandTotal: 314000,
    currency: "IDR",
    itemsCount: 1,
    createdAt: "2026-05-29T09:34:00+07:00",
    expiredAt: "2026-05-29T11:34:00+07:00",
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

const statusText = (value: string) =>
  value
    .split("_")
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(" ")

function StatusBadge({ value }: { value: OrderStatus | PaymentStatus | ShippingStatus }) {
  const isGood = value === "paid" || value === "completed" || value === "delivered"
  const isBad = value === "cancelled" || value === "expired" || value === "failed"

  if (isBad) {
    return <Badge variant="destructive">{statusText(value)}</Badge>
  }

  return <Badge variant={isGood ? "default" : "secondary"}>{statusText(value)}</Badge>
}

function OrderStat({
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

export function OrdersRoute() {
  const waitingPayment = orders.filter(
    (order) => order.status === "waiting_payment" || order.paymentStatus === "pending"
  ).length
  const paid = orders.filter((order) => order.paymentStatus === "paid").length
  const inTransit = orders.filter(
    (order) => order.shippingStatus === "in_transit" || order.status === "shipped"
  ).length
  const revenue = orders
    .filter((order) => order.paymentStatus === "paid")
    .reduce((total, order) => total + order.grandTotal, 0)

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-5 p-4 lg:p-6">
        <section className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold tracking-normal">Orders</h1>
          <p className="text-sm text-muted-foreground">
            Pantau order WhatsApp, payment Midtrans, dan shipping Biteship.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <OrderStat
            title="Total orders"
            value={String(orders.length)}
            description="Semua order di dashboard admin."
            icon={<ShoppingCartIcon />}
          />
          <OrderStat
            title="Waiting payment"
            value={String(waitingPayment)}
            description="Order menunggu pembayaran customer."
            icon={<ClockIcon />}
          />
          <OrderStat
            title="Paid revenue"
            value={formatCurrency(revenue)}
            description={`${paid} order sudah dibayar.`}
            icon={<BanknoteIcon />}
          />
          <OrderStat
            title="In transit"
            value={String(inTransit)}
            description="Paket sedang dikirim ke customer."
            icon={<TruckIcon />}
          />
        </section>

        <Card className="bg-card/95">
          <CardHeader className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Order list</CardTitle>
              <CardDescription>
                Data mock mengikuti struktur Orders dari ERD MVP.
              </CardDescription>
            </div>
            <Badge variant="outline">
              <PackageCheckIcon />
              {orders.length} records
            </Badge>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Payment</TableHead>
                  <TableHead>Shipping</TableHead>
                  <TableHead>Items</TableHead>
                  <TableHead className="text-right">Grand total</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead>Paid / Expired</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {orders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell>
                      <div className="font-medium">{order.orderNumber}</div>
                      <div className="text-xs text-muted-foreground">{order.currency}</div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{order.customerName}</div>
                      <div className="text-xs text-muted-foreground">{order.customerPhone}</div>
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={order.status} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={order.paymentStatus} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={order.shippingStatus} />
                    </TableCell>
                    <TableCell>{order.itemsCount}</TableCell>
                    <TableCell className="text-right font-medium tabular-nums">
                      {formatCurrency(order.grandTotal)}
                    </TableCell>
                    <TableCell>{formatDate(order.createdAt)}</TableCell>
                    <TableCell>{formatDate(order.paidAt ?? order.expiredAt)}</TableCell>
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
