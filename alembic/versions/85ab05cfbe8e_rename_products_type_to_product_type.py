"""rename products.type to product_type

Revision ID: 85ab05cfbe8e
Revises: 02747eef62cd
Create Date: 2025-09-24 01:14:25.539047

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85ab05cfbe8e'
down_revision: Union[str, Sequence[str], None] = '02747eef62cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
