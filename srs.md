# Software Requirements Specification (SRS)

# AI WhatsApp Chatbot E-Commerce Fashion

**Version:** 1.0  
**Status:** MVP Specification  
**Primary Channel:** WhatsApp via WAHA  
**Frontend:** React TypeScript, Vite, Tailwind CSS, shadcn/ui, TanStack Query  
**Backend:** FastAPI, Pydantic, SQLAlchemy/SQLModel, Alembic  
**Database:** PostgreSQL  
**Integrations:** WAHA, Midtrans, Biteship, AI LLM  

---

## 1. Introduction

### 1.1 Purpose

Dokumen ini menjelaskan kebutuhan perangkat lunak untuk project **AI WhatsApp Chatbot E-Commerce Fashion**. Sistem ini memungkinkan customer berbelanja pakaian melalui WhatsApp, mulai dari bertanya produk, mendapatkan rekomendasi, booking produk, checkout, memilih pengiriman, melakukan pembayaran, hingga mengecek status order.

SRS ini menjadi acuan untuk tim product, backend, frontend, AI engineer, QA, dan stakeholder bisnis.

### 1.2 Scope

Sistem terdiri dari:

- WhatsApp chatbot menggunakan WAHA.
- Backend API menggunakan FastAPI.
- Admin dashboard menggunakan React TypeScript.
- Database menggunakan PostgreSQL.
- Pembayaran menggunakan Midtrans.
- Pengiriman menggunakan Biteship.
- AI chatbot menggunakan LLM dengan tool calling.

Untuk MVP, produk dibuat sederhana dengan satu tabel `Products`. Tidak ada product variant, product image table, dan product category table terpisah.

### 1.3 System Overview

```txt
Customer WhatsApp
→ WAHA
→ FastAPI Webhook
→ AI Chatbot + Business Logic
→ PostgreSQL
→ Midtrans / Biteship
→ FastAPI
→ WAHA
→ Customer WhatsApp
```

Admin menggunakan dashboard web untuk mengelola produk, stok, customer, leads, chat, order, payment, shipping, dan analytics.

---

## 2. Overall Description

### 2.1 User Classes

| User | Description |
|---|---|
| Customer | Pembeli yang berinteraksi melalui WhatsApp |
| Admin | Pengelola toko melalui dashboard |
| Staff | User internal dengan akses terbatas |

### 2.2 Operating Environment

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy atau SQLModel
- Alembic
- PostgreSQL

Frontend:

- React TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- TanStack Query

External systems:

- WAHA untuk WhatsApp API
- Midtrans untuk payment
- Biteship untuk shipping
- LLM provider untuk AI chatbot

### 2.3 Assumptions

- Nomor WhatsApp toko sudah terhubung ke WAHA.
- WAHA dapat mengirim webhook ke FastAPI.
- Midtrans dan Biteship API key tersedia.
- Customer diidentifikasi dari nomor WhatsApp.
- Satu baris produk merepresentasikan satu item spesifik, misalnya `Hoodie Black Size L`.

### 2.4 Constraints

- WhatsApp integration wajib menggunakan WAHA.
- Payment wajib menggunakan Midtrans.
- Shipping wajib menggunakan Biteship.
- Produk MVP hanya memakai satu tabel `Products`.
- AI tidak boleh mengarang produk, harga, stok, order, payment, atau ongkir.
- Semua aksi penting harus dilakukan melalui backend tools.

---

## 3. Functional Requirements

## 3.1 Authentication and User Management

### FR-AUTH-001 — Admin Login

**Priority:** Must

Sistem harus menyediakan login admin menggunakan email dan password.

**Acceptance Criteria:**

- Admin dapat login dengan kredensial valid.
- Password disimpan dalam bentuk hash.
- Login gagal jika email atau password salah.
- Sistem mengembalikan token/session setelah login berhasil.

### FR-AUTH-002 — Role Management

**Priority:** Should

Sistem harus mendukung role:

```txt
superadmin
admin
staff
```

**Acceptance Criteria:**

