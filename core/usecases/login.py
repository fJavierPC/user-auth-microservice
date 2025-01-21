from core.domain.services.auth_service import verify_password
from infrastructure.repositories.user_repository import UserRepository


def authenticate_user(username: str, password: str, repo: UserRepository):
    user = repo.get_user_by_username(username)

    if user and user.is_locked:
        return None, "Account is locked due to too many failed attempts."

    if user and verify_password(password, user.password_hash):
        repo.reset_failed_attempts(user)
        return user, None

    if user:
        repo.increment_failed_attempts(user)

    return None, "Invalid credentials"
