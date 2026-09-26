"""create durable HAMYLION events"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_events"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "events",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("project_id", sa.String(length=128), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("next_attempt_at", sa.DateTime(), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("dead_lettered_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("project_id", "idempotency_key", name="uq_event_idempotency"),
    )
    for name, column in [
        ("ix_events_project_id", "project_id"),
        ("ix_events_event_type", "event_type"),
        ("ix_events_idempotency_key", "idempotency_key"),
        ("ix_events_status", "status"),
        ("ix_events_next_attempt_at", "next_attempt_at"),
        ("ix_events_published_at", "published_at"),
        ("ix_events_created_at", "created_at"),
    ]:
        op.create_index(name, "events", [column])

def downgrade():
    op.drop_table("events")
