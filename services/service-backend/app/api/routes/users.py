from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from passlib.context import CryptContext

from ...core import get_db, User, UserRole
from ...core.security import get_current_user, get_current_active_admin
from ...schemas.users import CreateUserRequest, InviteUserRequest, UpdateUserRequest, UserListItem
from ...schemas.auth import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=List[UserListItem])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only show team members (not candidates/guests)
    result = await db.execute(
        select(User).where(
            User.is_guest == False,
            User.role.in_([UserRole.ADMIN, UserRole.RECRUITER, UserRole.REVIEWER])
        )
    )
    users = result.scalars().all()
    
    return [
        UserListItem.model_validate({
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'is_guest': user.is_guest,
            'is_active': user.is_active,
            'created_at': user.created_at
        })
        for user in users
    ]


@router.post("", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user with hashed password
    hashed_password = pwd_context.hash(request.password)
    user = User(
        email=request.email,
        password_hash=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
        role=UserRole[request.role],
        is_guest=False,
        is_active=True
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate({
        'id': str(user.id),
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'is_guest': user.is_guest,
        'is_active': user.is_active,
        'created_at': user.created_at
    })


@router.post("/invite", response_model=UserResponse)
async def invite_user(
    request: InviteUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user
    user = User(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        role=UserRole[request.role],
        is_guest=False,
        password_hash=None  # Will be set when they activate account
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # TODO: Send invitation email with activation link
    
    return UserResponse.model_validate({
        'id': str(user.id),
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'is_guest': user.is_guest,
        'is_active': user.is_active,
        'created_at': user.created_at
    })


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if request.role is not None:
        user.role = UserRole[request.role]
    if request.first_name is not None:
        user.first_name = request.first_name
    if request.last_name is not None:
        user.last_name = request.last_name
    if request.is_active is not None:
        user.is_active = request.is_active
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate({
        'id': str(user.id),
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'is_guest': user.is_guest,
        'is_active': user.is_active,
        'created_at': user.created_at
    })
