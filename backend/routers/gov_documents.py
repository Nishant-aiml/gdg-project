"""
Government Documents Router
Handles upload, parsing, and explanation of government documents (GovEasy)
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import Optional
import logging
import uuid
from pathlib import Path
from config.database import get_db, GovDocument, close_db
from services.gov_documents.parser import GovDocumentParser
from services.firebase_storage import upload_file_to_firebase
from middleware.auth_middleware import get_current_user

router = APIRouter()
parser = GovDocumentParser()
logger = logging.getLogger(__name__)


@router.post("/upload")
async def upload_gov_document(
    file: UploadFile = File(...),
    user: Optional[dict] = Depends(get_current_user)
):
    """
    Upload a government document (circular, letter, scheme) for GovEasy explanation.
    
    Supported formats: PDF, images (PNG, JPG)
    """
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Validate file type
    allowed_types = [
        "application/pdf",
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, PNG, JPG"
        )
    
    # Generate document ID
    doc_id = str(uuid.uuid4())
    
    # Save file temporarily
    temp_dir = Path("storage/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{doc_id}_{file.filename}"
    
    try:
        # Save uploaded file
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Upload to Firebase Storage (if configured) or keep local
        storage_path = None
        try:
            storage_path = upload_file_to_firebase(
                file_path=str(temp_path),
                destination_path=f"gov_documents/{doc_id}/{file.filename}"
            )
        except Exception as e:
            logger.warning(f"Firebase upload failed, using local storage: {e}")
            storage_path = str(temp_path)
        
        # Parse document (extract text)
        logger.info(f"Parsing government document {doc_id}")
        parse_result = parser.parse_document(str(temp_path), file.filename)
        
        # Save to database
        db = get_db()
        try:
            gov_doc = GovDocument(
                id=doc_id,
                uploaded_by=user.get("uid") or user.get("email", "unknown"),
                document_type=parse_result.get("document_type", "document"),
                extracted_text=parse_result.get("extracted_text", ""),
                file_path=storage_path,
                file_name=file.filename,
                is_active=1
            )
            db.add(gov_doc)
            db.commit()
            db.refresh(gov_doc)
            
            return {
                "document_id": doc_id,
                "document_type": gov_doc.document_type,
                "file_name": gov_doc.file_name,
                "extraction_status": "success" if parse_result.get("extracted_text") else "failed",
                "text_length": len(parse_result.get("extracted_text", "")),
                "confidence": parse_result.get("confidence", 0.0),
                "method": parse_result.get("method", "unknown")
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving gov document to database: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to save document: {str(e)}")
        finally:
            close_db(db)
    
    except Exception as e:
        logger.error(f"Error uploading gov document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        # Clean up temp file
        if temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass


@router.get("/{document_id}")
def get_gov_document(
    document_id: str,
    user: Optional[dict] = Depends(get_current_user)
):
    """Get government document metadata."""
    db = get_db()
    try:
        gov_doc = db.query(GovDocument).filter(GovDocument.id == document_id).first()
        if not gov_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check access (user can only see their own documents, or institution users can see all)
        user_role = user.get("role", "department") if user else "department"
        user_id = user.get("uid") or user.get("email", "") if user else ""
        
        # Institution users can see all documents, department users only their own
        if user_role != "institution" and gov_doc.uploaded_by != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "document_id": gov_doc.id,
            "document_type": gov_doc.document_type,
            "file_name": gov_doc.file_name,
            "created_at": gov_doc.created_at.isoformat() if gov_doc.created_at else None,
            "text_length": len(gov_doc.extracted_text) if gov_doc.extracted_text else 0,
            "has_text": bool(gov_doc.extracted_text)
        }
    finally:
        close_db(db)


@router.get("/")
def list_gov_documents(
    user: Optional[dict] = Depends(get_current_user)
):
    """List all government documents for current user."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    db = get_db()
    try:
        user_role = user.get("role", "department")
        user_id = user.get("uid") or user.get("email", "")
        
        if user_role == "institution":
            # Institution users see all documents
            docs = db.query(GovDocument).filter(GovDocument.is_active == 1).all()
        else:
            # Department users see only their own
            docs = db.query(GovDocument).filter(
                GovDocument.uploaded_by == user_id,
                GovDocument.is_active == 1
            ).all()
        
        return {
            "documents": [
                {
                    "document_id": doc.id,
                    "document_type": doc.document_type,
                    "file_name": doc.file_name,
                    "created_at": doc.created_at.isoformat() if doc.created_at else None,
                    "text_length": len(doc.extracted_text) if doc.extracted_text else 0
                }
                for doc in docs
            ],
            "total": len(docs)
        }
    finally:
        close_db(db)

