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
  BadgeCheckIcon,
  FlameIcon,
  GaugeIcon,
  TargetIcon,
} from "lucide-react"

type LeadStatus = "new" | "interested" | "hot" | "converted" | "lost"

type Lead = {
  id: number
  customerName: string
  customerPhone: string
  status: LeadStatus
  leadScore: number
  interestSummary: string
  interestedProducts: string[]
  assignedTo?: string
  convertedOrderNumber?: string
  lastContactedAt?: string
  createdAt: string
  updatedAt: string
}

const leads: Lead[] = [
  {
    id: 1,
    customerName: "Nadia Putri",
    customerPhone: "+62 812-4400-1188",
    status: "hot",
    leadScore: 85,
    interestSummary: "Mencari hoodie hitam size L dan tanya ongkir Bandung.",
    interestedProducts: ["Oversized Hoodie Black L", "Relaxed T-Shirt White M"],
    assignedTo: "Admin Store",
    lastContactedAt: "2026-05-31T01:18:00+07:00",
    createdAt: "2026-05-30T22:40:00+07:00",
    updatedAt: "2026-05-31T01:18:00+07:00",
  },
  {
    id: 2,
    customerName: "Raka Mahendra",
    customerPhone: "+62 857-2100-9021",
    status: "converted",
    leadScore: 100,
    interestSummary: "Checkout hoodie dan berhasil bayar via Midtrans.",
    interestedProducts: ["Oversized Hoodie Black L"],
    assignedTo: "Admin Store",
    convertedOrderNumber: "ORD-20260530-0018",
    lastContactedAt: "2026-05-30T20:51:00+07:00",
    createdAt: "2026-05-30T19:12:00+07:00",
    updatedAt: "2026-05-30T20:51:00+07:00",
  },
  {
    id: 3,
    customerName: "Sinta Amelia",
    customerPhone: "+62 813-9000-3321",
    status: "interested",
    leadScore: 45,
    interestSummary: "Tanya rekomendasi outfit casual dan warna navy.",
    interestedProducts: ["Boxy Crop Shirt Navy S", "Wide Leg Pants Sand 32"],
    assignedTo: "Sales Staff",
    lastContactedAt: "2026-05-30T15:05:00+07:00",
    createdAt: "2026-05-30T14:43:00+07:00",
    updatedAt: "2026-05-30T15:05:00+07:00",
  },
  {
    id: 4,
    customerName: "Dimas Ardi",
    customerPhone: "+62 821-7700-6611",
    status: "new",
    leadScore: 20,
    interestSummary: "Baru bertanya stok celana sand size 32.",
    interestedProducts: ["Wide Leg Pants Sand 32"],
    createdAt: "2026-05-29T11:04:00+07:00",
    updatedAt: "2026-05-29T11:04:00+07:00",
  },
  {
    id: 5,
    customerName: "Maya Lestari",
    customerPhone: "+62 878-1200-4477",
    status: "lost",
    leadScore: 10,
    interestSummary: "Tanya outerwear, tidak lanjut setelah harga dikirim.",
    interestedProducts: ["Coach Jacket Olive XL"],
    assignedTo: "Sales Staff",
    lastContactedAt: "2026-05-29T09:40:00+07:00",
    createdAt: "2026-05-29T09:34:00+07:00",
    updatedAt: "2026-05-29T09:40:00+07:00",
  },
]

const formatDate = (value?: string) => {
  if (!value) return "-"

  return new Intl.DateTimeFormat("id-ID", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value))
}

const statusLabel: Record<LeadStatus, string> = {
  new: "New",
  interested: "Interested",
  hot: "Hot",
  converted: "Converted",
  lost: "Lost",
}

function LeadStatusBadge({ status }: { status: LeadStatus }) {
  if (status === "lost") {
    return <Badge variant="destructive">{statusLabel[status]}</Badge>
  }

  return (
    <Badge variant={status === "hot" || status === "converted" ? "default" : "secondary"}>
      {statusLabel[status]}
    </Badge>
  )
}

function LeadStat({
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

export function LeadsRoute() {
  const hotLeads = leads.filter((lead) => lead.status === "hot").length
  const convertedLeads = leads.filter((lead) => lead.status === "converted").length
  const averageScore = Math.round(
    leads.reduce((total, lead) => total + lead.leadScore, 0) / leads.length
  )

  return (
    <DashboardLayout>
      <div className="flex flex-col gap-5 p-4 lg:p-6">
        <section className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold tracking-normal">Leads</h1>
          <p className="text-sm text-muted-foreground">
            Pantau minat customer dari percakapan WhatsApp dan aktivitas produk.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <LeadStat
            title="Total leads"
            value={String(leads.length)}
            description="Semua lead dari chat dan admin."
            icon={<TargetIcon />}
          />
          <LeadStat
            title="Hot leads"
            value={String(hotLeads)}
            description="Lead prioritas dengan score tinggi."
            icon={<FlameIcon />}
          />
          <LeadStat
            title="Converted"
            value={String(convertedLeads)}
            description="Lead yang berubah jadi order paid."
            icon={<BadgeCheckIcon />}
          />
          <LeadStat
            title="Average score"
            value={String(averageScore)}
            description="Rata-rata lead score saat ini."
            icon={<GaugeIcon />}
          />
        </section>

        <Card className="bg-card/95">
          <CardHeader className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Lead list</CardTitle>
              <CardDescription>
                Data mock mengikuti struktur Leads dari ERD MVP.
              </CardDescription>
            </div>
            <Badge variant="outline">{leads.length} records</Badge>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Customer</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Score</TableHead>
                  <TableHead>Interest</TableHead>
                  <TableHead>Products</TableHead>
                  <TableHead>Assigned</TableHead>
                  <TableHead>Converted order</TableHead>
                  <TableHead>Last contacted</TableHead>
                  <TableHead>Updated</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leads.map((lead) => (
                  <TableRow key={lead.id}>
                    <TableCell>
                      <div className="font-medium">{lead.customerName}</div>
                      <div className="text-xs text-muted-foreground">{lead.customerPhone}</div>
                    </TableCell>
                    <TableCell>
                      <LeadStatusBadge status={lead.status} />
                    </TableCell>
                    <TableCell className="text-right font-medium tabular-nums">
                      {lead.leadScore}
                    </TableCell>
                    <TableCell className="max-w-xs">
                      <div className="truncate">{lead.interestSummary}</div>
                    </TableCell>
                    <TableCell>
                      <div className="flex max-w-xs flex-wrap gap-1">
                        {lead.interestedProducts.map((product) => (
                          <Badge key={product} variant="secondary">
                            {product}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>{lead.assignedTo ?? "-"}</TableCell>
                    <TableCell>{lead.convertedOrderNumber ?? "-"}</TableCell>
                    <TableCell>{formatDate(lead.lastContactedAt)}</TableCell>
                    <TableCell>{formatDate(lead.updatedAt)}</TableCell>
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
