"""Added roles

Revision ID: 6ef935cdb1d8
Revises: 2e1c74bc0530
Create Date: 2025-04-13 12:19:22.986281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ef935cdb1d8'
down_revision: Union[str, None] = '2e1c74bc0530'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Створення типу ENUM для ролей
    op.execute("""
        CREATE TYPE userrole AS ENUM ('USER', 'ADMIN');
    """)

    # Додавання стовпця 'role' з типом ENUM
    op.add_column('users', sa.Column('role', sa.Enum('USER', 'ADMIN', name='userrole'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    # Видалення стовпця 'role'
    op.drop_column('users', 'role')
    
    # Видалення типу ENUM 'userrole'
    op.execute("""
        DROP TYPE IF EXISTS userrole;
    """)