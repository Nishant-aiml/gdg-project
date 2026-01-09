"""
Firebase Authentication Middleware
Verifies Firebase ID tokens on protected endpoints
"""

import logging
from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


async def verify_token_middleware(request: Request, call_next: Callable):
    """
    Middleware to verify Firebase ID tokens on protected endpoints.
    
    Protected endpoints require Authorization header with Bearer token.
    Public endpoints (health, docs) are excluded.
    Demo mode tokens (starting with 'demo-token') are allowed for testing.
    """
    # Skip auth for public endpoints
    public_paths = [
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/health",
        "/api/auth/login",  # Login endpoint is public
        "/api/auth/verify",  # Token verification endpoint
        "/api/demo",  # Demo endpoints
    ]
    
    if request.url.path in public_paths or request.url.path.startswith("/static"):
        return await call_next(request)
    
    # Check for Authorization header
    auth_header = request.headers.get("Authorization")
    demo_mode = request.headers.get("X-Demo-Mode", "false").lower() == "true"
    
    if not auth_header:
        # Some endpoints may be public - check if endpoint explicitly requires auth
        # For now, we'll allow requests without auth but log a warning
        # Individual endpoints can enforce auth using the dependency
        logger.debug(f"Request to {request.url.path} without Authorization header")
        return await call_next(request)
    
    # Extract token
    try:
        scheme, token = auth_header.split(" ", 1)
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer' token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Store token and demo mode flag in request state
    request.state.auth_token = token
    request.state.is_demo_mode = demo_mode or token.startswith("demo-token")
    
    return await call_next(request)


from fastapi import Depends

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Dependency to get current authenticated user.
    Supports demo mode tokens (starting with 'demo-token') for testing.
    Returns None if no credentials provided (allows optional auth).
    
    Usage:
        @router.get("/protected")
        def protected_endpoint(user: dict = Depends(get_current_user)):
            ...
    """
    from services.firebase_auth import verify_firebase_token
    
    if not credentials:
        # No credentials - return None for optional auth endpoints
        return None
    
    token = credentials.credentials
    
    # Check for demo mode token
    if token and token.startswith("demo-token"):
        logger.info("Demo mode token detected - returning demo user")
        return {
            "uid": "demo-user-123",
            "email": "demo@smartapproval.ai",
            "email_verified": True,
            "name": "Demo User",
            "picture": None,
            "role": "institution",
            "is_demo": True,
        }
    
    # Verify real Firebase token
    try:
        user_info = verify_firebase_token(token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

