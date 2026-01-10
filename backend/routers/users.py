"""
Users Router
Handles user profile and role management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import logging

from services.firebase_auth import verify_firebase_token
from config.database import get_db, close_db, User

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer(auto_error=False)


class SetRoleRequest(BaseModel):
    """Set user role request"""
    role: str  # 'department' or 'college'


class UserProfileResponse(BaseModel):
    """User profile response"""
    uid: str
    email: str
    name: Optional[str] = None
    role: Optional[str] = None  # null if not set yet
    created_at: Optional[str] = None


@router.post("/set-role")
async def set_user_role(
    request: SetRoleRequest,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Set user role (one-time, first login only).
    
    - Extract UID from Firebase token
    - Create/update user in DB
    - Reject if role already exists (idempotent)
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # Validate role
    if request.role not in ['department', 'college']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be 'department' or 'college'"
        )
    
    try:
        # Verify Firebase token
        user_info = verify_firebase_token(credentials.credentials)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        uid = user_info.get("uid")
        email = user_info.get("email", "")
        name = user_info.get("name", "")
        
        db = get_db()
        try:
            # Check if user exists
            existing_user = db.query(User).filter(User.id == uid).first()
            
            if existing_user:
                # User exists - check if role already set
                if existing_user.role and existing_user.role != 'pending':
                    # Role already set - return success (idempotent)
                    logger.info(f"Role already set for user {uid}: {existing_user.role}")
                    return {
                        "success": True,
                        "message": "Role already set",
                        "role": existing_user.role,
                        "already_set": True
                    }
                else:
                    # Update role
                    existing_user.role = request.role
                    existing_user.last_login = datetime.now(timezone.utc)
                    db.commit()
                    logger.info(f"Updated role for user {uid}: {request.role}")
            else:
                # Create new user
                new_user = User(
                    id=uid,
                    email=email,
                    name=name,
                    role=request.role,
                    created_at=datetime.now(timezone.utc),
                    last_login=datetime.now(timezone.utc)
                )
                db.add(new_user)
                db.commit()
                logger.info(f"Created new user {uid} with role {request.role}")
            
            return {
                "success": True,
                "message": f"Role set to {request.role}",
                "role": request.role,
                "already_set": False
            }
            
        finally:
            close_db(db)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set role error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set user role"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Get current user profile including role.
    
    Returns role=null if not set yet (triggers /select-role redirect).
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        # Verify Firebase token
        user_info = verify_firebase_token(credentials.credentials)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        
        uid = user_info.get("uid")
        email = user_info.get("email", "")
        name = user_info.get("name", "")
        
        db = get_db()
        try:
            # Check if user exists in DB
            existing_user = db.query(User).filter(User.id == uid).first()
            
            if existing_user:
                # Return existing profile
                role = existing_user.role
                # Treat 'pending' as no role
                if role == 'pending':
                    role = None
                    
                return UserProfileResponse(
                    uid=uid,
                    email=existing_user.email,
                    name=existing_user.name,
                    role=role,
                    created_at=existing_user.created_at.isoformat() if existing_user.created_at else None
                )
            else:
                # User doesn't exist in DB yet - return profile without role
                return UserProfileResponse(
                    uid=uid,
                    email=email,
                    name=name,
                    role=None,  # No role yet - triggers /select-role
                    created_at=None
                )
                
        finally:
            close_db(db)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )
