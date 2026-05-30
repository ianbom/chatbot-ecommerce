# Product Requirements Document (PRD)

# AI WhatsApp Chatbot E-Commerce Fashion

**Version:** 1.0  
**Status:** MVP Planning  
**Project Type:** AI Conversational Commerce / WhatsApp Commerce  
**Primary Channel:** WhatsApp via WAHA  
**Backend:** FastAPI  
**Frontend:** React TypeScript  
**Database:** PostgreSQL  
**Payment Integration:** Midtrans  
**Shipping Integration:** Biteship  

---

## 1. Executive Summary

Project ini adalah platform **AI WhatsApp Chatbot E-Commerce Fashion** yang memungkinkan customer melakukan proses belanja pakaian langsung melalui WhatsApp. Customer dapat bertanya tentang produk, mendapatkan rekomendasi, melakukan booking produk, checkout, memilih pengiriman, melakukan pembayaran, dan mengecek status pesanan tanpa keluar dari percakapan WhatsApp.

Sistem menggunakan **WAHA** sebagai WhatsApp API gateway. WAHA menerima pesan dari WhatsApp dan meneruskannya ke **webhook FastAPI**. Backend FastAPI memproses pesan tersebut, menyimpan chat, menjalankan AI chatbot, mencari data produk, membuat cart/order, mengambil ongkir dari Biteship, membuat pembayaran Midtrans, dan mengirim balasan kembali ke customer melalui WAHA.

Selain chatbot, sistem juga memiliki **admin dashboard** untuk mengelola produk, stok, customer, leads, chat history, order, payment, shipping, dan analisis performa produk.

Untuk MVP, produk dibuat sederhana dengan hanya menggunakan satu tabel `Products`. Tidak ada product variants, product images, dan product categories terpisah. Satu baris produk mewakili satu item produk spesifik, misalnya “Oversized T-Shirt Black Size L”.

---

## 2. Product Vision

Membangun platform e-commerce berbasis percakapan yang menjadikan WhatsApp chatbot sebagai sales assistant utama. Chatbot tidak hanya menjawab pertanyaan customer, tetapi juga membantu customer menyelesaikan proses pembelian dari awal sampai akhir.

Visi produk ini adalah menghadirkan pengalaman belanja seperti berbicara dengan admin toko online, tetapi lebih cepat, otomatis, dan bisa dianalisis oleh pemilik bisnis.

---

## 3. Problem Statement

Banyak toko fashion online masih bergantung pada admin manusia untuk menjawab pertanyaan berulang seperti harga produk, stok ukuran, warna tersedia, ongkir, cara bayar, dan status pesanan.

Masalah utama yang ingin diselesaikan:

- Customer sering bertanya melalui WhatsApp, tetapi prosesnya masih manual.
- Admin harus menjawab pertanyaan yang sama berkali-kali.
- Percakapan customer tidak selalu tercatat dengan rapi.
- Data leads dan minat customer sulit dianalisis.
- Produk yang sering ditanyakan dan produk yang sering dibeli sulit diketahui otomatis.
- Proses checkout, pembayaran, dan pengiriman masih terpisah dari percakapan.

---

## 4. Solution Overview

Solusi yang dibuat adalah sistem chatbot e-commerce fashion berbasis WhatsApp.

```txt
Customer WhatsApp
↓
WAHA
↓
FastAPI Webhook
↓
Chatbot AI + Business Logic
↓
PostgreSQL
↓
Midtrans / Biteship jika diperlukan
↓
FastAPI
↓
WAHA
↓
Customer WhatsApp
```

Customer cukup chat ke WhatsApp toko. Semua proses belanja dipandu oleh chatbot.

Contoh percakapan:

```txt
Customer:
Ada hoodie hitam ukuran L?

Bot:
Ada. Hoodie Oversized Black ukuran L tersedia dengan harga Rp249.000, stok tersedia 8 pcs.
Mau saya bantu booking?

Customer:
Ya, saya mau beli 1.

Bot:
Baik, saya simpan ke cart. Silakan kirim alamat lengkap untuk cek ongkir.
```

---

## 5. Goals

### 5.1 Business Goals

