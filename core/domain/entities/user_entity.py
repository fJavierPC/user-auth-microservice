from sqlalchemy import Column, Integer, String, Boolean
from infrastructure.config.db_config import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True)
    failed_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
