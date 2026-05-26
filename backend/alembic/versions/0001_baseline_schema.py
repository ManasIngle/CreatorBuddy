"""baseline schema

Revision ID: 0001_baseline
Revises:
Create Date: 2026-05-26 00:00:00.000000

Full initial schema for CreatorIQ.
Creates all tables and installs pgvector extension.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pgvector extension — must exist before Vector columns
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("plan", sa.String(50), server_default="free"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_verified", sa.Boolean, server_default="false"),
        sa.Column("google_access_token", sa.Text, nullable=True),
        sa.Column("google_refresh_token", sa.Text, nullable=True),
        sa.Column("google_token_expiry", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------
    # channels
    # ------------------------------------------------------------------
    op.create_table(
        "channels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("youtube_channel_id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("subscriber_count", sa.Integer, server_default="0"),
        sa.Column("video_count", sa.Integer, server_default="0"),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("country", sa.String(10), nullable=True),
        sa.Column("niche", sa.String(255), nullable=True),
        sa.Column("niche_tags", postgresql.JSON, server_default="[]"),
        sa.Column("audience_type", sa.String(255), nullable=True),
        sa.Column("personality_summary", sa.Text, nullable=True),
        sa.Column("speaking_style", sa.Text, nullable=True),
        sa.Column("storytelling_structure", sa.Text, nullable=True),
        sa.Column("avg_views", sa.Float, server_default="0.0"),
        sa.Column("avg_engagement_rate", sa.Float, server_default="0.0"),
        sa.Column("avg_retention_rate", sa.Float, nullable=True),
        sa.Column("upload_frequency_days", sa.Float, nullable=True),
        sa.Column("best_upload_day", sa.String(20), nullable=True),
        sa.Column("best_upload_hour", sa.Integer, nullable=True),
        sa.Column("last_analyzed_at", sa.DateTime, nullable=True),
        sa.Column("analysis_status", sa.String(50), server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        # pgvector column — raw SQL because SQLAlchemy doesn't natively know Vector
    )
    op.execute(
        "ALTER TABLE channels ADD COLUMN content_embedding vector(1536);"
    )
    op.create_index("ix_channels_youtube_channel_id", "channels", ["youtube_channel_id"], unique=True)
    op.create_index("ix_channels_user_id", "channels", ["user_id"])

    # ------------------------------------------------------------------
    # videos
    # ------------------------------------------------------------------
    op.create_table(
        "videos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("channels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("youtube_video_id", sa.String(20), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("transcript", sa.Text, nullable=True),
        sa.Column("hook_text", sa.Text, nullable=True),
        sa.Column("thumbnail_url", sa.Text, nullable=True),
        sa.Column("duration_seconds", sa.Integer, server_default="0"),
        sa.Column("view_count", sa.Integer, server_default="0"),
        sa.Column("like_count", sa.Integer, server_default="0"),
        sa.Column("comment_count", sa.Integer, server_default="0"),
        sa.Column("engagement_rate", sa.Float, server_default="0.0"),
        sa.Column("estimated_retention_rate", sa.Float, nullable=True),
        sa.Column("tags", postgresql.JSON, server_default="[]"),
        sa.Column("category_id", sa.String(10), nullable=True),
        sa.Column("published_at", sa.DateTime, nullable=False),
        sa.Column("hook_quality_score", sa.Float, nullable=True),
        sa.Column("emotional_triggers", postgresql.JSON, server_default="[]"),
        sa.Column("storytelling_type", sa.String(100), nullable=True),
        sa.Column("pacing_score", sa.Float, nullable=True),
        sa.Column("is_viral", sa.Boolean, server_default="false"),
        sa.Column("is_competitor_video", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.execute(
        "ALTER TABLE videos ADD COLUMN content_embedding vector(1536);"
    )
    op.create_index("ix_videos_youtube_video_id", "videos", ["youtube_video_id"], unique=True)
    op.create_index("ix_videos_channel_id", "videos", ["channel_id"])

    # ------------------------------------------------------------------
    # competitors
    # ------------------------------------------------------------------
    op.create_table(
        "competitors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("channels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("youtube_channel_id", sa.String(100), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("subscriber_count", sa.Integer, server_default="0"),
        sa.Column("avg_views", sa.Float, server_default="0.0"),
        sa.Column("avg_engagement_rate", sa.Float, server_default="0.0"),
        sa.Column("niche_overlap_score", sa.Float, server_default="0.0"),
        sa.Column("why_they_succeed", sa.Text, nullable=True),
        sa.Column("best_formats", postgresql.JSON, server_default="[]"),
        sa.Column("emotional_triggers_used", postgresql.JSON, server_default="[]"),
        sa.Column("content_gaps", postgresql.JSON, server_default="[]"),
        sa.Column("hook_patterns", postgresql.JSON, server_default="[]"),
        sa.Column("upload_frequency_days", sa.Float, nullable=True),
        sa.Column("thumbnail_style", sa.Text, nullable=True),
        sa.Column("last_analyzed_at", sa.DateTime, nullable=True),
        sa.Column("analysis_status", sa.String(50), server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_competitors_channel_id", "competitors", ["channel_id"])
    op.create_index("ix_competitors_youtube_channel_id", "competitors", ["youtube_channel_id"])

    # ------------------------------------------------------------------
    # content_gaps
    # ------------------------------------------------------------------
    op.create_table(
        "content_gaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("channels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic", sa.String(500), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("opportunity_score", sa.Float, server_default="0.0"),
        sa.Column("competition_level", sa.String(20), server_default="medium"),
        sa.Column("estimated_search_demand", sa.String(20), server_default="medium"),
        sa.Column("suggested_angle", sa.Text, nullable=True),
        sa.Column("suggested_title", sa.String(500), nullable=True),
        sa.Column("supporting_evidence", postgresql.JSON, server_default="[]"),
        sa.Column("trend_direction", sa.String(20), server_default="stable"),
        sa.Column("source_type", sa.String(50), server_default="competitor_gap"),
        sa.Column("is_acted_on", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_content_gaps_channel_id", "content_gaps", ["channel_id"])

    # ------------------------------------------------------------------
    # scripts
    # ------------------------------------------------------------------
    op.create_table(
        "scripts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("channels.id", ondelete="SET NULL"), nullable=True),
        sa.Column("topic", sa.String(500), nullable=False),
        sa.Column("target_duration_minutes", sa.Integer, server_default="10"),
        sa.Column("format_type", sa.String(100), server_default="educational"),
        sa.Column("tone", sa.String(100), server_default="conversational"),
        sa.Column("title_suggestions", postgresql.JSON, server_default="[]"),
        sa.Column("hook", sa.Text, nullable=True),
        sa.Column("full_script", sa.Text, nullable=True),
        sa.Column("cta_text", sa.Text, nullable=True),
        sa.Column("short_form_adaptation", sa.Text, nullable=True),
        sa.Column("thumbnail_concept", sa.Text, nullable=True),
        sa.Column("retention_notes", sa.Text, nullable=True),
        sa.Column("generation_status", sa.String(50), server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_scripts_user_id", "scripts", ["user_id"])

    # ------------------------------------------------------------------
    # hooks
    # ------------------------------------------------------------------
    op.create_table(
        "hooks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("channel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("channels.id", ondelete="CASCADE"), nullable=True),
        sa.Column("hook_text", sa.Text, nullable=False),
        sa.Column("hook_type", sa.String(100), nullable=False),
        sa.Column("niche", sa.String(255), nullable=True),
        sa.Column("emotional_trigger", sa.String(100), nullable=True),
        sa.Column("predicted_retention_boost", sa.Float, nullable=True),
        sa.Column("source_video_id", sa.String(20), nullable=True),
        sa.Column("is_ai_generated", sa.Boolean, server_default="true"),
        sa.Column("performance_score", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_hooks_channel_id", "hooks", ["channel_id"])

    # ------------------------------------------------------------------
    # trends
    # ------------------------------------------------------------------
    op.create_table(
        "trends",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("topic", sa.String(500), nullable=False),
        sa.Column("niche", sa.String(255), nullable=True),
        sa.Column("velocity_score", sa.Float, server_default="0.0"),
        sa.Column("saturation_score", sa.Float, server_default="0.0"),
        sa.Column("opportunity_window", sa.String(50), server_default="open"),
        sa.Column("first_detected_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("peak_predicted_at", sa.DateTime, nullable=True),
        sa.Column("evidence", postgresql.JSON, server_default="[]"),
        sa.Column("recommended_action", sa.Text, nullable=True),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("ix_trends_niche", "trends", ["niche"])

    # ------------------------------------------------------------------
    # analysis_jobs
    # ------------------------------------------------------------------
    op.create_table(
        "analysis_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_type", sa.String(100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), server_default="queued"),
        sa.Column("progress_pct", sa.Integer, server_default="0"),
        sa.Column("current_step", sa.String(255), nullable=True),
        sa.Column("result_summary", sa.Text, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("retry_count", sa.Integer, server_default="0"),
        sa.Column("celery_task_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_analysis_jobs_entity_id", "analysis_jobs", ["entity_id"])
    op.create_index("ix_analysis_jobs_status", "analysis_jobs", ["status"])
    op.create_index("ix_analysis_jobs_idempotency_key", "analysis_jobs", ["idempotency_key"], unique=True)

    # ------------------------------------------------------------------
    # pgvector ANN indexes (IVFFlat — build after data loaded in prod)
    # ------------------------------------------------------------------
    op.execute(
        "CREATE INDEX ix_channels_content_embedding ON channels "
        "USING ivfflat (content_embedding vector_cosine_ops) WITH (lists = 100);"
    )
    op.execute(
        "CREATE INDEX ix_videos_content_embedding ON videos "
        "USING ivfflat (content_embedding vector_cosine_ops) WITH (lists = 100);"
    )


def downgrade() -> None:
    op.drop_table("analysis_jobs")
    op.drop_table("trends")
    op.drop_table("hooks")
    op.drop_table("scripts")
    op.drop_table("content_gaps")
    op.drop_table("competitors")
    op.drop_table("videos")
    op.drop_table("channels")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector;")
