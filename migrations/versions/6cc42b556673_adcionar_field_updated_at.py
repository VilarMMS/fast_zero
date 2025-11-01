"""adcionar field updated_at

Revision ID: 6cc42b556673
Revises: 61d39b44c0f3
Create Date: 2025-11-01 11:26:31.295093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cc42b556673'
down_revision: Union[str, Sequence[str], None] = '61d39b44c0f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',
                    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
)


def downgrade() -> None:
    op.drop_column('users',
                   'updated_at')
