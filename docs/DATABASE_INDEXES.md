# CreatorIQ Database Indexes

This document describes the database indexes used for query optimization.

## Overview

CreatorIQ uses PostgreSQL with pgvector for vector similarity search. Proper indexing is critical for query performance, especially with large datasets of videos and content gaps.

## Index Strategy

### High-Cardinality Columns
Columns with many unique values (UUIDs, external IDs) use B-tree indexes for equality lookups.

### Full-Text Search
For future full-text search capabilities, GIN indexes can be added to text columns.

### Vector Indexes
pgvector columns use IVF (Inverted File) indexes for approximate nearest neighbor search.

## Users Table

```sql
-- Primary key (automatic)
-- email is unique and frequently queried for auth
CREATE INDEX idx_users_email ON users(email);
```

## Channels Table

```sql
-- youtube_channel_id is unique and used for YouTube API lookups
CREATE UNIQUE INDEX idx_channels_youtube_channel_id ON channels(youtube_channel_id);

-- user_id is used for filtering channels by owner
CREATE INDEX idx_channels_user_id ON channels(user_id);

-- Composite index for user's channels ordered by created_at
CREATE INDEX idx_channels_user_created ON channels(user_id, created_at DESC);

-- analysis_status is used for filtering pending/running/done analysis
CREATE INDEX idx_channels_analysis_status ON channels(analysis_status);
```

## Videos Table

```sql
-- youtube_video_id is unique
CREATE UNIQUE INDEX idx_videos_youtube_video_id ON videos(youtube_video_id);

-- channel_id is used for filtering videos by channel
CREATE INDEX idx_videos_channel_id ON videos(channel_id);

-- Composite index for channel's videos ordered by published_at
CREATE INDEX idx_videos_channel_published ON videos(channel_id, published_at DESC);

-- is_viral for filtering viral content
CREATE INDEX idx_videos_is_viral ON videos(is_viral) WHERE is_viral = true;

-- view_count for sorting by popularity
CREATE INDEX idx_videos_view_count ON videos(view_count DESC);

-- engagement_rate for sorting by engagement
CREATE INDEX idx_videos_engagement ON videos(engagement_rate DESC);

-- Partial index for competitor videos only
CREATE INDEX idx_videos_competitor ON videos(channel_id, is_competitor) 
    WHERE is_competitor = true;
```

## Competitors Table

```sql
-- youtube_channel_id for dedup checking
CREATE INDEX idx_competitors_youtube_channel_id ON competitors(youtube_channel_id);

-- channel_id links competitor to user's channel
CREATE INDEX idx_competitors_channel_id ON competitors(channel_id);

-- analysis_status for filtering
CREATE INDEX idx_competitors_analysis_status ON competitors(analysis_status);

-- Composite for user's competitors
CREATE INDEX idx_competitors_user ON competitors(channel_id, created_at DESC);
```

## Content Gaps Table

```sql
-- channel_id for filtering by channel
CREATE INDEX idx_content_gaps_channel_id ON content_gaps(channel_id);

-- opportunity_score for sorting by opportunity
CREATE INDEX idx_content_gaps_opportunity ON content_gaps(opportunity_score DESC);

-- is_acted_on for filtering gaps not yet covered
CREATE INDEX idx_content_gaps_unacted ON content_gaps(is_acted_on) WHERE is_acted_on = false;

-- Composite for channel's unacted gaps by opportunity
CREATE INDEX idx_content_gaps_channel_opportunity ON content_gaps(channel_id, opportunity_score DESC) 
    WHERE is_acted_on = false;
```

## Scripts Table

```sql
-- user_id for filtering scripts by owner
CREATE INDEX idx_scripts_user_id ON scripts(user_id);

-- channel_id for channel-specific scripts
CREATE INDEX idx_scripts_channel_id ON scripts(channel_id);

-- generation_status for filtering
CREATE INDEX idx_scripts_status ON scripts(generation_status);

-- created_at for sorting
CREATE INDEX idx_scripts_user_created ON scripts(user_id, created_at DESC);
```

## Hooks Table

