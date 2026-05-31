from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.cart import Cart, CartItem
from app.model.enums import CartStatus
from app.model.product import Product


def get_or_create_active_cart(session: Session, customer_id: int, chat_session_id: int | None = None) -> Cart:
    cart = session.scalar(
        select(Cart)
        .where(Cart.customer_id == customer_id)
        .where(Cart.status == CartStatus.active)
        .order_by(Cart.id.desc())
    )
    if cart is not None:
        return cart
    cart = Cart(customer_id=customer_id, chat_session_id=chat_session_id, status=CartStatus.active)
    session.add(cart)
    session.flush()
    return cart


def add_product_to_cart(
    session: Session,
    customer_id: int,
    chat_session_id: int,
    product: Product,
    quantity: int,
) -> CartItem:
    cart = get_or_create_active_cart(session, customer_id, chat_session_id)
    cart_item = session.scalar(
        select(CartItem).where(CartItem.cart_id == cart.id).where(CartItem.product_id == product.id)
    )
    if cart_item is None:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price,
            subtotal=product.price * quantity,
        )
        session.add(cart_item)
    else:
        cart_item.quantity += quantity
        cart_item.subtotal = cart_item.unit_price * cart_item.quantity
    session.flush()
    return cart_item


def set_product_quantity(
    session: Session,
    customer_id: int,
    chat_session_id: int,
    product: Product,
    quantity: int,
) -> CartItem:
    cart = get_or_create_active_cart(session, customer_id, chat_session_id)
    cart_item = session.scalar(
        select(CartItem).where(CartItem.cart_id == cart.id).where(CartItem.product_id == product.id)
    )
    if cart_item is None:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price,
            subtotal=product.price * quantity,
        )
        session.add(cart_item)
    else:
        cart_item.quantity = quantity
        cart_item.subtotal = cart_item.unit_price * quantity
    session.flush()
    return cart_item


def active_cart_items(session: Session, customer_id: int) -> list[tuple[CartItem, Product]]:
    cart = session.scalar(
        select(Cart)
        .where(Cart.customer_id == customer_id)
        .where(Cart.status == CartStatus.active)
        .order_by(Cart.id.desc())
    )
    if cart is None:
        return []
    rows = session.execute(
        select(CartItem, Product)
        .join(Product, Product.id == CartItem.product_id)
        .where(CartItem.cart_id == cart.id)
        .order_by(CartItem.id)
    )
    return [(cart_item, product) for cart_item, product in rows]


def cart_total(session: Session, cart_id: int) -> Decimal:
    items = session.scalars(select(CartItem).where(CartItem.cart_id == cart_id))
    return sum((item.subtotal for item in items), Decimal("0"))


def active_cart_total(session: Session, customer_id: int) -> Decimal:
    return sum((item.subtotal for item, _product in active_cart_items(session, customer_id)), Decimal("0"))

def mark_active_cart_ordered(session: Session, customer_id: int) -> None:
    cart = session.scalar(
        select(Cart)
        .where(Cart.customer_id == customer_id)
        .where(Cart.status == CartStatus.active)
        .order_by(Cart.id.desc())
    )
    if cart is not None:
        cart.status = CartStatus.ordered
        session.flush()
