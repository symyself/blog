"""add new model : Post

Revision ID: 3029759cde88
Revises: 4db6fe551d5a
Create Date: 2015-12-09 17:24:04.909613

"""

# revision identifiers, used by Alembic.
revision = '3029759cde88'
down_revision = '4db6fe551d5a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blog_post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('alias', sa.String(length=128), nullable=True),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('last_change_time', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['blog_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('alias')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blog_post')
    ### end Alembic commands ###