from core.domain.entities.user_entity import User
from core.domain.entities.user_login_history_entity import UserLoginHistory

from sqlalchemy.orm import Session

class UserRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def add_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def increment_failed_attempts(self, user: User):
        user.failed_attempts += 1
        if user.failed_attempts >= 3:
            user.is_locked = True
        self.db.commit()

    def reset_failed_attempts(self, user: User):
        user.failed_attempts = 0
        self.db.commit()

    def log_user_login(self, user_id: int, ip_address: str = None, user_agent: str = None):
        login_history = UserLoginHistory(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.db.add(login_history)
        self.db.commit()

    def get_login_history(self, user_id: int, limit: int = 10):
        return (
            self.db.query(UserLoginHistory)
            .filter(UserLoginHistory.user_id == user_id)
            .order_by(UserLoginHistory.login_timestamp.desc())
            .limit(limit)
            .all()
        )