- Mengurangi beban admin dalam menjawab pertanyaan berulang.
- Meningkatkan conversion rate dari chat WhatsApp menjadi order.
- Mengumpulkan data leads dari customer yang tertarik tetapi belum membeli.
- Menyediakan insight produk yang paling sering ditanyakan, dibooking, dan dibeli.
- Membuat proses penjualan lebih otomatis dari chat hingga pembayaran.

### 5.2 Product Goals

- Customer dapat bertanya produk melalui WhatsApp.
- Customer dapat mendapatkan rekomendasi produk dari chatbot.
- Customer dapat booking produk melalui WhatsApp.
- Customer dapat checkout melalui WhatsApp.
- Customer dapat memilih pengiriman dari Biteship.
- Customer dapat membayar melalui Midtrans.
- Admin dapat mengelola produk dan stok.
- Admin dapat melihat chat history, leads, customer, order, payment, dan shipping.

### 5.3 Technical Goals

- Backend modular menggunakan FastAPI.
- Database menggunakan PostgreSQL.
- Frontend admin dashboard menggunakan React TypeScript.
- WhatsApp integration menggunakan WAHA.
- Payment menggunakan Midtrans.
- Shipping menggunakan Biteship.
- AI chatbot menggunakan tool calling agar dapat menjalankan aksi nyata di backend.
- Struktur database sederhana untuk MVP tetapi siap dikembangkan.

---

## 6. Non-Goals untuk MVP

Fitur berikut tidak termasuk MVP awal:

- Marketplace integration.
- Multi-store atau multi-tenant.
- Loyalty point.
- Voucher dan promo kompleks.
- Return/refund otomatis.
- Product variants terpisah.
- Multiple product images.
- Category management terpisah.
- Mobile app native.
- AI training model sendiri.
- Human handoff complex routing.
- Campaign broadcast otomatis.

---

## 7. Target Users

### 7.1 Customer

Customer adalah pembeli yang berinteraksi dengan chatbot melalui WhatsApp.

Customer dapat:

- Bertanya tentang produk.
- Menanyakan harga, stok, ukuran, warna, bahan, dan detail produk.
- Meminta rekomendasi produk.
- Booking produk.
- Checkout.
- Mengirim alamat.
- Memilih pengiriman.
- Membayar order.
- Mengecek status order.

### 7.2 Admin

Admin adalah pengelola toko yang menggunakan web dashboard.

Admin dapat:

- Login ke dashboard.
- Mengelola produk.
- Mengelola stok.
- Melihat customer.
- Melihat chat history.
- Melihat leads.
- Melihat order.
- Melihat pembayaran.
- Melihat pengiriman.
- Melihat analytics produk.

### 7.3 Staff

Staff adalah user internal dengan akses terbatas.

Staff dapat:

- Melihat order.
- Melihat customer.
- Melihat chat.
- Update status operasional tertentu sesuai permission.

---

## 8. Technology Stack

### 8.1 Frontend

Frontend digunakan untuk admin dashboard dan optional customer web interface.

| Technology | Fungsi |
|---|---|
| React TypeScript | Framework frontend utama |
| Vite | Build tool dan development server |
| Tailwind CSS | Styling utility-first |
| shadcn/ui | Komponen UI dashboard |
| TanStack Query | Data fetching, caching, dan mutation state |

Frontend harus dibuat modular, reusable, dan type-safe. TanStack Query digunakan untuk mengambil data dari API backend, mengelola loading state, error state, caching, dan mutation seperti create product, update stock, update order, dan sebagainya.

### 8.2 Backend

Backend menjadi pusat business logic, API, webhook, AI orchestration, payment, dan shipping.

| Technology | Fungsi |
|---|---|
| FastAPI | Framework backend utama |
| Pydantic | Request/response validation |
| SQLAlchemy / SQLModel | ORM dan database model |
| Alembic | Database migration |
| PostgreSQL | Database utama |

Backend harus dipisah berdasarkan domain module agar mudah dikembangkan.

Module utama:

```txt
auth
users
customers
products
stock
chat
whatsapp
ai
leads
carts
orders
payments
shipping
analytics
product_knowledge
```

### 8.3 WhatsApp Integration

WhatsApp integration menggunakan **WAHA**.

WAHA berfungsi sebagai gateway antara WhatsApp dan backend.

Tugas WAHA:

