Enum UserRole {
  superadmin
  admin
  staff
}

Enum CustomerSource {
  chatbot_web
  whatsapp
  manual_admin
}

Enum ProductStatus {
  draft
  active
  inactive
  archived
}

Enum ProductGender {
  men
  women
  unisex
}

Enum StockMovementType {
  initial
  restock
  sale
  reservation
  release_reservation
  adjustment
  return
}

Enum ChatChannel {
  web_chatbot
  whatsapp
  admin
}

Enum ChatSessionStatus {
  open
  closed
  abandoned
}

Enum ChatSenderType {
  customer
  bot
  admin
  system
}

Enum ChatIntent {
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
}

Enum LeadStatus {
  new
  interested
  hot
  converted
  lost
}

Enum ProductInteractionType {
  asked
  recommended
  viewed
  added_to_cart
  booked
  purchased
}

Enum CartStatus {
  active
  ordered
  abandoned
  expired
}

Enum OrderStatus {
  draft
  waiting_payment
  paid
  processing
  shipped
  completed
  cancelled
  expired
}

Enum PaymentStatus {
  unpaid
  pending
  paid
  failed
  expired
  cancelled
  refunded
}

Enum ShippingStatus {
  not_created
  waiting_pickup
  picked_up
  in_transit
  delivered
  failed
  cancelled
}

Enum PaymentProvider {
  midtrans
}

Enum ShippingProvider {
  biteship
}

Table Users {
  id bigint [pk, increment]
  name varchar(150) [not null]
  email varchar(191) [not null, unique]
  password varchar(255) [not null]

  role UserRole [not null, default: 'admin']
  is_active boolean [not null, default: true]

  last_login_at timestamptz

  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz
}

Table Customers {
  id bigint [pk, increment]

  name varchar(150)
  email varchar(191)
  phone varchar(30)

  source CustomerSource [not null, default: 'chatbot_web']

  first_seen_at timestamptz
  last_seen_at timestamptz

  total_orders int [not null, default: 0]
  total_spent decimal(14,2) [not null, default: 0]

  metadata jsonb

  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  indexes {
    phone
    email
    source
  }
}

Table CustomerAddresses {
  id bigint [pk, increment]
  customer_id bigint [not null, ref: > Customers.id]

  label varchar(100)

  recipient_name varchar(150) [not null]
  recipient_phone varchar(30) [not null]

  province varchar(100)
  city varchar(100)
  district varchar(100)
  subdistrict varchar(100)
  postal_code varchar(20)

  address_line text [not null]

  latitude decimal(10,7)
  longitude decimal(10,7)

  biteship_area_id varchar(100)

  is_default boolean [not null, default: false]

  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  indexes {
    customer_id
    biteship_area_id
    is_default
  }
}

Table Products {
  id bigint [pk, increment]

  name varchar(200) [not null]
  slug varchar(220) [not null, unique]

  description text
  embedding vector

  image_url text

  price decimal(14,2) [not null]

  stock_qty int [not null, default: 0]
  reserved_qty int [not null, default: 0]

  color varchar(100)
  size varchar(50)

  gender ProductGender [not null, default: 'unisex']

  material varchar(150)

  weight_gram int [not null, default: 0]
  length_cm decimal(10,2)
  width_cm decimal(10,2)
  height_cm decimal(10,2)

  status ProductStatus [not null, default: 'draft']
  is_featured boolean [not null, default: false]

  created_by bigint [ref: > Users.id]

  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  indexes {
    slug
    status
    is_featured
    stock_qty
    created_by
  }
}

Table StockMovements {
  id bigint [pk, increment]
  product_id bigint [not null, ref: > Products.id]

  movement_type StockMovementType [not null]
  quantity_change int [not null]

  stock_before int [not null]
  stock_after int [not null]

  reserved_before int [not null, default: 0]
  reserved_after int [not null, default: 0]

  reference_type varchar(50)
  reference_id bigint

  note text

  created_by bigint [ref: > Users.id]

  created_at timestamptz [not null]

  indexes {
    product_id
    movement_type
    reference_type
    reference_id
    created_at
  }
}

