"""
Firebase Storage Service
Handles file uploads to Firebase Storage (replaces local file storage)
"""

import logging
import os
from typing import Optional, BinaryIO
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Google Cloud Storage (Firebase Storage backend)
try:
    from google.cloud import storage
    from google.oauth2 import service_account
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    logger.warning("google-cloud-storage not installed. Install with: pip install google-cloud-storage")

# Global storage client
_storage_client = None
_bucket_name = None


def initialize_firebase_storage(bucket_name: Optional[str] = None):
    """
    Initialize Firebase Storage client.
    
    Args:
        bucket_name: Firebase Storage bucket name (from env or parameter)
    """
    global _storage_client, _bucket_name
    
    if _storage_client is not None:
        return _storage_client, _bucket_name
    
    if not GCS_AVAILABLE:
        logger.warning("Google Cloud Storage not available. File uploads will use local storage.")
        return None, None
    
    try:
        # Get bucket name from env or parameter
        _bucket_name = bucket_name or os.getenv("FIREBASE_STORAGE_BUCKET")
        
        if not _bucket_name:
            logger.warning("FIREBASE_STORAGE_BUCKET not set. File uploads will use local storage.")
            return None, None
        
        # Check for service account credentials
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if credentials_path and Path(credentials_path).exists():
            # Use service account file
            cred = service_account.Credentials.from_service_account_file(credentials_path)
            _storage_client = storage.Client(credentials=cred)
            logger.info(f"Firebase Storage initialized with bucket: {_bucket_name}")
        else:
            # Try default credentials
            try:
                _storage_client = storage.Client()
                logger.info(f"Firebase Storage initialized with default credentials, bucket: {_bucket_name}")
            except Exception as default_err:
                logger.warning(f"Firebase Storage default credentials failed: {default_err}")
                return None, None
        
        return _storage_client, _bucket_name
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Storage: {e}")
        return None, None


def upload_file_to_firebase(
    file_content: bytes,
    destination_path: str,
    content_type: Optional[str] = None,
    metadata: Optional[dict] = None
) -> Optional[str]:
    """
    Upload file to Firebase Storage.
    
    Args:
        file_content: File content as bytes
        destination_path: Path in Firebase Storage (e.g., "batches/{batch_id}/{filename}")
        content_type: MIME type (e.g., "application/pdf")
        metadata: Optional metadata dict
        
    Returns:
        Public URL of uploaded file, or None if upload failed
    """
    client, bucket_name = initialize_firebase_storage()
    
    if client is None or bucket_name is None:
        logger.warning("Firebase Storage not available. Upload skipped.")
        return None
    
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_path)
        
        # Set content type
        if content_type:
            blob.content_type = content_type
        
        # Set metadata
        if metadata:
            blob.metadata = metadata
        
        # Upload file
        blob.upload_from_string(file_content, content_type=content_type)
        
        # Generate signed URL (valid for 1 year)
        url = blob.generate_signed_url(
            expiration=datetime.utcnow() + timedelta(days=365),
            method="GET"
        )
        
        logger.info(f"File uploaded to Firebase Storage: {destination_path}")
        return url
        
    except Exception as e:
        logger.error(f"Error uploading file to Firebase Storage: {e}")
        return None


def download_file_from_firebase(storage_path: str) -> Optional[bytes]:
    """
    Download file from Firebase Storage.
    
    Args:
        storage_path: Path in Firebase Storage
        
    Returns:
        File content as bytes, or None if download failed
    """
    client, bucket_name = initialize_firebase_storage()
    
    if client is None or bucket_name is None:
        logger.warning("Firebase Storage not available. Download skipped.")
        return None
    
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(storage_path)
        
        if not blob.exists():
            logger.warning(f"File not found in Firebase Storage: {storage_path}")
            return None
        
        content = blob.download_as_bytes()
        logger.debug(f"File downloaded from Firebase Storage: {storage_path}")
        return content
        
    except Exception as e:
        logger.error(f"Error downloading file from Firebase Storage: {e}")
        return None


def delete_file_from_firebase(storage_path: str) -> bool:
    """
    Delete file from Firebase Storage.
    
    Args:
        storage_path: Path in Firebase Storage
        
    Returns:
        True if deleted, False otherwise
    """
    client, bucket_name = initialize_firebase_storage()
    
    if client is None or bucket_name is None:
        logger.warning("Firebase Storage not available. Delete skipped.")
        return False
    
    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(storage_path)
        
        if blob.exists():
            blob.delete()
            logger.info(f"File deleted from Firebase Storage: {storage_path}")
            return True
        else:
            logger.warning(f"File not found in Firebase Storage: {storage_path}")
            return False
        
    except Exception as e:
        logger.error(f"Error deleting file from Firebase Storage: {e}")
        return False


def get_firebase_storage_path(batch_id: str, filename: str) -> str:
    """
    Generate Firebase Storage path for a file.
    
    Args:
        batch_id: Batch ID
        filename: Original filename
        
    Returns:
        Storage path (e.g., "batches/{batch_id}/{filename}")
    """
    # Sanitize filename (remove path separators)
    safe_filename = filename.replace("/", "_").replace("\\", "_")
    return f"batches/{batch_id}/{safe_filename}"