- Menerima pesan dari WhatsApp customer.
- Mengirim pesan ke webhook FastAPI.
- Mengirim balasan dari backend ke WhatsApp customer.
- Menyediakan session WhatsApp untuk nomor toko.

Tugas FastAPI:

- Menyediakan webhook endpoint untuk menerima payload dari WAHA.
- Menyimpan pesan ke database.
- Menjalankan AI chatbot dan business logic.
- Mengirim response ke customer melalui WAHA API.

### 8.4 Payment Integration

Payment menggunakan **Midtrans**.

Fungsi Midtrans:

- Membuat payment transaction.
- Menghasilkan payment URL atau Snap token.
- Mengirim webhook status pembayaran.
- Mengubah status order setelah pembayaran berhasil, gagal, expired, atau cancelled.

### 8.5 Shipping Integration

Shipping menggunakan **Biteship**.

Fungsi Biteship:

- Mengambil shipping quotes berdasarkan alamat customer.
- Menyediakan pilihan kurir dan layanan.
- Membuat shipment.
- Menyimpan tracking number dan status pengiriman.

### 8.6 AI Technology

AI chatbot menggunakan pendekatan:

```txt
LLM + Tool Calling + Database Retrieval
```

AI tidak boleh menjawab hanya berdasarkan prompt bebas. AI harus menggunakan data dari database dan memanggil backend tools untuk aksi penting.

Contoh tools:

