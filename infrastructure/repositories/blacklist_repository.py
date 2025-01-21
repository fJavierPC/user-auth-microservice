from sqlalchemy.orm import Session

from core.domain.entities.blacklisted_token import BlacklistedToken


class BlacklistRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def add_token_to_blacklist(self, token: str):
        blacklisted_token = BlacklistedToken(token=token)
        self.db.add(blacklisted_token)
        self.db.commit()

    def is_token_blacklisted(self, token: str) -> bool:
        return self.db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None