- Setiap user memiliki role.
- API admin hanya dapat diakses oleh user terautentikasi.
- Akses fitur dapat dibatasi berdasarkan role.

---

## 3.2 Customer Management

### FR-CUST-001 — Auto Create Customer from WhatsApp

**Priority:** Must

Sistem harus otomatis membuat customer ketika menerima pesan dari nomor WhatsApp baru.

**Acceptance Criteria:**

- Customer dibuat jika nomor belum terdaftar.
- `Customers.phone` berisi nomor WhatsApp.
- `Customers.source` bernilai `whatsapp`.
- `first_seen_at` dan `last_seen_at` tersimpan.

### FR-CUST-002 — Customer Address

**Priority:** Must

Sistem harus dapat menyimpan alamat customer saat checkout.

**Acceptance Criteria:**

- Alamat tersimpan di `CustomerAddresses`.
- Data alamat mencakup nama penerima, nomor penerima, kota, kecamatan, kode pos, dan detail alamat.
- Alamat digunakan untuk mengambil ongkir dari Biteship.

---

## 3.3 Product Management

### FR-PROD-001 — Create Product

**Priority:** Must

Admin harus dapat membuat produk.

**Fields:**

- name
- slug
- description
- image_url
- category
- price
- stock_qty
- reserved_qty
- low_stock_threshold
- color
- size
- gender
- material
- weight_gram
- length_cm
- width_cm
- height_cm
- status
- is_featured

**Acceptance Criteria:**

- Produk tersimpan di `Products`.
- `name`, `slug`, dan `price` wajib diisi.
- `slug` harus unik.
- Produk memiliki status `draft`, `active`, `inactive`, atau `archived`.

### FR-PROD-002 — Product Search

**Priority:** Must

Chatbot dan admin dashboard harus dapat mencari produk.

**Acceptance Criteria:**

- Produk dapat dicari berdasarkan nama, kategori, warna, ukuran, gender, dan status.
- Chatbot hanya menampilkan produk `active`.
- Produk out of stock tidak disebut ready stock.

### FR-PROD-003 — Update Product

**Priority:** Must

Admin harus dapat mengubah data produk.

**Acceptance Criteria:**

- Admin dapat mengubah harga, stok, deskripsi, gambar, ukuran, warna, dan status.
- `updated_at` diperbarui.
- Produk soft deleted tidak tampil ke customer.

---

## 3.4 Stock Management

### FR-STOCK-001 — Available Stock

**Priority:** Must

Sistem harus menghitung stok tersedia dengan rumus:

```txt
available_stock = stock_qty - reserved_qty
```

**Acceptance Criteria:**

- Produk dapat dibeli jika `available_stock > 0`.
- Checkout tidak boleh melebihi available stock.
- Chatbot menggunakan available stock saat menjawab stok.

### FR-STOCK-002 — Stock Movement

**Priority:** Must

Semua perubahan stok harus dicatat di `StockMovements`.

**Movement Types:**

```txt
initial
restock
sale
reservation
release_reservation
adjustment
return
```

**Acceptance Criteria:**

- Setiap perubahan stok mencatat stock before dan stock after.
- Setiap perubahan reserved stock mencatat reserved before dan reserved after.
- Perubahan karena order/payment memiliki reference id.

### FR-STOCK-003 — Stock Reservation

**Priority:** Must

Sistem harus dapat mengunci stok sementara saat order menunggu pembayaran.

**Acceptance Criteria:**

- Saat order dibuat, `reserved_qty` bertambah.
- Saat payment sukses, `stock_qty` berkurang dan `reserved_qty` berkurang.
- Saat order expired/cancelled, `reserved_qty` berkurang.
- Tidak boleh terjadi overselling.

---

## 3.5 WhatsApp Integration with WAHA

### FR-WAHA-001 — Receive Message Webhook

**Priority:** Must

FastAPI harus menyediakan webhook untuk menerima pesan dari WAHA.

**Endpoint:**

```txt
POST /api/webhooks/waha/messages
```

**Acceptance Criteria:**

