from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.dependencies import get_current_active_user


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: Valid email address (unique)
    - **password**: Password (min 8 characters)
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        is_active=True
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login and get JWT tokens.
    
    - **email**: User email
    - **password**: User password
    
    Returns access token and refresh token.
    """
    # Get user from database
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()
    
    # Verify user exists and password is correct
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": user.email, "user_id": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and refresh token.
    """
    # Decode refresh token
    payload = decode_token(refresh_token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify token type
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    # Get user email
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Verify user exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    new_access_token = create_access_token(data={"sub": user.email, "user_id": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": user.email, "user_id": str(user.id)})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information.
    
    Requires valid access token in Authorization header.
    """
    return current_user
