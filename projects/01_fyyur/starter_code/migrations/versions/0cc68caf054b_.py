"""empty message

Revision ID: 0cc68caf054b
Revises: f69c1d4ed258
Create Date: 2021-07-21 18:17:16.650278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cc68caf054b'
down_revision = 'f69c1d4ed258'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_venues', sa.Boolean(), nullable=False))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(), nullable=True))
    op.drop_column('Artist', 'description')
    op.drop_column('Artist', 'looking_for_venues')
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=False))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(), nullable=True))
    op.drop_column('Venue', 'looking_for_talent')
    op.drop_column('Venue', 'description')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('Venue', sa.Column('looking_for_talent', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'seeking_talent')
    op.add_column('Artist', sa.Column('looking_for_venues', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('Artist', sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'seeking_venues')
    # ### end Alembic commands ###