Table ChatSessions {
  id bigint [pk, increment]
  customer_id bigint [ref: > Customers.id]

  channel ChatChannel [not null, default: 'web_chatbot']
  status ChatSessionStatus [not null, default: 'open']

  summary text
  detected_interest jsonb

  last_message_at timestamptz
  started_at timestamptz [not null]
  ended_at timestamptz

  metadata jsonb

  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    customer_id
    channel
    status
    last_message_at
  }
}

Table ChatMessages {
  id bigint [pk, increment]
  chat_session_id bigint [not null, ref: > ChatSessions.id]

  sender_type ChatSenderType [not null]
  sender_user_id bigint [ref: > Users.id]

  message text [not null]

  intent ChatIntent [not null, default: 'unknown']
  confidence decimal(5,4)

  related_product_id bigint [ref: > Products.id]

  metadata jsonb

  created_at timestamptz [not null]

  indexes {
    chat_session_id
    sender_type
    intent
    related_product_id
    created_at
  }
}

Table Leads {
  id bigint [pk, increment]

  customer_id bigint [not null, ref: > Customers.id]
  chat_session_id bigint [ref: > ChatSessions.id]

  status LeadStatus [not null, default: 'new']
  lead_score int [not null, default: 0]

  interest_summary text
  interested_products jsonb

  assigned_to bigint [ref: > Users.id]
  converted_order_id bigint [ref: > Orders.id]

  last_contacted_at timestamptz

  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  indexes {
    customer_id
    chat_session_id
    status
    lead_score
    assigned_to
  }
}

Table ProductInteractions {
  id bigint [pk, increment]

  customer_id bigint [ref: > Customers.id]
  chat_session_id bigint [ref: > ChatSessions.id]
  chat_message_id bigint [ref: > ChatMessages.id]

  product_id bigint [not null, ref: > Products.id]

  event_type ProductInteractionType [not null]
  quantity int [not null, default: 1]

  metadata jsonb

  created_at timestamptz [not null]

  indexes {
    customer_id
    chat_session_id
    chat_message_id
    product_id
    event_type
    created_at
  }
}

Table Carts {
  id bigint [pk, increment]

  customer_id bigint [not null, ref: > Customers.id]
  chat_session_id bigint [ref: > ChatSessions.id]

  status CartStatus [not null, default: 'active']

  expires_at timestamptz

  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    customer_id
    chat_session_id
    status
    expires_at
  }
}

Table CartItems {
  id bigint [pk, increment]

  cart_id bigint [not null, ref: > Carts.id]
  product_id bigint [not null, ref: > Products.id]

  quantity int [not null]
  unit_price decimal(14,2) [not null]
  subtotal decimal(14,2) [not null]

  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    cart_id
    product_id
  }
}

Table Orders {
  id bigint [pk, increment]

  order_number varchar(100) [not null, unique]

  customer_id bigint [not null, ref: > Customers.id]
  chat_session_id bigint [ref: > ChatSessions.id]
  customer_address_id bigint [ref: > CustomerAddresses.id]

  status OrderStatus [not null, default: 'draft']
  payment_status PaymentStatus [not null, default: 'unpaid']
  shipping_status ShippingStatus [not null, default: 'not_created']

  subtotal decimal(14,2) [not null, default: 0]
  shipping_cost decimal(14,2) [not null, default: 0]
  discount_total decimal(14,2) [not null, default: 0]
  service_fee decimal(14,2) [not null, default: 0]
  grand_total decimal(14,2) [not null, default: 0]

  currency varchar(10) [not null, default: 'IDR']

  notes text

  expired_at timestamptz
  paid_at timestamptz
  completed_at timestamptz
  cancelled_at timestamptz

  created_at timestamptz [not null]
  updated_at timestamptz [not null]
  deleted_at timestamptz

  indexes {
    order_number
    customer_id
    chat_session_id
    customer_address_id
    status
    payment_status
    shipping_status
    created_at
  }
}

