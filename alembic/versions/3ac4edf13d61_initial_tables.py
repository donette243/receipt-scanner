from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '3ac4edf13d61'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('receipts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('original_filename', sa.String(length=255), nullable=True),
    sa.Column('store', sa.String(length=255), nullable=True),
    sa.Column('receipt_date', sa.String(length=50), nullable=True),
    sa.Column('total', sa.Float(), nullable=True),
    sa.Column('raw_text', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_receipts_id'), 'receipts', ['id'], unique=False)
    op.create_table('receipt_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('receipt_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('quantity', sa.Float(), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['receipt_id'], ['receipts.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_receipt_items_id'), 'receipt_items', ['id'], unique=False)



def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_receipt_items_id'), table_name='receipt_items')
    op.drop_table('receipt_items')
    op.drop_index(op.f('ix_receipts_id'), table_name='receipts')
    op.drop_table('receipts')

