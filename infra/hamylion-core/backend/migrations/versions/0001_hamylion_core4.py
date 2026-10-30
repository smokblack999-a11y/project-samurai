"""HAMYLION Core 4 baseline; safe for fresh and Core 3 databases."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision='0001_hamylion_core4'
down_revision=None
branch_labels=None
depends_on=None

def _inspector():
    return sa.inspect(op.get_bind())

def _create_index_if_missing(name,table,columns,unique=False):
    insp=_inspector()
    if name not in {x['name'] for x in insp.get_indexes(table)}:
        op.create_index(name,table,columns,unique=unique)

def upgrade():
    insp=_inspector()
    if 'projects' not in insp.get_table_names():
        op.create_table('projects',
            sa.Column('id',sa.String(128),primary_key=True),
            sa.Column('name',sa.String(255),nullable=False))
    if 'api_keys' not in insp.get_table_names():
        op.create_table('api_keys',
            sa.Column('id',sa.String(64),primary_key=True),
            sa.Column('project_id',sa.String(128),nullable=False),
            sa.Column('key_hash',sa.String(128),nullable=False,unique=True),
            sa.Column('active',sa.Boolean(),nullable=False,server_default=sa.true()),
            sa.Column('created_at',sa.DateTime(),nullable=False))
    if 'events' not in insp.get_table_names():
        op.create_table('events',
            sa.Column('id',sa.String(64),primary_key=True),
            sa.Column('project_id',sa.String(128),nullable=False),
            sa.Column('event_type',sa.String(128),nullable=False),
            sa.Column('idempotency_key',sa.String(255),nullable=False),
            sa.Column('payload',postgresql.JSONB(),nullable=False),
            sa.Column('status',sa.String(32),nullable=False,server_default='queued'),
            sa.Column('attempts',sa.Integer(),nullable=False,server_default='0'),
            sa.Column('last_error',sa.Text()),
            sa.Column('created_at',sa.DateTime(),nullable=False),
            sa.Column('delivered_at',sa.DateTime()),
            sa.Column('last_delivered_at',sa.DateTime()),
            sa.Column('delivery_started_at',sa.DateTime()),
            sa.Column('retry_at',sa.DateTime()),
            sa.UniqueConstraint('project_id','idempotency_key',name='uq_event_idempotency'))
    # Upgrade databases created by Core 3's create_all without dropping event data.
    columns={c['name'] for c in _inspector().get_columns('events')}
    for name in ('last_delivered_at','delivery_started_at','retry_at'):
        if name not in columns:
            op.add_column('events',sa.Column(name,sa.DateTime(),nullable=True))
    _create_index_if_missing('ix_projects_id','projects',['id'])
    _create_index_if_missing('ix_api_keys_project_id','api_keys',['project_id'])
    _create_index_if_missing('ix_api_keys_key_hash','api_keys',['key_hash'],unique=True)
    _create_index_if_missing('ix_api_keys_active','api_keys',['active'])
    _create_index_if_missing('ix_events_project_id','events',['project_id'])
    _create_index_if_missing('ix_events_event_type','events',['event_type'])
    _create_index_if_missing('ix_events_idempotency_key','events',['idempotency_key'])
    _create_index_if_missing('ix_events_status','events',['status'])
    _create_index_if_missing('ix_events_delivery_started_at','events',['delivery_started_at'])
    _create_index_if_missing('ix_events_retry_at','events',['retry_at'])

def downgrade():
    op.drop_table('events')
    op.drop_table('api_keys')
    op.drop_table('projects')
