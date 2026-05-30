from enum import StrEnum


class UserRole(StrEnum):
    superadmin = "superadmin"
    admin = "admin"
    staff = "staff"


class CustomerSource(StrEnum):
    chatbot_web = "chatbot_web"
    whatsapp = "whatsapp"
    manual_admin = "manual_admin"


class ProductStatus(StrEnum):
    draft = "draft"
    active = "active"
    inactive = "inactive"
    archived = "archived"


class ProductGender(StrEnum):
    men = "men"
    women = "women"
    unisex = "unisex"


class StockMovementType(StrEnum):
    initial = "initial"
    restock = "restock"
    sale = "sale"
    reservation = "reservation"
    release_reservation = "release_reservation"
    adjustment = "adjustment"
    return_ = "return"


class ChatChannel(StrEnum):
    web_chatbot = "web_chatbot"
    whatsapp = "whatsapp"
    admin = "admin"


class ChatSessionStatus(StrEnum):
    open = "open"
    closed = "closed"
    abandoned = "abandoned"


class ChatSenderType(StrEnum):
    customer = "customer"
    bot = "bot"
    admin = "admin"
    system = "system"


class ChatIntent(StrEnum):
    greeting = "greeting"
    ask_product = "ask_product"
    ask_price = "ask_price"
    ask_stock = "ask_stock"
    ask_size = "ask_size"
    ask_color = "ask_color"
    ask_shipping = "ask_shipping"
    checkout = "checkout"
    payment = "payment"
    track_order = "track_order"
    complaint = "complaint"
    unknown = "unknown"


class LeadStatus(StrEnum):
    new = "new"
    interested = "interested"
    hot = "hot"
    converted = "converted"
    lost = "lost"


class ProductInteractionType(StrEnum):
    asked = "asked"
    recommended = "recommended"
    viewed = "viewed"
    added_to_cart = "added_to_cart"
    booked = "booked"
    purchased = "purchased"


class CartStatus(StrEnum):
    active = "active"
    ordered = "ordered"
    abandoned = "abandoned"
    expired = "expired"


class OrderStatus(StrEnum):
    draft = "draft"
    waiting_payment = "waiting_payment"
    paid = "paid"
    processing = "processing"
    shipped = "shipped"
    completed = "completed"
    cancelled = "cancelled"
    expired = "expired"


class PaymentStatus(StrEnum):
    unpaid = "unpaid"
    pending = "pending"
    paid = "paid"
    failed = "failed"
    expired = "expired"
    cancelled = "cancelled"
    refunded = "refunded"


class ShippingStatus(StrEnum):
    not_created = "not_created"
    waiting_pickup = "waiting_pickup"
    picked_up = "picked_up"
    in_transit = "in_transit"
    delivered = "delivered"
    failed = "failed"
    cancelled = "cancelled"


class PaymentProvider(StrEnum):
    midtrans = "midtrans"


class ShippingProvider(StrEnum):
    biteship = "biteship"