```sql
-- channel_id for channel-specific hooks
CREATE INDEX idx_hooks_channel_id ON hooks(channel_id);

-- hook_type for filtering by type
CREATE INDEX idx_hooks_type ON hooks(hook_type);

-- predicted_retention_boost for sorting
CREATE INDEX idx_hooks_retention ON hooks(predicted_retention_boost DESC);

-- is_ai_generated for filtering
CREATE INDEX idx_hooks_ai ON hooks(is_ai_generated) WHERE is_ai_generated = true;
```

## Trends Table

```sql
-- velocity_score for finding trending topics
CREATE INDEX idx_trends_velocity ON trends(velocity_score DESC);

-- opportunity_window for filtering
CREATE INDEX idx_trends_opportunity ON trends(opportunity_window);

-- niche for filtering by category
CREATE INDEX idx_trends_niche ON trends(niche);

-- Composite for active trends
CREATE INDEX idx_trends_active ON trends(opportunity_window, velocity_score DESC) 
    WHERE opportunity_window = 'open';
```

## Analysis Jobs Table

```sql
-- entity_id for finding jobs by entity
CREATE INDEX idx_analysis_jobs_entity ON analysis_jobs(entity_id);

-- status for monitoring
CREATE INDEX idx_analysis_jobs_status ON analysis_jobs(status);

-- celery_task_id for task tracking
CREATE INDEX idx_analysis_jobs_celery ON analysis_jobs(celery_task_id);

-- created_at for job ordering
CREATE INDEX idx_analysis_jobs_created ON analysis_jobs(created_at DESC);
```

## Vector Indexes (pgvector)

### Channel Content Embeddings

```sql
-- 1536-dimensional embeddings from text-embedding-3-small
CREATE INDEX idx_channels_content_embedding ON channels 
    USING ivfflat (content_embedding vector_cosine_ops)
    WITH (lists = 100);
```

### Video Content Embeddings

```sql
-- 1536-dimensional embeddings for video similarity search
CREATE INDEX idx_videos_content_embedding ON videos 
    USING ivfflat (content_embedding vector_cosine_ops)
    WITH (lists = 100);
```

## Index Maintenance

### Monitoring Index Usage

```sql
-- Check index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```

### Identifying Unused Indexes

```sql
-- Find indexes with no scans
SELECT 
    schemaname || '.' || tablename AS table,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indrelid) DESC;
```

### Index Bloat

```sql
-- Check for bloated indexes
SELECT 
    schemaname || '.' || tablename AS table,
    indexname,
    pg_size_pretty(pg_relation_size(i.indexrelid)) AS index_size,
    idx_scan,
    n_dead_tup,
    n_live_tup
FROM pg_stat_user_indexes ui
JOIN pg_index i ON ui.indexrelid = i.indexrelid
WHERE idx_scan = 0
ORDER BY pg_relation_size(i.indexrelid) DESC;
```

## Migration Example

When adding a new index via Alembic:

```python
# In your migration file
from alembic import op

def upgrade():
    # Add new index
    op.create_index(
        'idx_channels_user_created',
        'channels',
        ['user_id', 'created_at'],
        postgresql_using='btree'
    )
    
    # For partial index
    op.create_index(
        'idx_videos_is_viral',
        'videos',
        ['is_viral'],
        postgresql_where=sa.text('is_viral = true')
    )
    
    # For vector index
    op.execute('''
        CREATE INDEX idx_channels_content_embedding 
        ON channels USING ivfflat (content_embedding vector_cosine_ops)
        WITH (lists = 100)
    ''')

def downgrade():
    op.drop_index('idx_channels_user_created', table_name='channels')
    op.drop_index('idx_videos_is_viral', table_name='videos')
    op.execute('DROP INDEX idx_channels_content_embedding')
```

## Performance Tips

1. **Index only what you query**: Don't add indexes on columns you rarely filter by
2. **Consider partial indexes**: More efficient when index only applies to subset of rows
3. **Monitor query plans**: Use `EXPLAIN ANALYZE` to verify indexes are being used
4. **Don't over-index**: Each index slows down INSERT/UPDATE operations
5. **Use composite indexes wisely**: Column order matters - put most selective first