```txt
search_products()
get_product_detail()
check_product_stock()
create_customer()
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

### 8.7 Vector Database Decision

Untuk MVP, vector database terpisah belum wajib.

Rekomendasi:

- Gunakan PostgreSQL biasa untuk MVP.
- Gunakan SQL search dan filter untuk produk.
- Siapkan `ProductKnowledgeDocuments` untuk knowledge produk.
- Tambahkan `pgvector` di PostgreSQL jika chatbot mulai butuh semantic search/RAG.
- Tidak perlu langsung memakai Qdrant, Pinecone, atau Milvus.

---

## 9. MVP Scope

MVP harus mampu menyelesaikan alur utama:

```txt
Customer chat WhatsApp
→ WAHA menerima pesan
→ FastAPI webhook menerima payload
→ Chatbot memahami intent
→ Chatbot mencari produk
→ Customer memilih produk
→ Sistem membuat cart
→ Customer checkout
→ Sistem mengambil ongkir Biteship
→ Customer memilih pengiriman
→ Sistem membuat order
→ Sistem membuat pembayaran Midtrans
→ Customer membayar
→ Midtrans webhook update status pembayaran
→ Sistem update order dan stok
→ Admin melihat data di dashboard
```

---

## 10. Customer WhatsApp Chatbot Requirements

### 10.1 Receive Message from WhatsApp

**Description**  
Sistem harus dapat menerima pesan customer dari WhatsApp melalui WAHA.

**Functional Requirements**

- WAHA mengirim payload pesan ke endpoint webhook FastAPI.
- FastAPI memvalidasi payload.
- Sistem mengambil nomor WhatsApp customer.
- Sistem mencari atau membuat data customer berdasarkan nomor WhatsApp.
- Sistem membuat atau melanjutkan chat session.
- Sistem menyimpan pesan customer ke `ChatMessages`.

**Acceptance Criteria**

- Pesan WhatsApp masuk tersimpan di database.
- Customer otomatis dibuat jika belum ada.
- Chat session dibuat dengan channel `whatsapp`.
- Payload WAHA disimpan di metadata untuk audit/debugging.

### 10.2 Send Message to WhatsApp

**Description**  
Sistem harus dapat mengirim balasan chatbot ke customer melalui WAHA.

**Functional Requirements**

- Backend mengirim text response ke WAHA API.
- WAHA meneruskan pesan ke WhatsApp customer.
- Pesan bot disimpan ke `ChatMessages`.
- Sistem dapat mengirim pesan error fallback jika AI atau integration gagal.

**Acceptance Criteria**

- Customer menerima balasan di WhatsApp.
- Balasan bot tercatat di database.
- Error WAHA dicatat di log backend.

### 10.3 Product Q&A

**Description**  
Customer dapat bertanya tentang produk.

Contoh pertanyaan:

```txt
Ada hoodie hitam?
Harga kaos oversized berapa?
Ukuran L ready?
Ada baju yang cocok untuk acara casual?
```

**Functional Requirements**

- AI mendeteksi intent pertanyaan produk.
- Sistem mencari produk dari tabel `Products`.
- Sistem hanya menampilkan produk dengan status active.
- Sistem mempertimbangkan stok tersedia, yaitu `stock_qty - reserved_qty`.
- Sistem mencatat event ke `ProductInteractions` dengan event `asked`.

**Acceptance Criteria**

- Chatbot menjawab berdasarkan data produk.
- Chatbot tidak mengarang produk yang tidak ada.
- Produk yang ditanyakan tercatat untuk analytics.

### 10.4 Product Recommendation

**Description**  
Chatbot dapat memberikan rekomendasi produk berdasarkan kebutuhan customer.

**Functional Requirements**

- Chatbot memahami preferensi customer dari percakapan.
- Chatbot dapat merekomendasikan produk berdasarkan warna, ukuran, gender, material, harga, dan stok.
- Sistem mencatat event `recommended` ke `ProductInteractions`.

**Acceptance Criteria**

- Rekomendasi hanya menampilkan produk aktif.
- Produk kosong stok tidak direkomendasikan sebagai ready stock.
- Rekomendasi dapat diarahkan ke checkout.

### 10.5 Cart and Booking

**Description**  
Customer dapat memasukkan produk ke cart melalui chat.

**Functional Requirements**

- Customer dapat memilih produk dari hasil rekomendasi.
- Sistem membuat cart jika belum ada cart aktif.
- Sistem menambahkan item ke `CartItems`.
- Sistem menghitung subtotal.
- Sistem dapat menampilkan ringkasan cart.
- Sistem mencatat event `added_to_cart` atau `booked`.

**Acceptance Criteria**

- Cart aktif dibuat untuk customer.
- Item cart tersimpan dengan quantity dan harga saat itu.
- Customer dapat melanjutkan ke checkout.

### 10.6 Checkout

**Description**  
Customer dapat checkout melalui WhatsApp.

**Functional Requirements**

- Chatbot meminta data pengiriman.
- Sistem menyimpan alamat customer ke `CustomerAddresses`.
- Sistem membuat order dari cart.
- Sistem membuat order items dengan snapshot produk.
- Sistem menghitung subtotal, shipping cost, dan grand total.

**Acceptance Criteria**

- Order berhasil dibuat dengan status `waiting_payment`.
- Cart berubah menjadi `ordered`.
- Order memiliki customer, alamat, item, subtotal, shipping cost, dan grand total.

### 10.7 Shipping Quote with Biteship

**Description**  
Sistem mengambil pilihan pengiriman dari Biteship.

**Functional Requirements**

- Backend mengirim data alamat dan berat produk ke Biteship.
- Sistem menyimpan pilihan ongkir ke `ShippingQuotes`.
- Chatbot menampilkan beberapa opsi pengiriman.
- Customer memilih salah satu pengiriman.
- Sistem menandai quote terpilih dengan `is_selected = true`.

**Acceptance Criteria**

- Customer menerima pilihan kurir dan harga.
- Quote yang dipilih tersimpan.
- Shipping cost masuk ke order total.

### 10.8 Payment with Midtrans

**Description**  
Sistem membuat pembayaran melalui Midtrans.

**Functional Requirements**

- Backend membuat payment transaction ke Midtrans.
- Sistem menyimpan data payment ke `Payments`.
- Chatbot mengirim payment URL ke customer.
- Midtrans mengirim webhook ke FastAPI.
- Backend memvalidasi webhook.
- Backend update payment status dan order status.

**Acceptance Criteria**

- Customer menerima link pembayaran.
- Payment record tersimpan.
- Setelah webhook sukses, order berubah menjadi paid/processing.
- Stok produk diperbarui sesuai business rule.

### 10.9 Order Tracking

**Description**  
Customer dapat mengecek status order melalui WhatsApp.

**Functional Requirements**

- Customer dapat bertanya status order.
- Sistem mencari order berdasarkan nomor WhatsApp atau order number.
- Chatbot menampilkan status pembayaran, status order, dan status pengiriman.
- Jika shipment sudah dibuat, chatbot menampilkan tracking number.

**Acceptance Criteria**

- Customer mendapatkan status order terbaru.
- Chatbot tidak menampilkan order milik customer lain.

---

## 11. Admin Dashboard Requirements

### 11.1 Authentication

Admin dapat login ke dashboard menggunakan email dan password.

**Functional Requirements**

- Login.
- Logout.
- JWT/session authentication.
- Role-based access.
- Password hashing.

**Acceptance Criteria**

- User tidak bisa mengakses dashboard tanpa login.
- Token/session valid dibutuhkan untuk API admin.

### 11.2 Dashboard Overview

Dashboard menampilkan ringkasan bisnis.

Metrics utama:

- Total sales.
- Total paid orders.
- Total customers.
- Total leads.
- Total active products.
- Low stock products.
- Recent chats.
- Recent orders.
- Top asked products.
- Top purchased products.

### 11.3 Product Management

Admin dapat mengelola produk.

Product fields:

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

Functional requirements:

- Create product.
- Read product list.
- Update product.
- Soft delete product.
- Search/filter product.
- Update status active/inactive.

### 11.4 Stock Management

Admin dapat melihat dan memperbarui stok.

Functional requirements:

- Update stock.
- View stock history.
- View low stock products.
- Record stock movement.
- Track reserved stock.

Stock movement types:

```txt
initial
restock
sale
reservation
release_reservation
adjustment
return
```

### 11.5 Chat History

Admin dapat melihat percakapan customer.

Functional requirements:

- List chat sessions.
- Filter by customer, status, channel, date.
- View chat messages.
- View related product.
- View AI intent.
- View WAHA metadata.

### 11.6 Leads Management

Admin dapat melihat calon customer potensial.

Lead statuses:

```txt
new
interested
hot
converted
lost
```

Functional requirements:

- List leads.
- View interest summary.
- View interested products.
- Assign lead to staff.
- Mark lead as converted/lost.
- Link lead to converted order.

### 11.7 Customer Management

Admin dapat melihat data customer.

Functional requirements:

- List customers.
- View customer detail.
- View phone, email, source.
- View order history.
- View chat history.
- View addresses.
- View total orders and total spent.

### 11.8 Order Management

Admin dapat mengelola order.

Order statuses:

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

Functional requirements:

- List orders.
- View order detail.
- Filter by status.
- View order items.
- View payment status.
- View shipping status.
- Update operational status.

### 11.9 Payment Management

Admin dapat melihat transaksi pembayaran.

Functional requirements:

- List payments.
- View payment detail.
- View provider order ID.
- View transaction ID.
- View payment URL/Snap token.
- View webhook logs.
- Filter by payment status.

### 11.10 Shipping Management

Admin dapat melihat pengiriman.

Functional requirements:

- List shipping quotes.
- View selected quote.
- View shipment.
- View courier, service, tracking ID, waybill ID.
- View shipment tracking logs.
- Update shipment status if needed.

### 11.11 Product Analytics

Admin dapat melihat analytics produk.

Metrics:

- Produk paling sering ditanyakan.
- Produk paling sering direkomendasikan.
- Produk paling sering masuk cart.
- Produk paling sering dibooking.
- Produk paling sering dibeli.
- Produk dengan stok rendah.
- Produk sering ditanya tetapi jarang dibeli.

Data source utama:

- `ProductInteractions`
- `OrderItems`
- `Orders`
- `ChatMessages`

---

## 12. AI Chatbot Requirements

### 12.1 AI Responsibilities

AI chatbot bertindak sebagai sales assistant.

AI harus mampu:

- Memahami pesan customer.
- Mendeteksi intent.
- Mengambil data produk dari database.
- Menjawab pertanyaan produk.
- Memberikan rekomendasi.
- Membantu customer checkout.
- Mengarahkan customer ke pembayaran.
- Menjawab status order.
- Membuat lead summary.
- Menyimpan interaction event.

### 12.2 Supported Intents

Intent awal:

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

### 12.3 AI Guardrails

AI harus mengikuti aturan berikut:

- Tidak boleh mengarang produk.
- Tidak boleh mengarang harga.
- Tidak boleh mengarang stok.
- Tidak boleh membuat order tanpa konfirmasi customer.
- Tidak boleh menampilkan data order milik customer lain.
- Harus meminta konfirmasi sebelum checkout.
- Harus memberi fallback jika data tidak ditemukan.
- Harus menggunakan tools backend untuk aksi penting.

---

## 13. Business Rules

### 13.1 Product Rules

- Produk hanya bisa dijual jika status `active`.
- Produk dianggap tersedia jika `stock_qty - reserved_qty > 0`.
- Produk dengan stok habis tidak boleh ditawarkan sebagai ready stock.
- Harga order menggunakan snapshot harga saat checkout.

### 13.2 Cart Rules

- Satu customer dapat memiliki satu cart aktif.
- Cart dapat expired jika tidak dilanjutkan.
- Cart berubah menjadi ordered setelah order dibuat.
- Cart item menyimpan harga saat item ditambahkan.

### 13.3 Order Rules

- Order dibuat setelah customer konfirmasi checkout.
- Order awal memiliki status `waiting_payment`.
- Order memiliki expiry time.
- Order cancelled/expired jika tidak dibayar sampai waktu tertentu.
- Order paid jika webhook Midtrans valid dan payment berhasil.

### 13.4 Stock Reservation Rules

- Saat order dibuat, sistem dapat menambah `reserved_qty`.
- Saat pembayaran sukses, `stock_qty` dikurangi dan `reserved_qty` dikurangi.
- Saat order expired/cancelled, `reserved_qty` dikurangi.
- Semua perubahan stok harus dicatat di `StockMovements`.

### 13.5 Payment Rules

- Payment dibuat setelah order siap dibayar.
- Payment status mengikuti status dari Midtrans.
- Webhook harus idempotent.
- Duplicate webhook tidak boleh menggandakan perubahan status atau stok.

### 13.6 Shipping Rules

- Shipping quote dibuat sebelum payment.
- Shipment dapat dibuat setelah payment berhasil.
- Shipping status harus sinkron dengan order.
- Tracking logs disimpan jika tersedia.

### 13.7 Lead Rules

- Customer baru yang chat dapat dibuat sebagai lead.
- Customer yang bertanya produk mendapat lead score.
- Customer yang tanya stok, ongkir, atau payment mendapat score lebih tinggi.
- Lead berubah menjadi converted jika order berhasil dibayar.

---

## 14. Database Design Overview

Database final menggunakan struktur sederhana dengan table utama berikut:

### 14.1 Auth and Users

- `Users`

Menyimpan data admin, superadmin, dan staff.

### 14.2 Customer

- `Customers`
- `CustomerAddresses`

Menyimpan data customer WhatsApp, email, phone, source, alamat, dan histori customer.

### 14.3 Product and Stock

- `Products`
- `StockMovements`

Menyimpan produk sederhana dan riwayat perubahan stok.

### 14.4 Chat and Leads

- `ChatSessions`
- `ChatMessages`
- `Leads`
- `ProductInteractions`

Menyimpan sesi chat WhatsApp, pesan customer/bot, leads, dan event interaksi produk.

### 14.5 Cart and Order

- `Carts`
- `CartItems`
- `Orders`
- `OrderItems`

Menyimpan cart aktif, order, dan snapshot item yang dibeli.

### 14.6 Payment

- `Payments`
- `PaymentWebhookLogs`

Menyimpan transaksi Midtrans dan log webhook.

### 14.7 Shipping

- `ShippingQuotes`
- `Shipments`
- `ShipmentTrackingLogs`

Menyimpan pilihan ongkir, shipment, dan tracking pengiriman.

### 14.8 Product Knowledge

- `ProductKnowledgeDocuments`

Menyimpan knowledge produk untuk chatbot dan calon pengembangan RAG.

---

## 15. API Requirements

### 15.1 Auth API

```txt
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

