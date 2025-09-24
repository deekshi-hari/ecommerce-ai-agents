"""add status and payment_token to orders

Revision ID: e8baadc509f6
Revises: f39c2fa02fda
Create Date: 2025-09-24 16:39:25.075490

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8baadc509f6'
down_revision: Union[str, Sequence[str], None] = 'f39c2fa02fda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "orders",
        sa.Column("status", sa.String(length=16), nullable=False, server_default=sa.text("'pending'"))
    )
    op.add_column(
        "orders",
        sa.Column("payment_token", sa.String(length=64), nullable=True)
    )
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_unique_constraint("uq_orders_payment_token", "orders", ["payment_token"])

    # optional: remove the default so future inserts must set it explicitly (your app does)
    op.alter_column("orders", "status", server_default=None)

def downgrade():
    op.drop_constraint("uq_orders_payment_token", "orders", type_="unique")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_column("orders", "payment_token")
    op.drop_column("orders", "status")
