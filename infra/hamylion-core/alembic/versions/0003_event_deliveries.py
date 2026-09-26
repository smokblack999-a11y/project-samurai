"""add durable websocket clients and delivery state"""
from alembic import op
import sqlalchemy as sa

revision = "0003_event_deliveries"
down_revision = "0002_api_keys"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("websocket_clients",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("project_id", sa.String(length=128), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_websocket_clients_project_id", "websocket_clients", ["project_id"])
    op.create_index("ix_websocket_clients_active", "websocket_clients", ["active"])
    op.create_table("event_deliveries",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("event_id", sa.String(length=64), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.String(length=128), nullable=False),
        sa.Column("client_id", sa.String(length=128), sa.ForeignKey("websocket_clients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("event_id", "client_id", name="uq_event_client_delivery"),
    )
    op.create_index("ix_event_deliveries_event_id", "event_deliveries", ["event_id"])
    op.create_index("ix_event_deliveries_project_id", "event_deliveries", ["project_id"])
    op.create_index("ix_event_deliveries_client_id", "event_deliveries", ["client_id"])
    op.create_index("ix_event_deliveries_status", "event_deliveries", ["status"])

def downgrade():
    op.drop_table("event_deliveries")
    op.drop_table("websocket_clients")