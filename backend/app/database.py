from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Enhanced engine configuration with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,               # Base connections - adequate for MVP
    max_overflow=10,           # Burst capacity without exhausting DB
    pool_pre_ping=True,         # Verify connections before use
    pool_timeout=30,            # Seconds to wait for connection
    pool_recycle=1800,         # Recycle connections after 30 min
    echo=False,                # Set True for SQL debugging
    # PostgreSQL-specific optimizations
    connect_args={
        "options": "-c statement_timeout=30000"  # 30s query timeout
    } if "postgresql" in settings.DATABASE_URL else {}
)

# Session factory with explicit configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Context manager for database sessions - ensures proper cleanup
from contextlib import contextmanager
from typing import Generator

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Database session context manager with automatic cleanup.
    Use this for background tasks and batch operations.
    
    Usage:
        with get_db_session() as db:
            channel = db.query(Channel).first()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_db():
    """
    FastAPI dependency for database sessions.
    Yields session and ensures cleanup after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Query optimization helper
def add_selectinload_if_needed(query, *relationships):
    """
    Add selectinload for relationships to prevent N+1 queries.
    
    Usage:
        query = add_selectinload_if_needed(
            db.query(Channel),
            Channel.videos,
            Channel.competitors
        )
    """
    from sqlalchemy.orm import selectinload
    for rel in relationships:
        query = query.options(selectinload(rel))
    return query


# Event listener for query performance logging
@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log slow queries (>100ms) for optimization monitoring."""
    conn.info.setdefault("query_start_time", []).append(statement)


@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Calculate and log query execution time."""
    total = cursor.rowcount if hasattr(cursor, 'rowcount') else 0
    logger.debug(f"Query completed: {statement[:100]}... (rows: {total})")