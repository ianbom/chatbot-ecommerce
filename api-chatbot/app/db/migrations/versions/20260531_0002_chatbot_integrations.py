"""Add chatbot integration fields.

Revision ID: 20260531_0002
Revises: 20260531_0001
Create Date: 2026-05-31
"""

from alembic import op

revision = "20260531_0002"
down_revision = "20260531_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE chat_messages ADD COLUMN IF NOT EXISTS external_message_id VARCHAR(191)")
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS ux_chat_messages_external_message_id "
        "ON chat_messages (external_message_id) WHERE external_message_id IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_payment_webhook_logs_transaction_event "
        "ON payment_webhook_logs (transaction_id, event_type)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_payment_webhook_logs_transaction_event")
    op.execute("DROP INDEX IF EXISTS ux_chat_messages_external_message_id")
    op.execute("ALTER TABLE chat_messages DROP COLUMN IF EXISTS external_message_id")
