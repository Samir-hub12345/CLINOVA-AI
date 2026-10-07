import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class RevokedToken(Base):
    """Stores invalidated / logged-out JWT tokens to enforce server-side authentication revocation."""
    __tablename__ = "revoked_tokens"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    token_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default="logout")

    user = relationship("User")

    @staticmethod
    def hash_token(token: str) -> str:
        """Computes SHA-256 digest of raw JWT string for secure indexing and lookup."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
