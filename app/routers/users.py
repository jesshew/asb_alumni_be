from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from app.models.user import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserListResponse
)
from app.services.user_service import UserService
import logging

logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create a new user record."""
    try:
        return UserService.create_user(user_data)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user record"
        )

@router.get("/", response_model=UserListResponse)
async def get_user_list(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Number of items per page"),
    is_admin: Optional[bool] = Query(None, description="Filter by admin status"),
    search: Optional[str] = Query(None, description="Search in name and email")
):
    """Get paginated list of users with optional filters."""
    try:
        result = UserService.get_user_list(
            page=page,
            page_size=page_size,
            is_admin=is_admin,
            search=search
        )
        return UserListResponse(**result)
    except Exception as e:
        logger.error(f"Error fetching user list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user list"
        )

@router.get("/admins", response_model=list[UserResponse])
async def get_admin_users():
    """Get all admin users."""
    try:
        return UserService.get_admin_users()
    except Exception as e:
        logger.error(f"Error fetching admin users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch admin users"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int):
    """Get user by ID."""
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )

@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    """Get user by email."""
    try:
        user = UserService.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user by email {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate):
    """Update a user record."""
    try:
        user = UserService.update_user(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    """Delete a user record."""
    try:
        success = UserService.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        ) 