### 15.2 Product API

```txt
GET    /api/products
POST   /api/products
GET    /api/products/{id}
PATCH  /api/products/{id}
DELETE /api/products/{id}
PATCH  /api/products/{id}/stock
```

### 15.3 WhatsApp / WAHA API

Webhook dari WAHA ke FastAPI:

```txt
POST /api/webhooks/waha/messages
```

Endpoint internal untuk mengirim pesan melalui WAHA:

```txt
POST /api/whatsapp/send-message
```

Optional endpoint:

```txt
GET  /api/whatsapp/sessions
POST /api/whatsapp/sessions/start
POST /api/whatsapp/sessions/stop
```

### 15.4 Chatbot API

```txt
POST /api/chatbot/message
GET  /api/chat-sessions
GET  /api/chat-sessions/{id}
GET  /api/chat-sessions/{id}/messages
```

### 15.5 Cart API

```txt
GET    /api/carts/active
POST   /api/carts/items
PATCH  /api/carts/items/{id}
DELETE /api/carts/items/{id}
```

### 15.6 Order API

```txt
GET  /api/orders
POST /api/orders
GET  /api/orders/{id}
PATCH /api/orders/{id}/status
```

### 15.7 Payment API

```txt
POST /api/payments/midtrans/create
POST /api/webhooks/midtrans
GET  /api/payments/{id}
```

