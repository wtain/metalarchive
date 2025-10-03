from alembic import op
import sqlalchemy as sa


def upgrade():
    # 1. Create batch_runs
    op.create_table(
        "batch_runs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("timestamp", sa.DateTime, nullable=False),
    )

    conn = op.get_bind()

    # 2. Insert distinct timestamps
    conn.execute(sa.text("""
        INSERT INTO batch_runs (timestamp)
        SELECT DISTINCT timestamp FROM post_stats
        UNION
        SELECT DISTINCT timestamp FROM subscribers
        ORDER BY timestamp
    """))

    # 3. Add run_id columns
    op.add_column("post_stats", sa.Column("run_id", sa.Integer, nullable=True))
    op.add_column("subscribers", sa.Column("run_id", sa.Integer, nullable=True))

    # 4. Populate run_id
    conn.execute(sa.text("""
        UPDATE post_stats ps
        SET run_id = br.id
        FROM batch_runs br
        WHERE ps.timestamp = br.timestamp
    """))
    conn.execute(sa.text("""
        UPDATE subscribers s
        SET run_id = br.id
        FROM batch_runs br
        WHERE s.timestamp = br.timestamp
    """))

    # 5. Set NOT NULL and FKs
    op.alter_column("post_stats", "run_id", nullable=False)
    op.alter_column("subscribers", "run_id", nullable=False)
    op.create_foreign_key("fk_poststats_batch", "post_stats", "batch_runs", ["run_id"], ["id"])
    op.create_foreign_key("fk_subscribers_batch", "subscribers", "batch_runs", ["run_id"], ["id"])

    # (Optional: drop old timestamp columns later)
