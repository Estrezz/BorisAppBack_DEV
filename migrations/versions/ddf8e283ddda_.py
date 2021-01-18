"""empty message

Revision ID: ddf8e283ddda
Revises: 16c06262b3c4
Create Date: 2021-01-18 18:36:39.589338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddf8e283ddda'
down_revision = '16c06262b3c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_detail', sa.Column('variant', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_detail', 'variant')
    # ### end Alembic commands ###