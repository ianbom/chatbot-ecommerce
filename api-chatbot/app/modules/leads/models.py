from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.enums import LeadStatus, ProductInteractionType
from app.db.model_base import Base, SoftDeleteMixin, TimestampMixin
from app.db.types import pg_enum


class Lead(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_leads_customer_id", "customer_id"),
        Index("ix_leads_chat_session_id", "chat_session_id"),
        Index("ix_leads_status", "status"),
        Index("ix_leads_lead_score", "lead_score"),
        Index("ix_leads_assigned_to", "assigned_to"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    chat_session_id: Mapped[int | None] = mapped_column(ForeignKey("chat_sessions.id"))
    status: Mapped[LeadStatus] = mapped_column(
        pg_enum(LeadStatus, "lead_status"), server_default=LeadStatus.new.value, nullable=False
    )
    lead_score: Mapped[int] = mapped_column(server_default="0", nullable=False)
    interest_summary: Mapped[str | None] = mapped_column(Text)
    interested_products: Mapped[dict | None] = mapped_column(JSONB)
    assigned_to: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    converted_order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    last_contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ProductInteraction(Base):
    __tablename__ = "product_interactions"
    __table_args__ = (
        Index("ix_product_interactions_customer_id", "customer_id"),
        Index("ix_product_interactions_chat_session_id", "chat_session_id"),
        Index("ix_product_interactions_chat_message_id", "chat_message_id"),
        Index("ix_product_interactions_product_id", "product_id"),
        Index("ix_product_interactions_event_type", "event_type"),
        Index("ix_product_interactions_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    chat_session_id: Mapped[int | None] = mapped_column(ForeignKey("chat_sessions.id"))
    chat_message_id: Mapped[int | None] = mapped_column(ForeignKey("chat_messages.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    event_type: Mapped[ProductInteractionType] = mapped_column(
        pg_enum(ProductInteractionType, "product_interaction_type"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(server_default="1", nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