- Endpoint menerima payload dari WAHA.
- Sistem mengekstrak nomor customer, pesan, chat id, message id, dan session id.
- Pesan customer disimpan ke `ChatMessages`.
- Raw payload disimpan di metadata.

### FR-WAHA-002 — Send Message via WAHA

**Priority:** Must

Backend harus dapat mengirim balasan ke customer melalui WAHA.

**Endpoint Internal:**

```txt
POST /api/whatsapp/send-message
```

**Acceptance Criteria:**

- Pesan bot dikirim ke nomor WhatsApp customer.
- Pesan bot disimpan ke `ChatMessages`.
- Error pengiriman dicatat.

### FR-WAHA-003 — Idempotent Message Processing

**Priority:** Must

Sistem harus mencegah pesan WAHA diproses dua kali.

**Acceptance Criteria:**

- Message id digunakan untuk deduplication.
- Duplicate payload tidak memicu AI response ganda.
- Duplicate event dicatat.

---

## 3.6 Chat Management

### FR-CHAT-001 — Chat Session

**Priority:** Must

Sistem harus membuat atau melanjutkan chat session customer.

**Acceptance Criteria:**

- Customer baru memiliki `ChatSessions`.
- Channel untuk WhatsApp bernilai `whatsapp`.
- Session memiliki status `open`, `closed`, atau `abandoned`.
- `last_message_at` diperbarui setiap pesan masuk.

### FR-CHAT-002 — Chat Messages

**Priority:** Must

Sistem harus menyimpan pesan customer dan bot.

**Acceptance Criteria:**

- Pesan customer memiliki `sender_type = customer`.
- Pesan bot memiliki `sender_type = bot`.
- Intent dan related product dapat disimpan.
- Metadata dapat menyimpan payload WAHA.

### FR-CHAT-003 — Chat Dashboard

**Priority:** Must

Admin harus dapat melihat chat history.

**Acceptance Criteria:**

- Admin dapat melihat list chat session.
- Admin dapat membuka detail pesan.
- Admin dapat filter berdasarkan customer, channel, status, dan tanggal.

---

## 3.7 AI Chatbot

### FR-AI-001 — Intent Detection

**Priority:** Must

AI harus mendeteksi intent pesan customer.

**Supported Intents:**

```txt
greeting
ask_product
ask_price
ask_stock
ask_size
ask_color
ask_shipping
checkout
payment
track_order
complaint
unknown
```

**Acceptance Criteria:**

- Intent disimpan di `ChatMessages.intent`.
- Jika tidak yakin, intent menjadi `unknown`.
- AI memberikan fallback untuk pesan yang tidak jelas.

### FR-AI-002 — Product Q&A

**Priority:** Must

AI harus menjawab pertanyaan produk berdasarkan database.

**Acceptance Criteria:**

- AI mencari produk melalui backend tool.
- AI hanya menjawab berdasarkan produk aktif.
- AI tidak mengarang nama produk, harga, stok, ongkir, atau order.
- Jika produk tidak ditemukan, AI menawarkan alternatif.

### FR-AI-003 — Product Recommendation

**Priority:** Must

AI harus dapat merekomendasikan produk.

**Acceptance Criteria:**

- Rekomendasi mempertimbangkan warna, ukuran, gender, material, harga, dan stok.
- Produk inactive tidak direkomendasikan.
- Event `recommended` dicatat di `ProductInteractions`.

### FR-AI-004 — Tool Calling

**Priority:** Must

AI harus menggunakan backend tools untuk aksi penting.

**Required Tools:**

```txt
search_products()
get_product_detail()
check_product_stock()
create_cart()
add_item_to_cart()
create_order()
get_shipping_quotes()
select_shipping_quote()
create_midtrans_payment()
check_order_status()
track_shipment()
create_lead()
save_product_interaction()
```

**Acceptance Criteria:**

- AI tidak membuat order tanpa tool backend.
- AI tidak membuat payment tanpa Midtrans service.
- AI tidak menghitung ongkir tanpa Biteship service.
- AI meminta konfirmasi customer sebelum checkout.

