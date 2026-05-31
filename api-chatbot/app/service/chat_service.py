from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.chat import ChatMessage, ChatSession
from app.model.customer import Customer
from app.model.enums import ChatChannel, ChatIntent, ChatSenderType, CustomerSource


def get_or_create_whatsapp_customer(session: Session, phone: str, name: str | None = None) -> Customer:
    now = datetime.now(UTC)
    customer = session.scalar(select(Customer).where(Customer.phone == phone))
    if customer is not None:
        customer.last_seen_at = now
        if name and not customer.name:
            customer.name = name
        session.flush()
        return customer

    customer = Customer(
        phone=phone,
        name=name,
        source=CustomerSource.whatsapp,
        first_seen_at=now,
        last_seen_at=now,
    )
    session.add(customer)
    session.flush()
    return customer


def get_or_create_open_session(session: Session, customer: Customer) -> ChatSession:
    chat_session = session.scalar(
        select(ChatSession)
        .where(ChatSession.customer_id == customer.id)
        .where(ChatSession.channel == ChatChannel.whatsapp)
        .order_by(ChatSession.id.desc())
    )
    if chat_session is not None:
        return chat_session

    chat_session = ChatSession(
        customer_id=customer.id,
        channel=ChatChannel.whatsapp,
        started_at=datetime.now(UTC),
        last_message_at=datetime.now(UTC),
    )
    session.add(chat_session)
    session.flush()
    return chat_session


def has_external_message(session: Session, external_message_id: str | None) -> bool:
    if not external_message_id:
        return False
    existing_id = session.scalar(
        select(ChatMessage.id).where(ChatMessage.external_message_id == external_message_id)
    )
    return existing_id is not None


def store_message(
    session: Session,
    chat_session: ChatSession,
    sender_type: ChatSenderType,
    message: str,
    intent: ChatIntent,
    external_message_id: str | None = None,
) -> ChatMessage:
    chat_message = ChatMessage(
        chat_session_id=chat_session.id,
        sender_type=sender_type,
        external_message_id=external_message_id,
        message=message,
        intent=intent,
    )
    chat_session.last_message_at = datetime.now(UTC)
    session.add(chat_message)
    session.flush()
    return chat_message


def get_recent_chat_history(session: Session, chat_session: ChatSession, limit: int = 8) -> str:
    messages = list(
        session.scalars(
            select(ChatMessage)
            .where(ChatMessage.chat_session_id == chat_session.id)
            .order_by(ChatMessage.id.desc())
            .limit(limit)
        )
    )
    messages.reverse()
    lines: list[str] = []
    for message in messages:
        sender = message.sender_type.value if hasattr(message.sender_type, "value") else str(message.sender_type)
        lines.append(f"{sender}: {message.message}")
    return "\n".join(lines)


def get_session_state(chat_session: ChatSession) -> dict:
    return dict(chat_session.metadata_ or {})


def update_session_state(chat_session: ChatSession, updates: dict) -> dict:
    state = get_session_state(chat_session)
    state.update({key: value for key, value in updates.items() if value is not None})
    chat_session.metadata_ = state
    return state
