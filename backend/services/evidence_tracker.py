"""
Evidence Tracker Service
Tracks document evidence for every extracted value
Ensures traceability: value → snippet → page → source file
"""

from typing import Dict, Any, List, Optional, Tuple
from config.database import Block
import logging

logger = logging.getLogger(__name__)


class EvidenceTracker:
    """
    Tracks evidence for extracted values.
    Every KPI calculation must have evidence.
    """
    
    @staticmethod
    def build_evidence_map(blocks: List[Any]) -> Dict[str, Dict[str, Any]]:
        """
        Build evidence map from blocks (supports both Block objects and dicts).
        
        Returns: {
            "field_name": {
                "snippet": "...",
                "page": 5,
                "source_doc": "filename.pdf",
                "block_id": "...",
                "confidence": 0.85
            }
        }
        """
        evidence_map = {}
        
        for block in blocks:
            # Support both Block objects and dicts
            if isinstance(block, dict):
                block_data = block.get("extracted_data") or block.get("data") or {}
                evidence_snippet = block.get("evidence_snippet")
                evidence_page = block.get("evidence_page")
                source_doc = block.get("source_doc")
                block_id = block.get("id", "")
                confidence = block.get("extraction_confidence") or block.get("confidence", 0.0)
            else:
                # Block object
                block_data = block.data if hasattr(block, 'data') else {}
                evidence_snippet = block.evidence_snippet if hasattr(block, 'evidence_snippet') else None
                evidence_page = block.evidence_page if hasattr(block, 'evidence_page') else None
                source_doc = block.source_doc if hasattr(block, 'source_doc') else None
                block_id = block.id if hasattr(block, 'id') else ""
                confidence = (block.extraction_confidence if hasattr(block, 'extraction_confidence') else None) or \
                            (block.confidence if hasattr(block, 'confidence') else 0.0)
            
            if not block_data or not isinstance(block_data, dict):
                continue
            
            # Extract evidence for each field in block
            for field_name, field_value in block_data.items():
                if field_value is None or field_value == "":
                    continue
                
                # Store evidence if not already present (prefer first occurrence)
                if field_name not in evidence_map:
                    evidence_map[field_name] = {
                        "snippet": evidence_snippet or "",
                        "page": evidence_page or 1,
                        "source_doc": source_doc or "",
                        "block_id": block_id,
                        "confidence": confidence
                    }
        
        return evidence_map
    
    @staticmethod
    def get_evidence_for_field(
        field_name: str,
        evidence_map: Dict[str, Dict[str, Any]],
        aliases: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get evidence for a field, checking aliases.
        
        Args:
            field_name: Primary field name
            evidence_map: Evidence map from build_evidence_map
            aliases: Alternative field names to check
        
        Returns:
            Evidence dict or empty dict if not found
        """
        # Try direct match
        if field_name in evidence_map:
            return evidence_map[field_name]
        
        # Try aliases
        if aliases:
            for alias in aliases:
                if alias in evidence_map:
                    return evidence_map[alias]
        
        # Try common aliases
        common_aliases = {
            "faculty_count": ["faculty", "total_faculty", "teaching_staff"],
            "student_count": ["students", "total_students", "total_intake", "admitted_students"],
            "built_up_area": ["area", "total_area", "building_area", "built_up_area_sqm"],
            "classrooms": ["classroom_count", "number_of_classrooms", "total_classrooms"],
            "library_area": ["library_size", "library_space", "library_area_sqm"],
            "digital_resources": ["digital_library_resources"],
            "hostel_capacity": ["hostel"],
            "placement_rate": ["placement_percentage", "placement_ratio"],
            "total_labs": ["lab_count", "labs", "laboratories"]
        }
        
        for alias in common_aliases.get(field_name, []):
            if alias in evidence_map:
                return evidence_map[alias]
        
        return {}
    
    @staticmethod
    def validate_evidence(
        value: Any,
        evidence: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that a value has evidence.
        
        Returns:
            (is_valid, error_message)
        """
        if value is None:
            return True, None  # None values don't need evidence
        
        # Check if evidence exists
        if not evidence:
            return False, f"Value {value} has no evidence"
        
        # Check if snippet exists
        if not evidence.get("snippet"):
            return False, f"Value {value} has no evidence snippet"
        
        # Check if source doc exists
        if not evidence.get("source_doc"):
            return False, f"Value {value} has no source document"
        
        return True, None
    
    @staticmethod
    def format_evidence_string(evidence: Dict[str, Any]) -> str:
        """
        Format evidence as human-readable string.
        
        Returns:
            "Page 5 in filename.pdf: 'snippet text'"
        """
        if not evidence:
            return "No evidence available"
        
        page = evidence.get("page", "?")
        source = evidence.get("source_doc", "unknown")
        snippet = evidence.get("snippet", "")
        
        # Truncate snippet if too long
        if len(snippet) > 100:
            snippet = snippet[:100] + "..."
        
        return f"Page {page} in {source}: '{snippet}'"

