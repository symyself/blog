"""add_fields_for_User

Revision ID: 59d86417acee
Revises: 19699146d4e5
Create Date: 2015-12-03 16:30:23.629541

"""

# revision identifiers, used by Alembic.
revision = '59d86417acee'
down_revision = '19699146d4e5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blog_user', sa.Column('about', sa.Text(), nullable=True))
    op.add_column('blog_user', sa.Column('location', sa.String(length=128), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('blog_user', 'location')
    op.drop_column('blog_user', 'about')
    ### end Alembic commands ###
