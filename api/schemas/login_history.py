from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LoginHistoryResponse(BaseModel):
    login_timestamp: datetime
    ip_address: str | None
    user_agent: str | None

    model_config = ConfigDict(from_attributes=True)