Table OrderItems {
  id bigint [pk, increment]

  order_id bigint [not null, ref: > Orders.id]
  product_id bigint [not null, ref: > Products.id]

  product_name_snapshot varchar(200) [not null]
  product_snapshot jsonb

  quantity int [not null]
  unit_price decimal(14,2) [not null]
  subtotal decimal(14,2) [not null]

  weight_total_gram int [not null, default: 0]

  created_at timestamptz [not null]

  indexes {
    order_id
    product_id
  }
}

Table Payments {
  id bigint [pk, increment]

  order_id bigint [not null, ref: > Orders.id]

  provider PaymentProvider [not null, default: 'midtrans']

  provider_order_id varchar(150) [not null, unique]
  transaction_id varchar(150)

  snap_token text
  payment_url text

  payment_type varchar(50)
  status varchar(50) [not null, default: 'pending']

  gross_amount decimal(14,2) [not null]

  fraud_status varchar(50)
  raw_response jsonb

  paid_at timestamptz
  expired_at timestamptz

  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    order_id
    provider_order_id
    transaction_id
    status
  }
}

Table PaymentWebhookLogs {
  id bigint [pk, increment]

  provider PaymentProvider [not null, default: 'midtrans']
  order_id bigint [ref: > Orders.id]

  transaction_id varchar(150)
  event_type varchar(100)

  signature_valid boolean [not null, default: false]

  payload jsonb [not null]

  processed boolean [not null, default: false]
  processed_at timestamptz

  error_message text

  created_at timestamptz [not null]

  indexes {
    provider
    order_id
    transaction_id
    event_type
    processed
    created_at
  }
}

Table ShippingQuotes {
  id bigint [pk, increment]

  order_id bigint [not null, ref: > Orders.id]

  courier_code varchar(50) [not null]
  courier_name varchar(100) [not null]

  service_code varchar(50)
  service_name varchar(100)

  price decimal(14,2) [not null]
  estimated_delivery varchar(100)

  is_selected boolean [not null, default: false]

  raw_response jsonb

  created_at timestamptz [not null]

  indexes {
    order_id
    courier_code
    service_code
    is_selected
  }
}

Table Shipments {
  id bigint [pk, increment]

  order_id bigint [not null, ref: > Orders.id]

  provider ShippingProvider [not null, default: 'biteship']

  biteship_order_id varchar(150)

  courier_company varchar(100)
  courier_type varchar(100)
  courier_service_name varchar(100)

  tracking_id varchar(150)
  waybill_id varchar(150)

  status varchar(50) [not null, default: 'pending']

  shipping_cost decimal(14,2) [not null, default: 0]

  address_snapshot jsonb
  raw_response jsonb

  shipped_at timestamptz
  delivered_at timestamptz

  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    order_id
    biteship_order_id
    tracking_id
    waybill_id
    status
  }
}

Table ShipmentTrackingLogs {
  id bigint [pk, increment]

  shipment_id bigint [not null, ref: > Shipments.id]

  status varchar(100) [not null]
  description text
  location varchar(200)

  checkpoint_time timestamptz

  raw_payload jsonb

  created_at timestamptz [not null]

  indexes {
    shipment_id
    status
    checkpoint_time
  }
}

Table ProductKnowledgeDocuments {
  id bigint [pk, increment]

  product_id bigint [ref: > Products.id]

  content_type varchar(50) [not null]
  title varchar(200)
  content text [not null]

  embedding text
  metadata jsonb

  created_at timestamptz [not null]
  updated_at timestamptz [not null]

  indexes {
    product_id
    content_type
  }
}

