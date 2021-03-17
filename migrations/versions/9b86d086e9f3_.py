"""empty message

Revision ID: 9b86d086e9f3
Revises: 026ff8c5d681
Create Date: 2021-02-18 17:53:22.974384

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b86d086e9f3'
down_revision = '026ff8c5d681'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_detail', sa.Column('monto_devuelto', sa.Float(), nullable=True))
    op.add_column('order_detail', sa.Column('restock', sa.String(length=15), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_detail', 'restock')
    op.drop_column('order_detail', 'monto_devuelto')
    # ### end Alembic commands ###