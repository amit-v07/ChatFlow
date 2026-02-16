from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    email: str | None = None
    user_id: str | None = None