### 15.8 Shipping API

```txt
POST /api/shipping/quotes
POST /api/shipping/quotes/{id}/select
POST /api/shipping/shipments
GET  /api/shipping/shipments/{id}/tracking
```

### 15.9 Leads and Analytics API

```txt
GET   /api/leads
GET   /api/leads/{id}
PATCH /api/leads/{id}
GET   /api/analytics/products
GET   /api/analytics/sales
GET   /api/analytics/chats
```

---

## 16. Frontend Page Requirements

### 16.1 Admin Pages

Admin dashboard terdiri dari:

```txt
/auth/login
/admin/dashboard
/admin/products
/admin/customers
/admin/chats
/admin/leads
/admin/orders
/admin/payments
/admin/shipping
/admin/product-knowledge
```

### 16.2 Dashboard Page

Menampilkan metric utama toko.

Components:

- Revenue card.
- Orders card.
- Customers card.
- Leads card.
- Top asked products table.
- Recent chats.
- Recent orders.
- Low stock alert.

### 16.3 Products Page

Fitur:

- Product table.
- Search product.
- Filter status.
- Create product dialog.
- Edit product form.
- Delete/soft delete product.
- Update stock.

### 16.4 Chats Page

Fitur:

- List chat sessions.
- Filter by WhatsApp channel.
- Chat detail.
- Customer info panel.
- Related product panel.
- AI intent display.

