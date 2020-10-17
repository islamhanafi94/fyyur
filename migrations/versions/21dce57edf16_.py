"""empty message

Revision ID: 21dce57edf16
Revises: 9069d2e3708a
Create Date: 2020-10-15 01:09:35.183155

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21dce57edf16'
down_revision = '9069d2e3708a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website_link', sa.String(length=120), nullable=True))
    op.drop_column('artist', 'website')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('artist', 'website_link')
    # ### end Alembic commands ###
