"""Add category_id to events

Revision ID: 66a64917aaf3
Revises: 
Create Date: 2025-06-17 09:40:28.065549
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '66a64917aaf3'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add 'category_id' to 'events' table with named foreign key
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_events_category_id',   # ✅ Named foreign key constraint
            'categories',              # ✅ Matches your table name
            ['category_id'],
            ['id']
        )

    # Modify 'feedback' table
    with op.batch_alter_table('feedback', schema=None) as batch_op:
        batch_op.add_column(sa.Column('submitted_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('rating',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.drop_column('created_at')

def downgrade():
    # Revert changes to 'feedback' table
    with op.batch_alter_table('feedback', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DATETIME(), nullable=True))
        batch_op.alter_column('rating',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.drop_column('submitted_at')

    # Revert changes to 'events' table
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.drop_constraint('fk_events_category_id', type_='foreignkey')  # Use the name we added above
        batch_op.drop_column('category_id')
