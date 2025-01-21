from infrastructure.config.db_config import Base, engine
from core.domain.entities.user_entity import User
from core.domain.entities.user_login_history_entity import UserLoginHistory
from core.domain.entities.blacklisted_token import BlacklistedToken

def init_db():
    print("Registered tables:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    print("Database and tables created.")


if __name__ == "__main__":
    init_db()