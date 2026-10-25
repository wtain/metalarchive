"""add subscriber_photos table

Revision ID: c3f1a9b27d54
Revises: b5e8d4c7074c
Create Date: 2026-10-25 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f1a9b27d54'
down_revision: Union[str, Sequence[str], None] = 'b5e8d4c7074c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('subscriber_photos',
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('photo_id', sa.BigInteger(), nullable=False),
    sa.Column('file_name', sa.String(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('subscriber_photos')
