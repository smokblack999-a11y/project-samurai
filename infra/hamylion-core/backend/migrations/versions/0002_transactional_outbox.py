from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision='0002_transactional_outbox'
down_revision='0001_hamylion_core4'
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('outbox',sa.Column('id',sa.String(64),primary_key=True),sa.Column('event_id',sa.String(64),nullable=False),sa.Column('payload',postgresql.JSONB(),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False),sa.Column('published_at',sa.DateTime()),sa.Column('attempts',sa.Integer(),nullable=False,server_default='0'),sa.Column('last_error',sa.Text()))
    op.create_index('ix_outbox_event_id','outbox',['event_id'])
    op.create_index('ix_outbox_created_at','outbox',['created_at'])
    op.create_index('ix_outbox_published_at','outbox',['published_at'])
def downgrade():
    op.drop_table('outbox')
