"""empty message

Revision ID: 60837e6f1b71
Revises: 
Create Date: 2017-10-06 09:27:01.213000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60837e6f1b71'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('shoppinglists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], [u'users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shoppingitems',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('price', sa.Integer(), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('in_shoppinglist', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], [u'users.id'], ),
    sa.ForeignKeyConstraint(['in_shoppinglist'], [u'shoppinglists.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shoppingitems')
    op.drop_table('shoppinglists')
    op.drop_table('users')
    # ### end Alembic commands ###