from fastapi import APIRouter, Depends
from api.schemas.login_history import LoginHistoryResponse
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.services.jwt_service import get_current_user
from infrastructure.config.db_config import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/login-history", response_model=list[LoginHistoryResponse])
def get_login_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 10
):
    """
    Obtiene el historial de inicios de sesión del usuario autenticado.
    """
    repo = UserRepository(db)
    history = repo.get_login_history(user_id=current_user["user_id"], limit=limit)

    # Usar model_validate para mapear objetos ORM al modelo Pydantic
    return [LoginHistoryResponse.model_validate(h) for h in history]