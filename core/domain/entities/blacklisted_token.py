from sqlalchemy import Column, String, DateTime
from infrastructure.config.db_config import Base
from datetime import datetime, timezone

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    token = Column(String, primary_key=True, unique=True, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
