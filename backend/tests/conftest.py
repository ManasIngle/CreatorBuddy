"""
pytest fixtures shared across all test modules.

Database strategy:
  - Uses SQLite in-memory for speed (no Postgres needed for unit tests).
  - Each test gets a fresh, rolled-back transaction — no data bleeds between tests.

To run:
    cd backend
    source venv/bin/activate
    pytest tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.auth_utils import hash_password, create_access_token

# ---------------------------------------------------------------------------
# In-memory SQLite engine (fast, no external deps)
# ---------------------------------------------------------------------------

SQLITE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session."""
    # pgvector Vector type doesn't exist in SQLite — patch before create_all
    from sqlalchemy import String
    from unittest.mock import patch
    try:
        from pgvector.sqlalchemy import Vector as PGVector
        with patch.object(PGVector, "compile", return_value=String()):
            Base.metadata.create_all(bind=engine)
    except Exception:
        # If patching fails, create without vector columns
        Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """
    Each test gets a clean database session.
    Changes are rolled back after each test.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """FastAPI test client with DB dependency overridden."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------

@pytest.fixture
def test_user(db: Session) -> User:
    """A persisted test user with known credentials."""
    user = User(
        email="test@creatoriq.io",
        hashed_password=hash_password("testpassword123"),
        full_name="Test Creator",
        plan="pro",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Authorization headers for the test user."""
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def free_user(db: Session) -> User:
    """A free-plan user for testing plan-limit enforcement."""
    user = User(
        email="free@creatoriq.io",
        hashed_password=hash_password("freepassword123"),
        full_name="Free Creator",
        plan="free",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def free_auth_headers(free_user: User) -> dict:
    token = create_access_token({"sub": str(free_user.id)})
    return {"Authorization": f"Bearer {token}"}
