from sqlalchemy import Column, String, DateTime, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)  # null for OAuth-only users
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    plan = Column(String(50), default="free")  # free | starter | pro | agency
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Google OAuth tokens
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_token_expiry = Column(DateTime, nullable=True)

    channels = relationship("Channel", back_populates="user", cascade="all, delete-orphan")
    scripts = relationship("Script", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        """Debugging representation of the User model."""
        return (
            f"<User(id={self.id}, email={self.email}, "
            f"plan={self.plan}, is_active={self.is_active})>"
        )