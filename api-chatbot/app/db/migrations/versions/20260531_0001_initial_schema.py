"""Initial database schema from ERD.

Revision ID: 20260531_0001
Revises:
Create Date: 2026-05-31
"""

from alembic import op

from app.db.base import Base

revision = "20260531_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
