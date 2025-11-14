from sqlalchemy import create_engine, Column, Float
from sqlalchemy.ext.declarative import declarative_base
from alembic import op
import sqlalchemy as sa

# Create the database connection
engine = create_engine('sqlite:///./fabric.db', echo=True)

def upgrade():
    # Add tax_rate column to sales table
    op.add_column('sales', sa.Column('tax_rate', sa.Float(), nullable=True))
    
    # Update existing records to calculate and store their tax rate
    connection = op.get_bind()
    connection.execute("""
        UPDATE sales 
        SET tax_rate = CASE 
            WHEN apply_tax = 1 AND (quantity_meters * price_per_meter) > 0 
            THEN (tax / (quantity_meters * price_per_meter)) 
            ELSE 0 
        END
        WHERE tax_rate IS NULL
    """)

def downgrade():
    op.drop_column('sales', 'tax_rate')

if __name__ == '__main__':
    upgrade()