---

## 3.8 Leads

### FR-LEAD-001 — Create Lead

**Priority:** Must

Sistem harus membuat atau memperbarui lead dari percakapan customer.

**Acceptance Criteria:**

- Customer yang bertanya produk dapat dibuat sebagai lead.
- Lead terhubung ke customer dan chat session.
- Status lead dapat berupa `new`, `interested`, `hot`, `converted`, atau `lost`.

### FR-LEAD-002 — Lead Scoring

**Priority:** Should

Sistem harus memberi score berdasarkan aktivitas customer.

| Activity | Score |
|---|---:|
| Tanya produk | +10 |
| Tanya stok | +15 |
| Tanya ongkir | +20 |
| Add to cart | +30 |
| Booking produk | +40 |
| Payment success | converted |

**Acceptance Criteria:**

- Score bertambah berdasarkan aktivitas.
- Lead dengan score tinggi dapat menjadi `hot`.
- Lead berubah menjadi `converted` jika order dibayar.

---

## 3.9 Product Interactions

### FR-INT-001 — Log Product Interaction

**Priority:** Must

Sistem harus mencatat interaksi customer terhadap produk.

**Event Types:**

```txt
asked
recommended
viewed
added_to_cart
booked
purchased
```

**Acceptance Criteria:**

- Event `asked` dicatat saat customer bertanya produk.
- Event `recommended` dicatat saat bot merekomendasikan produk.
- Event `added_to_cart` dicatat saat produk masuk cart.
- Event `purchased` dicatat setelah payment sukses.

---

## 3.10 Cart and Checkout

### FR-CART-001 — Create Cart

**Priority:** Must

Sistem harus membuat cart aktif untuk customer.

**Acceptance Criteria:**

- Customer dapat memiliki cart aktif.
- Cart terhubung ke customer dan chat session.
- Status cart dapat berupa `active`, `ordered`, `abandoned`, atau `expired`.

### FR-CART-002 — Add Item to Cart

**Priority:** Must

Sistem harus dapat menambahkan produk ke cart.

**Acceptance Criteria:**

- Produk harus active.
- Quantity tidak boleh melebihi available stock.
- Unit price memakai harga saat produk dimasukkan.
- Subtotal dihitung otomatis.

### FR-CART-003 — Checkout

**Priority:** Must

Sistem harus membuat order dari cart setelah customer konfirmasi checkout.

**Acceptance Criteria:**

- Order dibuat dengan status `waiting_payment`.
- Cart berubah menjadi `ordered`.
- Order items memiliki product snapshot.
- Stok dapat di-reserve.

---

## 3.11 Order Management

### FR-ORDER-001 — Create Order

**Priority:** Must

Sistem harus membuat order dari cart customer.

**Acceptance Criteria:**

- Order memiliki order_number unik.
- Order memiliki customer, address, subtotal, shipping cost, grand total, dan status.
- Order items tersimpan dengan snapshot produk.

### FR-ORDER-002 — Order Status

**Priority:** Must

Sistem harus mengelola status order.

**Order Statuses:**

```txt
draft
waiting_payment
paid
processing
shipped
completed
cancelled
expired
```

**Acceptance Criteria:**

- Order baru setelah checkout berstatus `waiting_payment`.
- Order berubah setelah payment webhook diterima.
- Customer hanya dapat melihat order miliknya.

### FR-ORDER-003 — Order Tracking

**Priority:** Must

Customer harus dapat mengecek status order melalui WhatsApp.

**Acceptance Criteria:**

- Bot menampilkan status order, payment, dan shipping.
- Jika tracking number tersedia, bot menampilkannya.
- Sistem tidak menampilkan data order customer lain.

---

## 3.12 Payment with Midtrans

### FR-PAY-001 — Create Payment

**Priority:** Must

Sistem harus membuat payment melalui Midtrans.

**Acceptance Criteria:**

- Payment amount sama dengan `Orders.grand_total`.
- Payment URL atau Snap token tersimpan.
- Customer menerima payment link melalui WhatsApp.
- Payment tersimpan di `Payments`.

