from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.model.enums import ChatChannel, ChatIntent, ChatSenderType, ChatSessionStatus
from app.model.base import Base, TimestampMixin
from app.model.types import pg_enum


class ChatSession(TimestampMixin, Base):
    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("ix_chat_sessions_customer_id", "customer_id"),
        Index("ix_chat_sessions_channel", "channel"),
        Index("ix_chat_sessions_status", "status"),
        Index("ix_chat_sessions_last_message_at", "last_message_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    channel: Mapped[ChatChannel] = mapped_column(
        pg_enum(ChatChannel, "chat_channel"),
        server_default=ChatChannel.web_chatbot.value,
        nullable=False,
    )
    status: Mapped[ChatSessionStatus] = mapped_column(
        pg_enum(ChatSessionStatus, "chat_session_status"),
        server_default=ChatSessionStatus.open.value,
        nullable=False,
    )
    summary: Mapped[str | None] = mapped_column(Text)
    detected_interest: Mapped[dict | None] = mapped_column(JSONB)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("ix_chat_messages_chat_session_id", "chat_session_id"),
        Index("ix_chat_messages_sender_type", "sender_type"),
        Index("ix_chat_messages_intent", "intent"),
        Index("ix_chat_messages_related_product_id", "related_product_id"),
        Index("ix_chat_messages_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    chat_session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    sender_type: Mapped[ChatSenderType] = mapped_column(
        pg_enum(ChatSenderType, "chat_sender_type"), nullable=False
    )
    sender_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[ChatIntent] = mapped_column(
        pg_enum(ChatIntent, "chat_intent"), server_default=ChatIntent.unknown.value, nullable=False
    )
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    related_product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


