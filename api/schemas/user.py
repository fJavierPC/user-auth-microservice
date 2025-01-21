from pydantic import BaseModel, Field

class UserPayloadParams(BaseModel):
    username: str = Field(description="Username", max_length=60, min_length=5)
    password: str = Field(description="Username", max_length=60, min_length=8)