from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...core import get_db, User, UserRole, SystemSettings
from ...core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)
from ...schemas.auth import (
    LoginRequest,
    TokenResponse,
    SetupAdminRequest,
    SetPasswordRequest,
    ResetPasswordRequest,
    UserResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(access_token=access_token)


@router.post("/setup-admin", response_model=TokenResponse)
async def setup_admin(
    request: SetupAdminRequest,
    db: AsyncSession = Depends(get_db)
):
    # Check if any admin exists
    result = await db.execute(
        select(User).where(User.role == UserRole.ADMIN)
    )
    existing_admin = result.scalar_one_or_none()
    
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin already exists. Use login instead."
        )
    
    # Create admin user
    admin = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        role=UserRole.ADMIN,
        is_guest=False
    )
    
    db.add(admin)
    
    # Create default system settings
    settings = SystemSettings(
        id=1,
        company_name="My Company"
    )
    db.add(settings)
    
    await db.commit()
    await db.refresh(admin)
    
    access_token = create_access_token(data={"sub": str(admin.id)})
    
    return TokenResponse(access_token=access_token)


@router.post("/set-password")
async def set_password(request: SetPasswordRequest):
    return {"message": "Set password - to be implemented with email tokens"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    return {"message": "Reset password - to be implemented with email service"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate({
        'id': str(current_user.id),
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'role': current_user.role,
        'is_guest': current_user.is_guest,
        'is_active': current_user.is_active,
        'created_at': current_user.created_at
    })
