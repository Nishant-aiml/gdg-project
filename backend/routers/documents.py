"""
File upload router - SQLite version
Temporary storage only
"""

from fastapi import APIRouter, HTTPException, UploadFile, File as FastAPIFile, Form, Depends
from typing import List, Optional
from schemas.document import DocumentUploadResponse, DocumentResponse, DocumentListResponse
from config.database import get_db, File, Batch, close_db
from config.settings import settings
from utils.id_generator import generate_document_id
from utils.file_utils import save_uploaded_file, get_mime_type
from middleware.auth_middleware import get_current_user
from datetime import datetime, timezone
import shutil
from pathlib import Path

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    batch_id: str = Form(...),
    file: UploadFile = FastAPIFile(...),
    user: Optional[dict] = Depends(get_current_user)
):
    """Upload a file to a batch - PDF only (or JPG/PNG which will be wrapped in PDF)"""
    import logging
    logger = logging.getLogger(__name__)
    
    db = None
    try:
        # Verify batch exists
        db = get_db()
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Check file extension - PDF, JPG, PNG, Excel, CSV, Word allowed
        filename_lower = file.filename.lower()
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.xls', '.csv', '.docx']
        file_ext = Path(filename_lower).suffix
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Allowed file types: PDF, JPG, PNG, Excel (.xlsx, .xls), CSV, Word (.docx). Received: {file_ext}."
            )
        
        # PERFORMANCE: Read file content in chunks and calculate size
        file_size = 0
        file_chunks = []
        
        while True:
            chunk = await file.read(8192)  # Read in 8KB chunks
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB"
                )
            file_chunks.append(chunk)
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Combine chunks into single bytes
        file_content = b"".join(file_chunks)
        
        # GOOGLE INTEGRATION: Upload to Firebase Storage (primary) or local storage (fallback)
        from services.firebase_storage import upload_file_to_firebase, get_firebase_storage_path
        from utils.file_utils import get_mime_type
        
        storage_path = get_firebase_storage_path(batch_id, file.filename)
        content_type = get_mime_type(file.filename)
        
        # Try Firebase Storage first
        firebase_url = upload_file_to_firebase(
            file_content=file_content,
            destination_path=storage_path,
            content_type=content_type,
            metadata={"batch_id": batch_id, "filename": file.filename}
        )
        
        # Fallback to local storage if Firebase Storage is not available
        if firebase_url:
            file_path = storage_path  # Store Firebase path, not local path
            logger.info(f"File uploaded to Firebase Storage: {firebase_url}")
        else:
            # Fallback to local storage
            upload_dir = Path(settings.UPLOAD_DIR) / batch_id
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / file.filename
            
            # Save to local storage
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            file_path = str(file_path)  # Convert to string for DB storage
            logger.info(f"File saved to local storage (Firebase Storage not available): {file_path}")
        
        # Calculate document hash for duplicate detection (use file content, not path)
        import hashlib
        
        try:
            # Calculate hash from file content (works for both Firebase and local)
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Check for duplicate
            from utils.document_hash import check_duplicate_hash
            is_duplicate, existing_batch_id = check_duplicate_hash(db, file_hash, batch_id)
            if is_duplicate:
                # Clean up uploaded file if local
                if not firebase_url and Path(file_path).exists():
                    Path(file_path).unlink()
                raise HTTPException(
                    status_code=409,
                    detail=f"Duplicate document detected. This file already exists in batch {existing_batch_id}"
                )
        except HTTPException:
            raise
        except Exception as hash_error:
            logger.warning(f"Error calculating hash: {hash_error}, continuing without duplicate check")
            file_hash = None
        
        # Create file record
        file_id = generate_document_id()
        
        # Store Firebase URL if available, otherwise local path
        stored_path = firebase_url if firebase_url else str(file_path)
        
        file_record = File(
            id=file_id,
            batch_id=batch_id,
            filename=file.filename,
            filepath=stored_path,  # Firebase URL or local path
            file_size=file_size,
            document_hash=file_hash,  # Store hash for duplicate detection
            uploaded_at=datetime.now(timezone.utc)
        )
        
        db.add(file_record)
        db.commit()
        
        logger.info(f"Successfully uploaded file {file.filename} ({file_size} bytes) to batch {batch_id}")
        
        return DocumentUploadResponse(
            document_id=file_id,
            filename=file.filename,
            file_size=file_size,
            status="uploaded"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        # Clean up partial file if it exists
        if 'file_path' in locals() and file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    finally:
        if db:
            close_db(db)


@router.post("/{batch_id}/upload", response_model=DocumentUploadResponse)
async def upload_document_with_path(
    batch_id: str,
    file: UploadFile = FastAPIFile(...)
):
    """
    Alias endpoint for POST /api/documents/{batch_id}/upload.
    Uses batch_id from URL path parameter.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    db = None
    try:
        # Verify batch exists
        db = get_db()
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Check file extension - PDF, JPG, PNG, Excel, CSV, Word allowed
        filename_lower = file.filename.lower()
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.xlsx', '.xls', '.csv', '.docx']
        file_ext = Path(filename_lower).suffix
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Allowed file types: PDF, JPG, PNG, Excel (.xlsx, .xls), CSV, Word (.docx). Received: {file_ext}."
            )
        
        # PERFORMANCE: Read file content in chunks and calculate size
        file_size = 0
        file_chunks = []
        
        while True:
            chunk = await file.read(8192)  # Read in 8KB chunks
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB"
                )
            file_chunks.append(chunk)
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Combine chunks into single bytes
        file_content = b"".join(file_chunks)
        
        # GOOGLE INTEGRATION: Upload to Firebase Storage (primary) or local storage (fallback)
        from services.firebase_storage import upload_file_to_firebase, get_firebase_storage_path
        from utils.file_utils import get_mime_type
        
        storage_path = get_firebase_storage_path(batch_id, file.filename)
        content_type = get_mime_type(file.filename)
        
        # Try Firebase Storage first
        firebase_url = upload_file_to_firebase(
            file_content=file_content,
            destination_path=storage_path,
            content_type=content_type,
            metadata={"batch_id": batch_id, "filename": file.filename}
        )
        
        # Fallback to local storage if Firebase Storage is not available
        if firebase_url:
            file_path = storage_path  # Store Firebase path, not local path
            logger.info(f"File uploaded to Firebase Storage: {firebase_url}")
        else:
            # Fallback to local storage
            upload_dir = Path(settings.UPLOAD_DIR) / batch_id
            upload_dir.mkdir(parents=True, exist_ok=True)
            file_path = upload_dir / file.filename
            
            # Save to local storage
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            file_path = str(file_path)  # Convert to string for DB storage
            logger.info(f"File saved to local storage (Firebase Storage not available): {file_path}")
        
        # Calculate document hash for duplicate detection (use file content, not path)
        import hashlib
        
        try:
            # Calculate hash from file content (works for both Firebase and local)
            file_hash = hashlib.sha256(file_content).hexdigest()
            
            # Check for duplicate
            is_duplicate, existing_batch_id = check_duplicate_hash(db, file_hash, batch_id)
            if is_duplicate:
                # Clean up uploaded file if local
                if not firebase_url and Path(file_path).exists():
                    Path(file_path).unlink()
                raise HTTPException(
                    status_code=409,
                    detail=f"Duplicate document detected. This file already exists in batch {existing_batch_id}"
                )
        except HTTPException:
            raise
        except Exception as hash_error:
            logger.warning(f"Error calculating hash: {hash_error}, continuing without duplicate check")
            file_hash = None
        
        # Create file record
        file_id = generate_document_id()
        
        # Store Firebase URL if available, otherwise local path
        stored_path = firebase_url if firebase_url else str(file_path)
        
        file_record = File(
            id=file_id,
            batch_id=batch_id,
            filename=file.filename,
            filepath=stored_path,  # Firebase URL or local path
            file_size=file_size,
            document_hash=file_hash,  # Store hash for duplicate detection
            uploaded_at=datetime.now(timezone.utc)
        )
        
        db.add(file_record)
        db.commit()
        
        logger.info(f"Successfully uploaded file {file.filename} ({file_size} bytes) to batch {batch_id}")
        
        return DocumentUploadResponse(
            document_id=file_id,
            filename=file.filename,
            file_size=file_size,
            status="uploaded"
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}", exc_info=True)
        # Clean up partial file if it exists
        if 'file_path' in locals() and file_path.exists():
            try:
                file_path.unlink()
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    finally:
        if db:
            close_db(db)

@router.get("/batch/{batch_id}", response_model=DocumentListResponse)
def list_documents(batch_id: str):
    """List all files in a batch"""
    db = get_db()
    
    try:
        files = db.query(File).filter(File.batch_id == batch_id).all()
        
        doc_responses = [
            DocumentResponse(
                document_id=f.id,
                batch_id=f.batch_id,
                filename=f.filename,
                file_size=f.file_size,
                doc_type=None,  # No document types
                classification_confidence=None,
                status="uploaded",
                quality_flags=[]
            )
            for f in files
        ]
        
        return DocumentListResponse(documents=doc_responses, total=len(doc_responses))
    finally:
        close_db(db)

@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    user: Optional[dict] = Depends(get_current_user)
):
    """Delete a file"""
    db = get_db()
    
    try:
        file_record = db.query(File).filter(File.id == document_id).first()
        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete file
        import os
        if os.path.exists(file_record.filepath):
            os.remove(file_record.filepath)
        
        # Delete record
        db.delete(file_record)
        db.commit()
        
        return {"message": "File deleted successfully"}
    finally:
        close_db(db)
