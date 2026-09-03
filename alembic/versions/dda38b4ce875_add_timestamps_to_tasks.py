"""add timestamps to tasks

Revision ID: dda38b4ce875
Revises: d844b7c0bf06
Create Date: 2026-09-03 15:01:20.641551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dda38b4ce875'
down_revision: Union[str, Sequence[str], None] = 'd844b7c0bf06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite cannot ADD COLUMN with a CURRENT_TIMESTAMP default.
    # Recreate the table and copy existing rows; the new defaults populate
    # timestamps for those rows with the migration time.
    with op.batch_alter_table('tasks', recreate='always') as batch_op:
        batch_op.add_column(sa.Column(
            'created_at', sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False,
        ))
        batch_op.add_column(sa.Column(
            'updated_at', sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False,
        ))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('tasks', recreate='always') as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