### FR-PAY-002 — Midtrans Webhook

**Priority:** Must

Sistem harus menerima webhook pembayaran dari Midtrans.

**Endpoint:**

```txt
POST /api/webhooks/midtrans
```

**Acceptance Criteria:**

- Payload webhook disimpan di `PaymentWebhookLogs`.
- Payment status diperbarui.
- Order status diperbarui.
- Webhook diproses secara idempotent.
- Duplicate webhook tidak mengubah stok dua kali.

---

## 3.13 Shipping with Biteship

### FR-SHIP-001 — Get Shipping Quotes

**Priority:** Must

Sistem harus mengambil pilihan ongkir dari Biteship.

**Acceptance Criteria:**

- Backend mengirim alamat dan berat order ke Biteship.
- Pilihan ongkir disimpan di `ShippingQuotes`.
- Bot menampilkan beberapa opsi kurir ke customer.

### FR-SHIP-002 — Select Shipping Quote

**Priority:** Must

Customer harus dapat memilih salah satu ongkir.

**Acceptance Criteria:**

- Quote pilihan ditandai `is_selected = true`.
- Shipping cost order diperbarui.
- Grand total order diperbarui.

### FR-SHIP-003 — Shipment Tracking

**Priority:** Should

Sistem harus dapat menyimpan shipment dan tracking.

**Acceptance Criteria:**

- Shipment tersimpan di `Shipments`.
- Tracking logs tersimpan di `ShipmentTrackingLogs`.
- Customer dapat bertanya status pengiriman.

---

## 3.14 Admin Dashboard

### FR-ADM-001 — Dashboard Overview

**Priority:** Must

Admin dashboard harus menampilkan ringkasan bisnis.

**Metrics:**

- Total revenue
- Total paid orders
- Total customers
- Total leads
- Active products
- Low stock products
- Recent chats
- Recent orders
- Top asked products
- Top purchased products

### FR-ADM-002 — Product Page

**Priority:** Must

Admin harus dapat CRUD produk dan update stok.

### FR-ADM-003 — Chat Page

**Priority:** Must

Admin harus dapat melihat percakapan WhatsApp customer.

### FR-ADM-004 — Leads Page

**Priority:** Must

Admin harus dapat melihat dan mengelola leads.

### FR-ADM-005 — Orders Page

**Priority:** Must

Admin harus dapat melihat dan mengelola order.

### FR-ADM-006 — Payments Page

**Priority:** Must

Admin harus dapat melihat payment dan webhook logs.

### FR-ADM-007 — Shipping Page

**Priority:** Should

Admin harus dapat melihat shipping quotes, shipment, dan tracking logs.

---

## 4. API Requirements

### 4.1 Auth API

