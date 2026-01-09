"""
Government Document Model
Stores uploaded government letters, circulars, and schemes for GovEasy explanation
"""

from sqlalchemy import Column, String, Text, DateTime, Integer
from config.database import Base
from datetime import datetime, timezone


class GovDocument(Base):
    __tablename__ = "gov_documents"
    
    id = Column(String, primary_key=True)  # gov_document_id
    uploaded_by = Column(String, nullable=False, index=True)  # Firebase UID
    document_type = Column(String, nullable=True)  # "circular", "letter", "scheme", "notice", etc.
    extracted_text = Column(Text, nullable=True)  # Full OCR text
    file_path = Column(String, nullable=True)  # Firebase Storage path or local path
    file_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Integer, default=1)  # 0 or 1

