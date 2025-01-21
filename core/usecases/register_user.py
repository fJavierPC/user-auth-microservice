from core.domain.entities.user_entity import User
from core.domain.services.auth_service import hash_password

def register_user(user_id: int, username: str, password: str) -> User:
    password_hash = hash_password(password)
    return User(user_id=user_id, username=username, password_hash=password_hash)