```txt
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

### 4.2 Product API

```txt
GET    /api/products
POST   /api/products
GET    /api/products/{id}
PATCH  /api/products/{id}
DELETE /api/products/{id}
PATCH  /api/products/{id}/stock
```

### 4.3 WhatsApp / WAHA API

```txt
POST /api/webhooks/waha/messages
POST /api/whatsapp/send-message
GET  /api/whatsapp/sessions
POST /api/whatsapp/sessions/start
POST /api/whatsapp/sessions/stop
```

### 4.4 Chat API

```txt
GET /api/chat-sessions
GET /api/chat-sessions/{id}
GET /api/chat-sessions/{id}/messages
```

### 4.5 Cart API

```txt
GET    /api/carts/active
POST   /api/carts/items
PATCH  /api/carts/items/{id}
DELETE /api/carts/items/{id}
```

### 4.6 Order API

```txt
GET   /api/orders
POST  /api/orders
GET   /api/orders/{id}
PATCH /api/orders/{id}/status
```

### 4.7 Payment API

```txt
POST /api/payments/midtrans/create
POST /api/webhooks/midtrans
GET  /api/payments
GET  /api/payments/{id}
```

### 4.8 Shipping API

```txt
POST /api/shipping/quotes
POST /api/shipping/quotes/{id}/select
POST /api/shipping/shipments
GET  /api/shipping/shipments/{id}/tracking
```

### 4.9 Leads and Analytics API

```txt
GET   /api/leads
GET   /api/leads/{id}
PATCH /api/leads/{id}
GET   /api/analytics/products
GET   /api/analytics/sales
GET   /api/analytics/chats
```

---

## 5. Data Requirements

### 5.1 Main Tables

```txt
Users
Customers
CustomerAddresses
Products
StockMovements
ChatSessions
ChatMessages
Leads
ProductInteractions
Carts
CartItems
Orders
OrderItems
Payments
PaymentWebhookLogs
ShippingQuotes
Shipments
ShipmentTrackingLogs
ProductKnowledgeDocuments
```

### 5.2 Data Integrity

- `Users.email` harus unik.
- `Products.slug` harus unik.
- `Orders.order_number` harus unik.
- `Payments.provider_order_id` harus unik.
- Order item harus menyimpan snapshot produk.
- Payment webhook harus disimpan untuk audit.
- Stock movement wajib dibuat untuk perubahan stok.
- Chat message tidak boleh hilang setelah diproses AI.

---

## 6. Business Rules

### BR-001 — Product Availability

Produk tersedia jika:

```txt
status = active
AND stock_qty - reserved_qty > 0
```

### BR-002 — Price Snapshot

Harga order menggunakan harga saat checkout, bukan harga terbaru setelah produk diedit.

### BR-003 — Stock Reservation

Reserved stock digunakan saat order menunggu payment untuk menghindari overselling.

### BR-004 — Payment Success

Jika payment sukses:

- Payment status menjadi `paid`.
- Order status menjadi `paid` atau `processing`.
- Stock berkurang.
- Reserved stock berkurang.
- Lead dapat menjadi `converted`.
- Product interaction `purchased` dicatat.

### BR-005 — Payment Expired

Jika payment expired:

- Payment status menjadi `expired`.
- Order status menjadi `expired`.
- Reserved stock dilepas.

### BR-006 — Customer Data Isolation

Customer hanya boleh menerima informasi order miliknya sendiri.

### BR-007 — AI Confirmation

AI harus meminta konfirmasi sebelum membuat cart, order, payment, atau mengubah alamat.

---

## 7. State Requirements

### 7.1 Cart Status

```txt
active
ordered
abandoned
expired
```

### 7.2 Order Status

```txt
draft
waiting_payment
paid
processing
shipped
completed
cancelled
expired
```

### 7.3 Payment Status

```txt
unpaid
pending
paid
failed
expired
cancelled
refunded
```

### 7.4 Shipping Status

```txt
not_created
waiting_pickup
picked_up
in_transit
delivered
failed
cancelled
```

### 7.5 Lead Status

```txt
new
interested
hot
converted
lost
```

---

## 8. Non-Functional Requirements

### NFR-001 — Performance

**Priority:** Must

- Webhook WAHA harus cepat menerima payload.
- List API harus menggunakan pagination.
- Dashboard tidak boleh mengambil seluruh data tanpa limit.
- Proses AI yang lama sebaiknya tidak membuat webhook timeout.

### NFR-002 — Reliability

**Priority:** Must

- Webhook WAHA dan Midtrans harus idempotent.
- Error external API harus dicatat.
- Sistem harus memiliki fallback message.
- Stock update harus aman dari race condition.

### NFR-003 — Security

**Priority:** Must

- Password harus di-hash.
- API admin harus menggunakan authentication.
- Role-based access control harus tersedia.
- Webhook Midtrans harus divalidasi.
- Webhook WAHA sebaiknya dilindungi token/secret.
- Environment variables tidak boleh disimpan di repository.

### NFR-004 — Privacy

**Priority:** Must

- Nomor WhatsApp dan alamat customer diperlakukan sebagai data pribadi.
- Data customer tidak boleh terlihat oleh customer lain.
- Logs tidak boleh membocorkan data sensitif.

### NFR-005 — Maintainability

**Priority:** Must

- Backend harus modular.
- Business logic dipisahkan dari router.
- Migration menggunakan Alembic.
- Frontend component harus reusable.
- Query frontend menggunakan TanStack Query.

### NFR-006 — Scalability

**Priority:** Should

- Sistem siap ditambahkan background worker.
- PostgreSQL indexing digunakan untuk query utama.
- Product knowledge siap dikembangkan ke pgvector.
- Analytics dapat dioptimasi dengan materialized/reporting table di masa depan.

### NFR-007 — Observability

**Priority:** Should

- Webhook logs disimpan.
- Error integration dicatat.
- Raw payload penting disimpan di metadata.
- Admin dapat melihat payment webhook logs.

---

## 9. Error Handling Requirements

### ERR-001 — Product Not Found

Bot harus memberi fallback jika produk tidak ditemukan.

```txt
Maaf, produk yang kamu cari belum tersedia. Mau saya rekomendasikan produk lain yang mirip?
```

### ERR-002 — Stock Not Available

Bot harus memberi tahu customer jika stok tidak cukup.

```txt
Maaf, stok produk tersebut tidak cukup. Mau ambil jumlah yang tersedia atau pilih produk lain?
```

### ERR-003 — WAHA Error

Jika pesan gagal dikirim melalui WAHA, sistem mencatat error dan dapat melakukan retry.

### ERR-004 — Midtrans Error

Jika payment gagal dibuat, order tidak boleh dianggap paid dan customer diberi pesan fallback.

### ERR-005 — Biteship Error

Jika ongkir gagal diambil, customer diminta mencoba lagi atau admin dapat follow up.

### ERR-006 — AI Error

Jika AI gagal, pesan customer tetap tersimpan dan bot mengirim fallback response.

---

## 10. Testing Requirements

### 10.1 Unit Testing

Unit test harus mencakup:

- Product service
- Stock calculation
- Cart service
- Order service
- Payment status mapping
- Webhook idempotency
- Lead scoring
- Product interaction logging

### 10.2 Integration Testing

Integration test harus mencakup:

- WAHA webhook receive message
- Send message via WAHA mock
- Create payment via Midtrans mock
- Receive Midtrans webhook mock
- Get shipping quote via Biteship mock
- Create order from cart
- Stock reservation and release

### 10.3 End-to-End Testing

E2E scenario utama:

```txt
Customer chat WhatsApp
→ chatbot search product
→ customer add to cart
→ checkout
→ input address
→ get shipping quote
→ create payment
→ payment webhook success
→ order paid
→ stock updated
→ admin sees order
```

---

## 11. Deployment Requirements

### 11.1 Environment Variables

```txt
APP_ENV
DATABASE_URL
JWT_SECRET
WAHA_BASE_URL
WAHA_API_KEY
MIDTRANS_SERVER_KEY
MIDTRANS_CLIENT_KEY
MIDTRANS_IS_PRODUCTION
BITESHIP_API_KEY
AI_PROVIDER_API_KEY
```

### 11.2 Recommended Services

- FastAPI application server
- PostgreSQL database
- React frontend hosting
- WAHA service
- Reverse proxy
- SSL certificate
- Object storage for product images if needed
- Background worker if needed

---

## 12. Suggested Backend Structure

```txt
app/
  main.py
  core/
    config.py
    security.py
    database.py
  db/
    base.py
    session.py
    migrations/
  modules/
    auth/
    users/
    customers/
    products/
    stock/
    chat/
    whatsapp/
    ai/
    leads/
    carts/
    orders/
    payments/
    shipping/
    analytics/
    product_knowledge/
  integrations/
    waha/
    midtrans/
    biteship/
  shared/
    exceptions.py
    pagination.py
    responses.py
    dependencies.py
