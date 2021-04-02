"""empty message

Revision ID: 60880ea3d795
Revises: bee7e003e6f2
Create Date: 2021-04-02 15:30:47.974476

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60880ea3d795'
down_revision = 'bee7e003e6f2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('company', sa.Column('store_country', sa.String(length=20), nullable=True))
    op.add_column('company', sa.Column('store_main_currency', sa.String(length=20), nullable=True))
    op.add_column('company', sa.Column('store_main_language', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('company', 'store_main_language')
    op.drop_column('company', 'store_main_currency')
    op.drop_column('company', 'store_country')
    # ### end Alembic commands ###