### 16.5 Leads Page

Fitur:

- Lead list.
- Lead score.
- Lead status.
- Interest summary.
- Assign staff.
- Link to chat and customer.

### 16.6 Orders Page

Fitur:

- Order list.
- Filter by order/payment/shipping status.
- Order detail.
- Order item detail.
- Customer address.
- Payment info.
- Shipping info.

---

## 17. Suggested Backend Structure

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
      router.py
      service.py
      schemas.py
      models.py
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
      client.py
      service.py
      schemas.py
    midtrans/
      client.py
      service.py
      schemas.py
    biteship/
      client.py
      service.py
      schemas.py
  shared/
    exceptions.py
    pagination.py
    responses.py
    dependencies.py
```

---

## 18. Suggested Frontend Structure

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
      login.tsx
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
    product.queries.ts
    customer.queries.ts
    chat.queries.ts
    lead.queries.ts
    order.queries.ts
    payment.queries.ts
    shipping.queries.ts
  types/
  hooks/
  utils/
```

---

## 19. MVP Milestones

### Phase 1 — Project Setup

- Setup FastAPI.
- Setup PostgreSQL.
- Setup SQLAlchemy/SQLModel.
- Setup Alembic migration.
- Setup React TypeScript with Vite.
- Setup Tailwind CSS.
- Setup shadcn/ui.
- Setup TanStack Query.
- Setup environment configuration.

### Phase 2 — Core Admin

- Auth admin.
- Users.
- Product CRUD.
- Stock management.
- Customer list.
- Basic dashboard layout.

### Phase 3 — WAHA and Chat Foundation

- Setup WAHA.
- Connect WhatsApp session.
- Create FastAPI webhook for WAHA.
- Store incoming messages.
- Send outgoing messages via WAHA.
- Create chat sessions and messages.

### Phase 4 — AI Product Q&A

- Intent detection.
- Product search.
- Product answer generation.
- Product recommendation.
- Product interaction logging.
- Basic lead creation.

### Phase 5 — Cart and Checkout

- Create cart.
- Add item to cart.
- Cart summary.
- Address collection.
- Create order.
- Create order item snapshot.
- Stock reservation.

### Phase 6 — Biteship Integration

- Get shipping quotes.
- Save quotes.
- Select quote.
- Update order shipping cost.

