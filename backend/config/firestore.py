"""
Firebase Firestore Configuration
Replaces SQLite/SQLAlchemy for Railway + Vercel + Firebase deployment
"""

import os
import logging
from typing import Optional
from google.cloud import firestore
from google.oauth2 import service_account
from pathlib import Path

logger = logging.getLogger(__name__)

# Global Firestore client
_db: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """
    Initialize and return Firestore client.
    Uses service account credentials from environment variable.
    """
    global _db
    
    if _db is not None:
        return _db
    
    try:
        # Check for service account credentials
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if credentials_path and Path(credentials_path).exists():
            # Use service account file
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            _db = firestore.Client(credentials=credentials)
            logger.info("Firestore client initialized with service account credentials")
        else:
            # Try default credentials (for local development with gcloud auth)
            _db = firestore.Client()
            logger.info("Firestore client initialized with default credentials")
        
        return _db
    
    except Exception as e:
        logger.error(f"Failed to initialize Firestore client: {e}")
        raise


def get_db() -> firestore.Client:
    """
    Get Firestore database client.
    Alias for get_firestore_client() for compatibility.
    """
    return get_firestore_client()


def close_db(db: Optional[firestore.Client] = None) -> None:
    """
    Close database connection.
    Firestore doesn't require explicit closing, but kept for compatibility.
    """
    # Firestore client doesn't need explicit closing
    pass


# Collection names (constants)
COLLECTIONS = {
    "institutions": "institutions",
    "departments": "departments",
    "batches": "batches",
    "documents": "documents",
    "blocks": "blocks",
    "kpis": "kpis",
    "compliance_flags": "compliance_flags",
    "approval_results": "approval_results",
    "trends": "trends",
    "forecasts": "forecasts"
}

