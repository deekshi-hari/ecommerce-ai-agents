"""rename products.type to product_type

Revision ID: f39c2fa02fda
Revises: 85ab05cfbe8e
Create Date: 2025-09-24 01:17:40.795345

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f39c2fa02fda'
down_revision: Union[str, Sequence[str], None] = '85ab05cfbe8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
