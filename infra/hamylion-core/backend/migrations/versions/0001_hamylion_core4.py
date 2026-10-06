"""HAMYLION Core 4 schema"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision='0001_hamylion_core4'
down_revision=None
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('projects',sa.Column('id',sa.String(128),primary_key=True),sa.Column('name',sa.String(255),nullable=False))
    op.create_table('api_keys',sa.Column('id',sa.String(64),primary_key=True),sa.Column('project_id',sa.String(128),nullable=False),sa.Column('key_hash',sa.String(128),nullable=False,unique=True),sa.Column('active',sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_api_keys_project_id','api_keys',['project_id'])
    op.create_index('ix_api_keys_key_hash','api_keys',['key_hash'],unique=True)
    op.create_index('ix_api_keys_active','api_keys',['active'])
    op.create_table('events',sa.Column('id',sa.String(64),primary_key=True),sa.Column('project_id',sa.String(128),nullable=False),sa.Column('event_type',sa.String(128),nullable=False),sa.Column('idempotency_key',sa.String(255),nullable=False),sa.Column('payload',postgresql.JSONB(),nullable=False),sa.Column('status',sa.String(32),nullable=False,server_default='queued'),sa.Column('attempts',sa.Integer(),nullable=False,server_default='0'),sa.Column('last_error',sa.Text()),sa.Column('created_at',sa.DateTime(),nullable=False),sa.Column('delivered_at',sa.DateTime()),sa.Column('last_delivered_at',sa.DateTime()),sa.Column('delivery_started_at',sa.DateTime()),sa.Column('retry_at',sa.DateTime()),sa.UniqueConstraint('project_id','idempotency_key',name='uq_event_idempotency'))
    for name,table,col in [('ix_events_project_id','events','project_id'),('ix_events_event_type','events','event_type'),('ix_events_idempotency_key','events','idempotency_key'),('ix_events_status','events','status'),('ix_events_delivery_started_at','events','delivery_started_at'),('ix_events_retry_at','events','retry_at')]:
        op.create_index(name,table,[col])
def downgrade():
    op.drop_table('events')
    op.drop_table('api_keys')
    op.drop_table('projects')
