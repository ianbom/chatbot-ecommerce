import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { DashboardLayout } from "@/layouts/dashboard-layout"
import {
  CirclePlusIcon,
  SearchIcon,
  SparklesIcon,
  TriangleAlertIcon,
} from "lucide-react"

type ProductStatus = "draft" | "active" | "inactive" | "archived"
type ProductGender = "men" | "women" | "unisex"

type Product = {
  id: number
  name: string
  slug: string
  description: string
  imageUrl: string
  category: string
  price: number
  stockQty: number
  reservedQty: number
  lowStockThreshold: number
  color: string
  size: string
  gender: ProductGender
  material: string
  weightGram: number
  status: ProductStatus
  isFeatured: boolean
}

const products: Product[] = [
  {
    id: 1,
    name: "Oversized Hoodie Black Size L",
    slug: "oversized-hoodie-black-l",
    description: "Heavy cotton fleece hoodie for WhatsApp product recommendation.",
    imageUrl:
      "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=900&q=80",
    category: "Hoodie",
    price: 249000,
    stockQty: 8,
    reservedQty: 2,
    lowStockThreshold: 5,
    color: "Black",
    size: "L",
    gender: "unisex",
    material: "Cotton fleece",
    weightGram: 650,
    status: "active",
    isFeatured: true,
  },
  {
    id: 2,
    name: "Relaxed T-Shirt White Size M",
    slug: "relaxed-t-shirt-white-m",
    description: "Soft daily tee with clean fit and fast-moving chat demand.",
    imageUrl:
      "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=900&q=80",
    category: "T-Shirt",
    price: 119000,
    stockQty: 24,
    reservedQty: 4,
    lowStockThreshold: 8,
    color: "White",
    size: "M",
    gender: "unisex",
    material: "Cotton combed 24s",
    weightGram: 220,
    status: "active",
    isFeatured: true,
  },
  {
    id: 3,
    name: "Wide Leg Pants Sand Size 32",
    slug: "wide-leg-pants-sand-32",
    description: "Structured pants item used by chatbot for outfit pairing.",
    imageUrl:
      "https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=900&q=80",
    category: "Pants",
    price: 199000,
    stockQty: 3,
    reservedQty: 1,
    lowStockThreshold: 5,
    color: "Sand",
    size: "32",
    gender: "men",
    material: "Twill cotton",
    weightGram: 520,
    status: "active",
    isFeatured: false,
  },
  {
    id: 4,
    name: "Boxy Crop Shirt Navy Size S",
    slug: "boxy-crop-shirt-navy-s",
    description: "Draft fashion item waiting for final stock and content check.",
    imageUrl:
      "https://images.unsplash.com/photo-1485462537746-965f33f7f6a7?auto=format&fit=crop&w=900&q=80",
    category: "Shirt",
    price: 159000,
    stockQty: 0,
    reservedQty: 0,
    lowStockThreshold: 5,
    color: "Navy",
    size: "S",
    gender: "women",
    material: "Rayon blend",
    weightGram: 260,
    status: "draft",
    isFeatured: false,
  },
  {
    id: 5,
    name: "Coach Jacket Olive Size XL",
    slug: "coach-jacket-olive-xl",
    description: "Inactive item kept for historical leads and product analytics.",
    imageUrl:
      "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=900&q=80",
    category: "Outerwear",
    price: 289000,
    stockQty: 12,
    reservedQty: 0,
    lowStockThreshold: 4,
    color: "Olive",
    size: "XL",
    gender: "men",
    material: "Taslan",
    weightGram: 470,
    status: "inactive",
    isFeatured: false,
  },
]

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(value)

const statusLabel: Record<ProductStatus, string> = {
  active: "Active",
  draft: "Draft",
  inactive: "Inactive",
  archived: "Archived",
}

function ProductStatusBadge({ status }: { status: ProductStatus }) {
  return (
    <Badge variant={status === "active" ? "default" : "secondary"}>
      {statusLabel[status]}
    </Badge>
  )
}

function ProductCard({ product }: { product: Product }) {
  const availableStock = product.stockQty - product.reservedQty
  const lowStock = availableStock <= product.lowStockThreshold

  return (
    <Card className="overflow-hidden border-border/70 bg-card/95 shadow-sm">
      <div className="aspect-[4/3] overflow-hidden bg-muted">
        <img
          src={product.imageUrl}
          alt={product.name}
          className="size-full object-cover"
        />
      </div>
      <CardHeader className="gap-3 p-4">
        <div className="flex flex-wrap items-center gap-2">
          <ProductStatusBadge status={product.status} />
          {product.isFeatured ? (
            <Badge variant="outline">
              <SparklesIcon />
              Featured
            </Badge>
          ) : null}
          {lowStock ? (
            <Badge variant="destructive">
              <TriangleAlertIcon />
              Low
            </Badge>
          ) : null}
        </div>
        <div className="min-w-0">
          <CardTitle className="line-clamp-2 text-base leading-tight">
            {product.name}
          </CardTitle>
          <CardDescription className="mt-1 truncate">
            {product.category} / {product.color} / {product.size}
          </CardDescription>
        </div>
      </CardHeader>
      <CardContent className="flex flex-col gap-3 p-4 pt-0">
        <div className="flex items-center justify-between gap-3">
          <div className="text-lg font-semibold tabular-nums">
            {formatCurrency(product.price)}
          </div>
          <div className="text-xs text-muted-foreground">{product.gender}</div>
        </div>
        <div className="grid grid-cols-3 gap-2 rounded-xl bg-muted/30 p-3 text-sm">
          <div>
            <div className="text-xs text-muted-foreground">Stock</div>
            <div className="font-semibold tabular-nums">{product.stockQty}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Hold</div>
            <div className="font-semibold tabular-nums">{product.reservedQty}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Ready</div>
            <div className="font-semibold tabular-nums">{availableStock}</div>
          </div>
        </div>
        <Button variant="secondary" size="sm" className="w-full rounded-full">
          Manage
        </Button>
      </CardContent>
    </Card>
  )
}

export function ProductsRoute() {
  return (
    <DashboardLayout>
      <div className="flex flex-col gap-5 p-4 lg:p-6">
        <section className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-normal">Products</h1>
            <p className="text-sm text-muted-foreground">
              List product kecil untuk katalog fashion chatbot.
            </p>
          </div>
          <Button className="rounded-full">
            <CirclePlusIcon data-icon="inline-start" />
            Add product
          </Button>
        </section>

        <section className="flex flex-col gap-4">
          <div className="flex flex-col gap-3 rounded-2xl border bg-card/80 p-3 md:flex-row md:items-center md:justify-between">
            <div className="relative flex-1">
              <SearchIcon className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Search products"
                placeholder="Search by product name, slug, color, or size"
                className="h-11 rounded-full pl-10"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">active</Badge>
              <Badge variant="outline">draft</Badge>
              <Badge variant="outline">low stock</Badge>
              <Badge variant="outline">featured</Badge>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </section>
      </div>
    </DashboardLayout>
  )
}
