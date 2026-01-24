"""core resource tables

Revision ID: 0003_core_resources
Revises: 0002_core_domain
Create Date: 2026-01-24 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_core_resources"
down_revision = "0002_core_domain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("holder_id", sa.Integer, sa.ForeignKey("account_holders.id"), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("balance", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "transfers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("from_account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("to_account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "cards",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("last4", sa.String(length=4), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("cards")
    op.drop_table("transfers")
    op.drop_table("transactions")
    op.drop_table("accounts")