### Phase 7 — Midtrans Integration

- Create payment.
- Send payment URL to WhatsApp.
- Receive Midtrans webhook.
- Update payment/order status.
- Update stock after payment success.

### Phase 8 — Admin Operations and Analytics

- Chat history page.
- Leads page.
- Orders page.
- Payments page.
- Shipping page.
- Product analytics.
- Sales analytics.

---

## 20. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| AI mengarang produk | Customer mendapat informasi salah | Gunakan tool calling dan database retrieval |
| WAHA session disconnect | Chatbot tidak menerima/mengirim pesan | Buat monitoring session dan reconnect flow |
| Webhook duplicate | Data chat/payment duplikat | Gunakan idempotency key/message ID |
| Payment webhook duplicate | Stok berubah dua kali | Webhook Midtrans harus idempotent |
| Stok tidak sinkron | Overselling | Gunakan reserved_qty dan StockMovements |
| Biteship API error | Checkout terganggu | Simpan error dan tampilkan fallback |
| Customer salah input alamat | Ongkir tidak akurat | Chatbot validasi alamat dan konfirmasi ulang |
| Dashboard lambat | Admin sulit monitoring | Gunakan pagination dan index database |
| Data customer bocor | Risiko privacy | Terapkan auth, role, dan access control |

---

## 21. Success Metrics

### Product Metrics

- Jumlah chat WhatsApp per hari.
- Jumlah customer aktif.
- Jumlah customer yang bertanya produk.
- Jumlah produk yang ditanyakan.
- Jumlah add to cart dari chat.
- Conversion rate dari chat ke order.
- Conversion rate dari order ke paid.

### Business Metrics

- Total revenue.
- Total paid orders.
- Average order value.
- Total leads.
- Total converted leads.
- Produk paling sering dibeli.
- Produk paling sering ditanyakan.

### AI Metrics

- Persentase pertanyaan produk yang berhasil dijawab.
- Jumlah fallback response.
- Jumlah rekomendasi yang menghasilkan cart.
- Jumlah rekomendasi yang menghasilkan order.
- Jumlah kesalahan intent detection.

### Operational Metrics

- WAHA webhook success rate.
- Midtrans webhook success rate.
- Biteship quote success rate.
- Average response time chatbot.
- Order processing time.

---

## 22. Future Improvements

Fitur yang dapat dikembangkan setelah MVP:

- Product variants terpisah.
- Multiple product images.
- Product categories.
- Promo code dan discount.
- Broadcast WhatsApp campaign.
- Human handoff ke admin.
- Multi-admin assignment.
- Customer segmentation.
- Recommendation engine lebih lanjut.
- pgvector untuk semantic product search.
- Product FAQ automation.
- Return/refund management.
- Multi-store atau multi-tenant.
- Integration dengan marketplace.
- Integration dengan Instagram DM.

---

## 23. Final MVP Definition

MVP dianggap selesai jika sistem sudah dapat menjalankan alur berikut secara end-to-end:

```txt
Customer chat WhatsApp
→ WAHA kirim webhook ke FastAPI
→ Chat tersimpan di database
→ AI chatbot menjawab pertanyaan produk
→ Customer memilih produk
→ Sistem membuat cart dan order
→ Sistem mengambil ongkir Biteship
→ Customer memilih pengiriman
→ Sistem membuat payment Midtrans
→ Customer menerima payment URL di WhatsApp
→ Midtrans webhook mengubah status pembayaran
→ Sistem memperbarui order dan stok
→ Admin dapat melihat customer, chat, leads, order, payment, dan shipping di dashboard
```

---

## 24. Conclusion

Project ini adalah platform e-commerce fashion berbasis WhatsApp chatbot yang menggabungkan AI assistant, FastAPI backend, PostgreSQL database, WAHA WhatsApp gateway, Midtrans payment, Biteship shipping, dan React admin dashboard.

Fokus MVP adalah membuktikan bahwa customer dapat melakukan proses belanja dari tanya produk sampai pembayaran melalui WhatsApp, sementara admin dapat memantau semua data operasional dan analytics melalui dashboard.

Dengan struktur ini, project tetap sederhana untuk dibangun pada tahap awal, tetapi sudah memiliki fondasi kuat untuk dikembangkan menjadi conversational commerce platform yang lebih lengkap.

