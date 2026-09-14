"""add posts_embeddings table

Revision ID: d92118edd7ed
Revises: bea9a5ea04f8
Create Date: 2026-09-14 19:58:40.433202

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = 'd92118edd7ed'
down_revision: Union[str, Sequence[str], None] = 'bea9a5ea04f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table('posts_embeddings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('model_name', sa.String(), nullable=False),
    sa.Column('embedding', Vector(384), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_posts_embeddings_post_id'), 'posts_embeddings', ['post_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_posts_embeddings_post_id'), table_name='posts_embeddings')
    op.drop_table('posts_embeddings')
    # extension intentionally left installed - other objects may depend on it
