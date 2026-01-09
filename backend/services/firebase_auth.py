"""
Firebase Authentication Service
Handles user authentication with Firebase Auth (Email + Google Sign-In)
"""

import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, auth
    FIREBASE_ADMIN_AVAILABLE = True
except ImportError:
    FIREBASE_ADMIN_AVAILABLE = False
    logger.warning("firebase-admin not installed. Install with: pip install firebase-admin")

# Initialize Firebase Admin (singleton pattern)
_firebase_app = None


def initialize_firebase_admin():
    """Initialize Firebase Admin SDK (singleton)"""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    if not FIREBASE_ADMIN_AVAILABLE:
        logger.warning("Firebase Admin SDK not available. Authentication will be disabled.")
        return None
    
    try:
        # Check for service account credentials (production)
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if credentials_path:
            # Resolve relative paths - try relative to project root first, then current directory
            cred_path_obj = Path(credentials_path)
            if not cred_path_obj.is_absolute():
                # Try relative to project root (parent of backend directory)
                project_root = Path(__file__).parent.parent.parent
                cred_path_obj = project_root / credentials_path.lstrip('./')
                if not cred_path_obj.exists():
                    # Try relative to current directory
                    cred_path_obj = Path(credentials_path)
            credentials_path = str(cred_path_obj.resolve())
        
        if credentials_path and Path(credentials_path).exists():
            # Use service account file (recommended for production)
            cred = credentials.Certificate(credentials_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info(f"Firebase Admin initialized with service account credentials: {credentials_path}")
        else:
            # For development: Initialize with project ID from environment
            # This allows token verification without service account file
            # Try FIREBASE_PROJECT_ID first, then NEXT_PUBLIC_FIREBASE_PROJECT_ID (from frontend)
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            if not project_id:
                # Fallback: Try to get from frontend env (for development)
                project_id = os.getenv("NEXT_PUBLIC_FIREBASE_PROJECT_ID")
            
            if project_id:
                # Initialize with project ID (for development)
                # Note: This works for token verification but has limited permissions
                try:
                    _firebase_app = firebase_admin.initialize_app(
                        options={"projectId": project_id}
                    )
                    logger.info(f"Firebase Admin initialized with project ID: {project_id}")
                except ValueError:
                    # App already initialized, get existing app
                    _firebase_app = firebase_admin.get_app()
                    logger.info("Firebase Admin already initialized")
            else:
                # Try default credentials (for local development with gcloud CLI)
                try:
                    _firebase_app = firebase_admin.initialize_app()
                    logger.info("Firebase Admin initialized with default credentials")
                except Exception as default_err:
                    logger.warning(f"Firebase Admin initialization failed: {default_err}")
                    logger.warning("Options:")
                    logger.warning("1. Set GOOGLE_APPLICATION_CREDENTIALS for service account file")
                    logger.warning("2. Set FIREBASE_PROJECT_ID environment variable")
                    logger.warning("3. Use 'gcloud auth application-default login' for default credentials")
                    return None
        
        return _firebase_app
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin: {e}")
        return None


def verify_firebase_token(id_token: str, demo_mode: bool = False) -> Optional[Dict[str, Any]]:
    """
    Verify Firebase ID token and return decoded token claims.
    
    Args:
        id_token: Firebase ID token from client
        demo_mode: If True, allow demo tokens without Firebase verification
        
    Returns:
        Decoded token claims (uid, email, etc.) or None if invalid
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    # Check for demo mode token
    if id_token and id_token.startswith("demo-token"):
        logger.info("Demo mode token detected - bypassing Firebase verification")
        return {
            "uid": "demo-user-123",
            "email": "demo@smartapproval.ai",
            "email_verified": True,
            "name": "Demo User",
            "picture": None,
            "role": "institution",
            "firebase": {},
            "iss": "demo",
            "aud": "demo",
            "auth_time": None,
            "exp": None,
            "is_demo": True,
        }
    
    if not FIREBASE_ADMIN_AVAILABLE:
        logger.warning("Firebase Admin not available. Token verification skipped.")
        return None
    
    # Initialize if not already done
    app = initialize_firebase_admin()
    if app is None:
        logger.warning("Firebase Admin not initialized. Token verification skipped.")
        return None
    
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(id_token)
        
        # Extract user info (including custom claims which are at root level)
        user_info = {
            "uid": decoded_token.get("uid"),
            "email": decoded_token.get("email"),
            "email_verified": decoded_token.get("email_verified", False),
            "name": decoded_token.get("name"),
            "picture": decoded_token.get("picture"),
            "firebase": decoded_token.get("firebase", {}),
            "iss": decoded_token.get("iss"),
            "aud": decoded_token.get("aud"),
            "auth_time": decoded_token.get("auth_time"),
            "exp": decoded_token.get("exp"),
            # Custom claims are at root level of decoded token
            "role": decoded_token.get("role"),  # Custom claim
            "is_demo": False,
        }
        
        logger.debug(f"Firebase token verified for user: {user_info.get('email')}")
        return user_info
        
    except auth.InvalidIdTokenError as e:
        logger.warning(f"Invalid Firebase token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    except auth.ExpiredIdTokenError as e:
        logger.warning(f"Expired Firebase token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired"
        )
    except Exception as e:
        logger.error(f"Error verifying Firebase token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication verification failed"
        )



def get_user_role(user_info: Dict[str, Any]) -> str:
    """
    Extract user role from Firebase custom claims or email domain.
    
    Supported roles (NO ADMIN):
    - institution: @college domain or custom claim (can access all departments)
    - department: @department domain or default (single department only)
    
    Args:
        user_info: Decoded Firebase token claims
        
    Returns:
        Role string: "institution" or "department"
    """
    # Check custom claims first (they're at root level of decoded token)
    if "role" in user_info and user_info["role"]:
        role = user_info["role"]
        # Map old "admin" role to "institution"
        if role == "admin":
            return "institution"
        # Map old "college" role to "institution"
        if role == "college":
            return "institution"
        if role in ["department", "institution"]:
            return role
    
    # Also check nested custom claims (legacy support)
    custom_claims = user_info.get("firebase", {}).get("custom_claims", {})
    if "role" in custom_claims:
        role = custom_claims["role"]
        # Map old "admin" role to "institution"
        if role == "admin":
            return "institution"
        # Map old "college" role to "institution"
        if role == "college":
            return "institution"
        if role in ["department", "institution"]:
            return role
    
    # Fallback to email domain
    email = user_info.get("email", "")
    if not email:
        return "department"  # Default role
    
    email_domain = email.split("@")[-1].lower()
    
    # Role mapping based on domain
    # Institution users: .edu domains or college-related domains
    if email_domain.endswith(".edu") or "college" in email_domain or "university" in email_domain:
        return "institution"
    else:
        return "department"


def set_user_role(uid: str, role: str) -> bool:
    """
    Set custom claims (role) for a Firebase user.
    
    Args:
        uid: Firebase user UID
        role: Role to set ('department' or 'institution')
        
    Returns:
        True if successful, False otherwise
    """
    if not FIREBASE_ADMIN_AVAILABLE:
        logger.warning("Firebase Admin not available. Cannot set user role.")
        return False
    
    # Initialize if not already done
    app = initialize_firebase_admin()
    if app is None:
        logger.warning("Firebase Admin not initialized. Cannot set user role.")
        return False
    
    # Validate role
    if role not in ['department', 'institution']:
        logger.error(f"Invalid role: {role}. Must be 'department' or 'institution'")
        return False
    
    try:
        # Set custom claims
        auth.set_custom_user_claims(uid, {'role': role})
        logger.info(f"Set role '{role}' for user {uid}")
        return True
    except Exception as e:
        logger.error(f"Failed to set user role: {e}")
        return False


def require_auth(token: Optional[str] = None) -> Dict[str, Any]:
    """
    Require authentication and return user info.
    
    Args:
        token: Firebase ID token (from Authorization header)
        
    Returns:
        User info dictionary
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return verify_firebase_token(token)

