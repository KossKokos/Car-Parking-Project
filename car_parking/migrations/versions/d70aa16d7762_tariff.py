"""'tariff'

Revision ID: d70aa16d7762
Revises: 6475a8bbbe39
Create Date: 2024-04-10 15:36:43.478352

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd70aa16d7762'
down_revision = '6475a8bbbe39'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tariffs_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tarriff_name', sa.String(length=30), nullable=False),
    sa.Column('tarriff_value', sa.Numeric(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tarriff_name')
    )
    op.add_column('users_table', sa.Column('tariff', sa.Integer(), nullable=True))
    op.drop_constraint('users_table_license_plate_fkey', 'users_table', type_='foreignkey')
    op.create_foreign_key(None, 'users_table', 'cars_table', ['license_plate'], ['license_plate'])
    op.create_foreign_key(None, 'users_table', 'tariffs_table', ['tariff'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users_table', type_='foreignkey')
    op.drop_constraint(None, 'users_table', type_='foreignkey')
    op.create_foreign_key('users_table_license_plate_fkey', 'users_table', 'cars_table', ['license_plate'], ['license_plate'], ondelete='CASCADE')
    op.drop_column('users_table', 'tariff')
    op.drop_table('tariffs_table')
    # ### end Alembic commands ###