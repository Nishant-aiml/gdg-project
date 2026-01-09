"""
Document Hash Utility
Generates unique hash per document to prevent duplicates
"""

import hashlib
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA256 hash of file content.
    Used for duplicate detection.
    
    Args:
        file_path: Path to file
        
    Returns:
        SHA256 hash as hex string
    """
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            # Read file in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {file_path}: {e}")
        raise


def calculate_content_hash(content: bytes) -> str:
    """
    Calculate SHA256 hash of content bytes.
    
    Args:
        content: File content as bytes
        
    Returns:
        SHA256 hash as hex string
    """
    return hashlib.sha256(content).hexdigest()


def check_duplicate_hash(db, file_hash: str, batch_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """
    Check if a document hash already exists in database.
    
    Args:
        db: Database session
        file_hash: SHA256 hash of file
        batch_id: Optional batch ID to exclude from check
        
    Returns:
        (is_duplicate, existing_batch_id)
    """
    from config.database import File
    
    query = db.query(File).filter(File.document_hash == file_hash)
    
    if batch_id:
        # Exclude current batch from duplicate check
        query = query.filter(File.batch_id != batch_id)
    
    existing_file = query.first()
    
    if existing_file:
        return True, existing_file.batch_id
    
    return False, None

