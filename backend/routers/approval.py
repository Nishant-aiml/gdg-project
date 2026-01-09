"""
Approval API Router.
Provides classification and readiness scoring for approval requests.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
from config.database import get_db, close_db, Batch, Block
from middleware.auth_middleware import get_current_user
from services.approval_classifier import (
    classify_approval,
    get_required_documents,
    calculate_readiness_score,
    normalize_classification
)

router = APIRouter()


@router.get("/approval/{batch_id}")
def get_approval_classification(
    batch_id: str,
    user: Optional[dict] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get approval classification and readiness for a batch.
    
    Returns:
    - classification: category (aicte/ugc/mixed), subtype (new/renewal)
    - required_documents: list of required docs for this subtype
    - readiness_score: percentage of requirements met
    - missing_documents: list of missing required docs
    """
    db = get_db()
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        blocks = db.query(Block).filter(Block.batch_id == batch_id).all()
        
        # Combine all block text for classification
        all_text = ""
        present_docs = []
        extracted_data = {}
        
        for block in blocks:
            if block.evidence_snippet:
                all_text += " " + block.evidence_snippet
            if block.block_type:
                present_docs.append(block.block_type)
            if block.data:
                extracted_data.update(block.data or {})
        
        # Classify - returns dict or ClassificationResult
        classification_raw = classify_approval(all_text)
        classification = normalize_classification(classification_raw)
        
        # Ensure classification is a dict
        if not isinstance(classification, dict):
            classification = {
                "category": batch.mode or "aicte",
                "subtype": "unknown",
                "confidence": 0.0,
                "signals": []
            }
        
        # Get required docs
        category = classification.get("category", batch.mode or "aicte")
        subtype = classification.get("subtype", "unknown")
        required_docs = get_required_documents(category, subtype)
        
        # Calculate readiness
        readiness = calculate_readiness_score(
            classification,
            present_docs,
            extracted_data
        )
        
        # Transform required_docs list of dicts to list of strings
        required_docs_names = []
        required_docs_readable = []
        for doc in required_docs:
            if isinstance(doc, dict):
                doc_name = doc.get("name", "")
                doc_desc = doc.get("description", doc_name)
                if doc_name:
                    required_docs_names.append(doc_name)
                    required_docs_readable.append(doc_desc)
            elif isinstance(doc, str):
                required_docs_names.append(doc)
                required_docs_readable.append(doc)
        
        # Get present documents (found documents)
        documents_found = []
        for doc_name in required_docs_names:
            # Check if this document is present
            doc_name_lower = doc_name.lower()
            found = any(
                doc_name_lower in str(pd).lower() or str(pd).lower() in doc_name_lower
                for pd in present_docs
            )
            if found:
                documents_found.append(doc_name)
        
        # Get document details with confidence
        document_details = []
        for doc_name in required_docs_names:
            doc_name_lower = doc_name.lower()
            found = any(
                doc_name_lower in str(pd).lower() or str(pd).lower() in doc_name_lower
                for pd in present_docs
            )
            # Try to find matching block for confidence
            confidence = 0.0
            for block in blocks:
                if block.block_type and doc_name_lower in block.block_type.lower():
                    confidence = block.confidence or block.extraction_confidence or 0.0
                    break
            
            document_details.append({
                "document_key": doc_name,
                "document_name": doc_name,
                "present": found,
                "confidence": confidence
            })
        
        # Generate recommendation
        readiness_score = readiness.get("readiness_score", 0.0)
        if readiness_score >= 80:
            recommendation = "Your institution is well-prepared for approval. All required documents are present."
        elif readiness_score >= 50:
            recommendation = "Your institution is partially prepared. Upload the missing documents to improve readiness."
        else:
            recommendation = "Your institution needs significant improvement. Please upload the missing required documents to proceed with approval."
        
        return {
            "batch_id": batch_id,
            "mode": batch.mode,
            "classification": readiness.get("classification", classification),
            "required_documents": required_docs_names,
            "required_documents_readable": required_docs_readable,
            "documents_found": documents_found,
            "missing_documents": readiness.get("missing_documents", []),
            "missing_documents_readable": [
                required_docs_readable[required_docs_names.index(m)] if m in required_docs_names
                else m for m in readiness.get("missing_documents", [])
            ],
            "document_details": document_details,
            "readiness_score": readiness_score,
            "recommendation": recommendation,
            "present": readiness.get("present_documents", 0),
            "required": readiness.get("required_documents", len(required_docs_names))
        }
    
    finally:
        close_db(db)


@router.get("/approval/{batch_id}/requirements")
def get_approval_requirements(batch_id: str) -> Dict[str, Any]:
    """
    Get detailed requirements for a batch based on classification.
    """
    db = get_db()
    try:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        blocks = db.query(Block).filter(Block.batch_id == batch_id).all()
        
        # Get text for classification
        all_text = " ".join(
            block.evidence_snippet or "" 
            for block in blocks
        )
        
        classification_raw = classify_approval(all_text)
        classification = normalize_classification(classification_raw)
        
        # Ensure classification is a dict
        if not isinstance(classification, dict):
            classification = {
                "category": batch.mode or "aicte",
                "subtype": "unknown",
                "confidence": 0.0,
                "signals": []
            }
        
        category = classification.get("category", batch.mode or "aicte")
        subtype = classification.get("subtype", "unknown")
        required_docs = get_required_documents(category, subtype)
        
        # Ensure required_docs is a list
        if not isinstance(required_docs, list):
            required_docs = []
        
        return {
            "batch_id": batch_id,
            "category": category,
            "subtype": subtype,
            "required_documents": required_docs,
            "total_required": sum(1 for d in required_docs if isinstance(d, dict) and d.get("required", False)),
            "total_optional": sum(1 for d in required_docs if isinstance(d, dict) and not d.get("required", False))
        }
    
    finally:
        close_db(db)