```

---

## 13. Suggested Frontend Structure

```txt
src/
  app/
    router.tsx
    query-client.ts
  components/
    ui/
    layout/
    dashboard/
    products/
    customers/
    chats/
    leads/
    orders/
    payments/
    shipping/
  pages/
    auth/
    admin/
      dashboard/
      products/
      customers/
      chats/
      leads/
      orders/
      payments/
      shipping/
      product-knowledge/
  services/
    api.ts
    auth.service.ts
    product.service.ts
    customer.service.ts
    chat.service.ts
    lead.service.ts
    order.service.ts
    payment.service.ts
    shipping.service.ts
  queries/
  types/
  hooks/
  utils/
```

---

## 14. MVP Acceptance Criteria

MVP selesai jika:

1. Admin dapat login.
2. Admin dapat CRUD produk.
3. Admin dapat update stok.
4. WAHA dapat mengirim pesan WhatsApp ke FastAPI webhook.
5. Backend menyimpan customer, chat session, dan chat message.
6. AI chatbot menjawab pertanyaan produk berdasarkan database.
7. AI chatbot dapat menambahkan produk ke cart.
8. Sistem dapat membuat order dari cart.
9. Sistem dapat mengambil shipping quote dari Biteship.
10. Customer dapat memilih shipping quote.
11. Sistem dapat membuat payment Midtrans.
12. Customer menerima payment URL via WhatsApp.
13. Midtrans webhook mengubah payment dan order status.
14. Stok berkurang setelah payment sukses.
15. Product interactions tercatat.
16. Leads tercatat.
17. Admin dapat melihat customer, chat, leads, order, payment, dan shipping di dashboard.
18. Customer dapat mengecek status order melalui WhatsApp.

---

## 15. Out of Scope for MVP

- Product variants terpisah.
- Multiple product images.
- Category management terpisah.
- Voucher dan promo kompleks.
- Refund otomatis.
- Return management.
- Loyalty point.
- Marketplace integration.
- Instagram DM integration.
- Multi-tenant/multi-store.
- Native mobile app.
- Broadcast campaign WhatsApp.
- Human handoff kompleks.
- AI model training sendiri.
- Dedicated vector database.

---

## 16. Future Enhancements

- Product variants.
- Product images table.
- Product categories.
- WhatsApp broadcast campaign.
- Human handoff to admin.
- Admin live reply from dashboard.
- Customer segmentation.
- Coupon and promotion.
- Refund and return flow.
- Advanced product analytics.
- pgvector for semantic search.
- RAG for product FAQ.
- Multi-store support.
- Marketplace sync.
- Instagram DM chatbot.

---

## 17. Traceability Matrix

| Business Goal | Related Requirements |
|---|---|
| Mengurangi beban admin | FR-AI-002, FR-AI-003, FR-WAHA-001, FR-WAHA-002 |
| Meningkatkan conversion chat ke order | FR-CART-001, FR-CART-002, FR-CART-003, FR-PAY-001 |
| Mengelola produk dan stok | FR-PROD-001, FR-PROD-002, FR-PROD-003, FR-STOCK-001, FR-STOCK-002 |
| Menyediakan data leads | FR-LEAD-001, FR-LEAD-002 |
| Mengetahui produk populer | FR-INT-001, FR-ADM-001 |
| Otomatisasi pembayaran | FR-PAY-001, FR-PAY-002 |
| Otomatisasi pengiriman | FR-SHIP-001, FR-SHIP-002, FR-SHIP-003 |
| Monitoring operasional | FR-ADM-001 sampai FR-ADM-007 |

---

## 18. Conclusion

SRS ini mendefinisikan kebutuhan software untuk membangun **AI WhatsApp Chatbot E-Commerce Fashion** sebagai MVP conversational commerce.

Sistem harus mampu menjalankan proses end-to-end:

```txt
Customer WhatsApp
→ WAHA
→ FastAPI Webhook
→ AI Chatbot
→ Product Search
→ Cart
→ Checkout
→ Biteship Shipping Quote
→ Midtrans Payment
→ Payment Webhook
→ Stock Update
→ Admin Dashboard Monitoring
```

Dokumen ini dapat digunakan sebagai dasar pengembangan backend, frontend, chatbot AI, integrasi WAHA, integrasi Midtrans, integrasi Biteship, database, testing, dan deployment.
