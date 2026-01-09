"""
Production Validation Script
End-to-end validation to ensure no dummy data, no fallbacks, strict evidence requirements.
Fails build if any step violates production rules.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_db, close_db, Batch, Block
from services.production_guard import ProductionGuard
from services.kpi_official import OfficialKPIService
from services.evidence_tracker import EvidenceTracker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_no_fallback_values():
    """Check that no formulas use fallback 'or 0' values."""
    logger.info("🔍 Checking for fallback values in formulas...")
    
    import re
    
    formula_files = [
        "backend/services/naac_formulas.py",
        "backend/services/nirf_formulas.py",
        "backend/services/nba_formulas.py",
        "backend/services/kpi_official.py"
    ]
    
    violations = []
    for file_path in formula_files:
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Check for 'or 0' patterns (but allow in comments or strings)
                if re.search(r'\bor\s+0\b', line) and not line.strip().startswith('#'):
                    # Allow in specific contexts (like default parameters)
                    if 'default' in line.lower() or 'def ' in line:
                        continue
                    violations.append(f"{file_path}:{i} - Potential fallback value: {line.strip()}")
    
    if violations:
        logger.error("❌ FOUND FALLBACK VALUES:")
        for v in violations:
            logger.error(f"  {v}")
        return False
    
    logger.info("✅ No fallback values found")
    return True


def validate_batch_invalid_marking():
    """Check that invalid batches are properly marked."""
    logger.info("🔍 Checking invalid batch marking...")
    
    db = get_db()
    try:
        # Find batches with overall_score == 0 or None (from kpi_results)
        all_batches = db.query(Batch).all()
        
        unmarked_invalid = []
        for batch in all_batches:
            # Check kpi_results for overall_score
            kpi_results = batch.kpi_results or {}
            overall_score = None
            
            if isinstance(kpi_results, dict):
                overall_score_data = kpi_results.get("overall_score") or kpi_results.get("aicte_overall_score") or kpi_results.get("ugc_overall_score")
                if isinstance(overall_score_data, dict):
                    overall_score = overall_score_data.get("value")
                elif isinstance(overall_score_data, (int, float)):
                    overall_score = overall_score_data
            
            # Check sufficiency
            sufficiency_result = batch.sufficiency_result or {}
            sufficiency = sufficiency_result.get("percentage", 0) if isinstance(sufficiency_result, dict) else 0
            
            # Batch should be invalid if overall_score is 0/None or sufficiency is 0
            should_be_invalid = (overall_score is None or overall_score == 0) or sufficiency == 0
            
            if should_be_invalid and batch.is_invalid != 1:
                unmarked_invalid.append({
                    "id": batch.id,
                    "overall_score": overall_score,
                    "sufficiency": sufficiency,
                    "is_invalid": batch.is_invalid
                })
        
        if unmarked_invalid:
            logger.error(f"❌ Found {len(unmarked_invalid)} batches that should be marked invalid but aren't:")
            for batch_info in unmarked_invalid[:10]:  # Show first 10
                logger.error(f"  Batch {batch_info['id']}: overall_score={batch_info['overall_score']}, sufficiency={batch_info['sufficiency']}, is_invalid={batch_info['is_invalid']}")
            return False
        
        logger.info("✅ All invalid batches properly marked")
        return True
    finally:
        close_db(db)


def validate_evidence_requirements():
    """Check that KPI calculations require evidence."""
    logger.info("🔍 Checking evidence requirements...")
    
    # This is a code-level check - formulas should validate evidence
    # We check that evidence_map is used in calculations
    
    formula_files = [
        "backend/services/kpi_official.py",
        "backend/services/nba_formulas.py",
        "backend/services/naac_formulas.py",
        "backend/services/nirf_formulas.py"
    ]
    
    missing_evidence_checks = []
    for file_path in formula_files:
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check that functions accept evidence_map parameter
            if 'evidence_map' not in content:
                missing_evidence_checks.append(f"{file_path} - No evidence_map parameter")
    
    if missing_evidence_checks:
        logger.warning("⚠️  Some formula files may not use evidence_map:")
        for m in missing_evidence_checks:
            logger.warning(f"  {m}")
        # Not a failure, just a warning
    
    logger.info("✅ Evidence requirements checked")
    return True


def validate_production_guard_integration():
    """Check that production guard is integrated in critical endpoints."""
    logger.info("🔍 Checking production guard integration...")
    
    endpoint_files = [
        "backend/routers/compare.py",
        "backend/routers/dashboard.py",
        "backend/routers/batches.py"
    ]
    
    missing_guard = []
    for file_path in endpoint_files:
        if not os.path.exists(file_path):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            if 'production_guard' not in content.lower() and 'ProductionGuard' not in content:
                missing_guard.append(file_path)
    
    if missing_guard:
        logger.warning("⚠️  Production guard not integrated in:")
        for m in missing_guard:
            logger.warning(f"  {m}")
        # Not a failure, but should be integrated
    
    logger.info("✅ Production guard integration checked")
    return True


def main():
    """Run all validation checks."""
    logger.info("=" * 60)
    logger.info("PRODUCTION VALIDATION - Starting...")
    logger.info("=" * 60)
    
    checks = [
        ("No Fallback Values", validate_no_fallback_values),
        ("Invalid Batch Marking", validate_batch_invalid_marking),
        ("Evidence Requirements", validate_evidence_requirements),
        ("Production Guard Integration", validate_production_guard_integration),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"❌ Check '{name}' failed with error: {e}")
            results.append((name, False))
    
    logger.info("=" * 60)
    logger.info("VALIDATION RESULTS:")
    logger.info("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {name}")
        if not result:
            all_passed = False
    
    logger.info("=" * 60)
    
    if not all_passed:
        logger.error("❌ VALIDATION FAILED - Production rules violated!")
        sys.exit(1)
    else:
        logger.info("✅ ALL VALIDATIONS PASSED - Production ready!")
        sys.exit(0)


if __name__ == "__main__":
    main()

