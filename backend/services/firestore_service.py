"""
Firestore Service Layer
Provides CRUD operations for all collections
Replaces SQLAlchemy ORM operations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from google.cloud.firestore import Client, Query
from config.firestore import get_db, COLLECTIONS

logger = logging.getLogger(__name__)


class FirestoreService:
    """Service layer for Firestore operations"""
    
    def __init__(self):
        self.db = get_db()
    
    # ==================== BATCHES ====================
    
    def create_batch(self, batch_data: Dict[str, Any]) -> str:
        """Create a new batch document"""
        batch_id = batch_data["batch_id"]
        doc_ref = self.db.collection(COLLECTIONS["batches"]).document(batch_id)
        doc_ref.set(batch_data)
        return batch_id
    
    def get_batch(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch by ID"""
        doc_ref = self.db.collection(COLLECTIONS["batches"]).document(batch_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def update_batch(self, batch_id: str, updates: Dict[str, Any]) -> None:
        """Update batch document"""
        updates["updated_at"] = datetime.now(timezone.utc)
        doc_ref = self.db.collection(COLLECTIONS["batches"]).document(batch_id)
        doc_ref.update(updates)
    
    def list_batches(
        self,
        institution_id: Optional[str] = None,
        department_id: Optional[str] = None,
        academic_year: Optional[str] = None,
        accreditation_mode: Optional[str] = None,
        is_valid: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List batches with optional filters"""
        query: Query = self.db.collection(COLLECTIONS["batches"])
        
        if institution_id:
            query = query.where("institution_id", "==", institution_id)
        if department_id:
            query = query.where("department_id", "==", department_id)
        if academic_year:
            query = query.where("academic_year", "==", academic_year)
        if accreditation_mode:
            query = query.where("accreditation_mode", "==", accreditation_mode)
        if is_valid is not None:
            query = query.where("is_valid", "==", is_valid)
        
        query = query.order_by("created_at", direction=Query.DESCENDING).limit(limit)
        docs = query.stream()
        
        return [doc.to_dict() for doc in docs]
    
    # ==================== DOCUMENTS ====================
    
    def create_document(self, document_data: Dict[str, Any]) -> str:
        """Create a new document record"""
        doc_id = document_data["document_id"]
        doc_ref = self.db.collection(COLLECTIONS["documents"]).document(doc_id)
        doc_ref.set(document_data)
        return doc_id
    
    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        doc_ref = self.db.collection(COLLECTIONS["documents"]).document(document_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def list_documents(
        self,
        batch_id: Optional[str] = None,
        institution_id: Optional[str] = None,
        department_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List documents with optional filters"""
        query: Query = self.db.collection(COLLECTIONS["documents"])
        
        if batch_id:
            query = query.where("batch_id", "==", batch_id)
        if institution_id:
            query = query.where("institution_id", "==", institution_id)
        if department_id:
            query = query.where("department_id", "==", department_id)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def check_duplicate_document(self, document_hash: str, exclude_batch_id: Optional[str] = None) -> Optional[str]:
        """Check if document hash already exists, return batch_id if found"""
        query = self.db.collection(COLLECTIONS["documents"]).where("document_hash", "==", document_hash)
        
        if exclude_batch_id:
            query = query.where("batch_id", "!=", exclude_batch_id)
        
        docs = query.limit(1).stream()
        for doc in docs:
            data = doc.to_dict()
            return data.get("batch_id")
        
        return None
    
    # ==================== BLOCKS ====================
    
    def create_block(self, block_data: Dict[str, Any]) -> str:
        """Create a new block document"""
        block_id = block_data["block_id"]
        doc_ref = self.db.collection(COLLECTIONS["blocks"]).document(block_id)
        doc_ref.set(block_data)
        return block_id
    
    def get_block(self, block_id: str) -> Optional[Dict[str, Any]]:
        """Get block by ID"""
        doc_ref = self.db.collection(COLLECTIONS["blocks"]).document(block_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def list_blocks(
        self,
        batch_id: Optional[str] = None,
        block_type: Optional[str] = None,
        is_invalid: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """List blocks with optional filters"""
        query: Query = self.db.collection(COLLECTIONS["blocks"])
        
        if batch_id:
            query = query.where("batch_id", "==", batch_id)
        if block_type:
            query = query.where("block_type", "==", block_type)
        if is_invalid is not None:
            query = query.where("is_invalid", "==", is_invalid)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    def delete_blocks(self, batch_id: str) -> int:
        """Delete all blocks for a batch"""
        blocks = self.list_blocks(batch_id=batch_id)
        batch = self.db.batch()
        count = 0
        
        for block in blocks:
            doc_ref = self.db.collection(COLLECTIONS["blocks"]).document(block["block_id"])
            batch.delete(doc_ref)
            count += 1
        
        if count > 0:
            batch.commit()
        
        return count
    
    # ==================== KPIs ====================
    
    def create_kpi(self, kpi_data: Dict[str, Any]) -> str:
        """Create a new KPI record"""
        kpi_id = kpi_data.get("kpi_id") or f"{kpi_data['batch_id']}_{kpi_data['kpi_name']}"
        doc_ref = self.db.collection(COLLECTIONS["kpis"]).document(kpi_id)
        kpi_data["kpi_id"] = kpi_id
        doc_ref.set(kpi_data)
        return kpi_id
    
    def list_kpis(
        self,
        batch_id: Optional[str] = None,
        institution_id: Optional[str] = None,
        department_id: Optional[str] = None,
        academic_year: Optional[str] = None,
        kpi_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List KPIs with optional filters"""
        query: Query = self.db.collection(COLLECTIONS["kpis"])
        
        if batch_id:
            query = query.where("batch_id", "==", batch_id)
        if institution_id:
            query = query.where("institution_id", "==", institution_id)
        if department_id:
            query = query.where("department_id", "==", department_id)
        if academic_year:
            query = query.where("academic_year", "==", academic_year)
        if kpi_name:
            query = query.where("kpi_name", "==", kpi_name)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    # ==================== COMPLIANCE FLAGS ====================
    
    def create_compliance_flag(self, flag_data: Dict[str, Any]) -> str:
        """Create a new compliance flag"""
        flag_id = flag_data.get("flag_id") or f"{flag_data['batch_id']}_{len(flag_data.get('message', ''))}"
        doc_ref = self.db.collection(COLLECTIONS["compliance_flags"]).document(flag_id)
        flag_data["flag_id"] = flag_id
        doc_ref.set(flag_data)
        return flag_id
    
    def list_compliance_flags(self, batch_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List compliance flags"""
        query: Query = self.db.collection(COLLECTIONS["compliance_flags"])
        
        if batch_id:
            query = query.where("batch_id", "==", batch_id)
        
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    # ==================== TRENDS ====================
    
    def create_trend(self, trend_data: Dict[str, Any]) -> str:
        """Create a new trend record"""
        trend_id = f"{trend_data['institution_id']}_{trend_data['department_id']}_{trend_data['kpi_name']}_{trend_data['year']}"
        doc_ref = self.db.collection(COLLECTIONS["trends"]).document(trend_id)
        trend_data["trend_id"] = trend_id
        doc_ref.set(trend_data)
        return trend_id
    
    def list_trends(
        self,
        institution_id: str,
        department_id: str,
        kpi_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List trends for a department"""
        query: Query = self.db.collection(COLLECTIONS["trends"]).where(
            "institution_id", "==", institution_id
        ).where("department_id", "==", department_id)
        
        if kpi_name:
            query = query.where("kpi_name", "==", kpi_name)
        
        query = query.order_by("year")
        docs = query.stream()
        return [doc.to_dict() for doc in docs]
    
    # ==================== FORECASTS ====================
    
    def create_forecast(self, forecast_data: Dict[str, Any]) -> str:
        """Create a new forecast record"""
        forecast_id = f"{forecast_data['institution_id']}_{forecast_data['department_id']}_{forecast_data['kpi_name']}_{forecast_data['forecast_year']}"
        doc_ref = self.db.collection(COLLECTIONS["forecasts"]).document(forecast_id)
        forecast_data["forecast_id"] = forecast_id
        doc_ref.set(forecast_data)
        return forecast_id
    
    def list_forecasts(
        self,
        institution_id: str,
        department_id: str,
        kpi_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List forecasts for a department"""
        query: Query = self.db.collection(COLLECTIONS["forecasts"]).where(
            "institution_id", "==", institution_id
        ).where("department_id", "==", department_id)
        
        if kpi_name:
            query = query.where("kpi_name", "==", kpi_name)
        
        query = query.order_by("forecast_year")
        docs = query.stream()
        return [doc.to_dict() for doc in docs]

