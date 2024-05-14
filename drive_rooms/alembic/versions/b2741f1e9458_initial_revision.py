"""initial_revision

Revision ID: b2741f1e9458
Revises: 
Create Date: 2024-05-13 21:30:38.178619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2741f1e9458'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rooms',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('files',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('room', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('extension', sa.String(), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=False),
    sa.Column('file_url', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['room'], ['rooms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('files')
    op.drop_table('rooms')
    # ### end Alembic commands ###