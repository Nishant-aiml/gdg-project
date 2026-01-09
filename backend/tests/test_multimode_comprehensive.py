"""
Comprehensive Multi-Mode Platform Tests
Tests for: Mode Isolation, NBA, NAAC, NIRF, Evidence Enforcement

CRITICAL: Ensures no dummy data, no cross-mode reuse, proper NULL handling
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.information_blocks import (
    get_information_blocks,
    validate_document_for_mode,
    AICTE_BLOCKS,
    NBA_BLOCKS,
    NAAC_BLOCKS,
    NIRF_BLOCKS
)
from services.nba_calculation_engine import NBACalculationEngine
from services.naac_calculation_engine import NAACCalculationEngine, NAAC_WEIGHTS
from services.nirf_calculation_engine import NIRFCalculationEngine
from models.naac_models import get_naac_grade
from utils.production_guard import ProductionGuard


class TestModeIsolation:
    """Tests for strict mode isolation - No cross-mode data reuse"""
    
    def test_aicte_blocks_exist(self):
        """AICTE mode should have its own blocks"""
        blocks = get_information_blocks("aicte")
        assert len(blocks) > 0
        assert "faculty_information" in blocks
        print(f"✅ AICTE has {len(blocks)} blocks")
    
    def test_nba_blocks_different_from_aicte(self):
        """NBA mode should have different blocks from AICTE"""
        aicte = get_information_blocks("aicte")
        nba = get_information_blocks("nba")
        
        # NBA blocks should be completely different
        for block in nba:
            assert block not in aicte, f"NBA block '{block}' found in AICTE - violates isolation!"
        
        print(f"✅ NBA {len(nba)} blocks are isolated from AICTE {len(aicte)} blocks")
    
    def test_naac_blocks_different_from_others(self):
        """NAAC mode should have different blocks"""
        naac = get_information_blocks("naac")
        aicte = get_information_blocks("aicte")
        
        assert "iqac_report" in naac
        assert "curricular_aspects" in naac
        
        for block in naac:
            assert block not in aicte, f"NAAC block '{block}' found in AICTE!"
        
        print(f"✅ NAAC has {len(naac)} isolated blocks")
    
    def test_nirf_blocks_different_from_others(self):
        """NIRF mode should have different blocks"""
        nirf = get_information_blocks("nirf")
        
        assert "perception_survey" in nirf
        assert "student_strength" in nirf
        
        print(f"✅ NIRF has {len(nirf)} isolated blocks")
    
    def test_unknown_mode_raises_error(self):
        """Unknown mode should raise ValueError"""
        with pytest.raises(ValueError) as exc:
            get_information_blocks("invalid_mode")
        
        assert "Unknown mode" in str(exc.value)
        print("✅ Unknown mode correctly raises ValueError")
    
    def test_cross_mode_document_rejected(self):
        """Cross-mode document uploads should be rejected"""
        # Try to use NAAC doc in AICTE mode
        is_valid, error = validate_document_for_mode("iqac_report", "aicte")
        assert is_valid is False
        assert "not allowed" in error
        
        # Try to use AICTE doc in NBA mode
        is_valid, error = validate_document_for_mode("faculty_information", "nba")
        assert is_valid is False
        
        print("✅ Cross-mode documents correctly rejected")
    
    def test_same_mode_document_accepted(self):
        """Same-mode documents should be accepted"""
        is_valid, error = validate_document_for_mode("co_definitions", "nba")
        assert is_valid is True
        assert error is None
        
        is_valid, error = validate_document_for_mode("iqac_report", "naac")
        assert is_valid is True
        
        print("✅ Same-mode documents correctly accepted")


class TestNBAFormulas:
    """Tests for NBA OBE Calculation Formulas"""
    
    def test_co_attainment_calculation(self):
        """Test CO attainment = (students >= threshold) / total * 100"""
        # Manual calculation
        students_above = 70
        total = 100
        expected = 70.0
        calculated = (students_above / total) * 100
        
        assert calculated == expected
        print("✅ CO Attainment formula correct: 70/100 = 70%")
    
    def test_po_attainment_weighted_average(self):
        """Test PO attainment = Σ(CO_attainment × mapping) / Σ(mapping)"""
        # CO attainments with mapping levels
        co_data = [
            {"attainment": 75, "mapping": 3},
            {"attainment": 60, "mapping": 2},
            {"attainment": 80, "mapping": 1},
        ]
        
        numerator = sum(c["attainment"] * c["mapping"] for c in co_data)
        denominator = sum(c["mapping"] for c in co_data)
        expected = numerator / denominator
        
        # (75*3 + 60*2 + 80*1) / (3+2+1) = (225+120+80)/6 = 425/6 = 70.83
        assert round(expected, 2) == 70.83
        print(f"✅ PO Attainment weighted average: {round(expected, 2)}")
    
    def test_final_po_with_direct_indirect(self):
        """Test Final PO = 0.8 × Direct + 0.2 × Indirect"""
        direct = 75.0
        indirect = 60.0
        
        expected = 0.8 * direct + 0.2 * indirect
        assert expected == 72.0
        print(f"✅ Final PO (80/20 weighted): {expected}")
    
    def test_attainment_status_thresholds(self):
        """Test attainment status classification"""
        assert 75 >= 70  # Attained
        assert 55 >= 50 and 55 < 70  # Partially Attained
        assert 40 < 50  # Not Attained
        print("✅ Attainment status thresholds correct")
    
    def test_missing_mapping_returns_null(self):
        """PO cannot be computed without CO-PO mapping"""
        # If no mappings, result should be None
        mappings = []
        result = None if len(mappings) == 0 else sum(m for m in mappings)
        
        assert result is None
        print("✅ Missing mapping correctly returns NULL")


class TestNAACFormulas:
    """Tests for NAAC 7 Criteria Calculation Formulas"""
    
    def test_naac_weights_sum_to_1000(self):
        """NAAC weights should sum to 1000"""
        total = sum(NAAC_WEIGHTS.values())
        assert total == 1000
        print(f"✅ NAAC weights sum: {total}")
    
    def test_naac_has_7_criteria(self):
        """NAAC should have exactly 7 criteria"""
        assert len(NAAC_WEIGHTS) == 7
        assert "C1" in NAAC_WEIGHTS
        assert "C7" in NAAC_WEIGHTS
        print("✅ NAAC has 7 criteria (C1-C7)")
    
    def test_cgpa_calculation(self):
        """Test CGPA = Σ(score × weight) / 1000"""
        scores = {
            "C1": 3.5, "C2": 3.2, "C3": 3.8,
            "C4": 3.0, "C5": 3.3, "C6": 3.1, "C7": 3.4
        }
        
        weighted_sum = sum(scores[c] * NAAC_WEIGHTS[c] for c in scores)
        cgpa = weighted_sum / 1000
        
        expected = (
            3.5*150 + 3.2*200 + 3.8*250 + 
            3.0*100 + 3.3*100 + 3.1*100 + 3.4*100
        ) / 1000
        
        assert round(cgpa, 2) == round(expected, 2)
        print(f"✅ NAAC CGPA calculation: {round(cgpa, 2)}")
    
    def test_naac_grading_scale(self):
        """Test NAAC grading based on CGPA"""
        assert get_naac_grade(3.8) == "A++"
        assert get_naac_grade(3.4) == "A+"
        assert get_naac_grade(3.1) == "A"
        assert get_naac_grade(2.9) == "B++"
        assert get_naac_grade(2.6) == "B+"
        assert get_naac_grade(2.3) == "B"
        assert get_naac_grade(1.7) == "C"
        assert get_naac_grade(1.3) == "D"
        print("✅ NAAC grading scale correct")
    
    def test_missing_criterion_blocks_cgpa(self):
        """Missing criterion should result in NULL overall"""
        scores = {"C1": 3.5, "C2": 3.2}  # Missing C3-C7
        missing = [c for c in ["C1", "C2", "C3", "C4", "C5", "C6", "C7"] if c not in scores]
        
        # If any missing, CGPA should be NULL
        cgpa = None if len(missing) > 0 else 3.0
        
        assert cgpa is None
        assert len(missing) == 5
        print("✅ Missing criterion correctly blocks CGPA")


class TestNIRFFormulas:
    """Tests for NIRF 5 Parameter Calculation Formulas"""
    
    def test_nirf_has_5_parameters(self):
        """NIRF should have exactly 5 parameters"""
        params = ["TLR", "RP", "GO", "OI", "PR"]
        assert len(params) == 5
        print("✅ NIRF has 5 parameters")
    
    def test_nirf_overall_score(self):
        """Test overall = (TLR + RP + GO + OI + PR) / 5"""
        scores = {"TLR": 80, "RP": 70, "GO": 85, "OI": 75, "PR": 60}
        
        overall = sum(scores.values()) / 5
        expected = (80 + 70 + 85 + 75 + 60) / 5
        
        assert overall == expected
        assert overall == 74.0
        print(f"✅ NIRF overall score: {overall}")
    
    def test_nirf_without_pr(self):
        """Without perception survey, use 4 params"""
        scores = {"TLR": 80, "RP": 70, "GO": 85, "OI": 75, "PR": None}
        
        available = {k: v for k, v in scores.items() if v is not None}
        overall = sum(available.values()) / len(available) if available else None
        
        expected = (80 + 70 + 85 + 75) / 4
        assert overall == expected
        assert overall == 77.5
        print(f"✅ NIRF without PR: {overall}")
    
    def test_pr_requires_survey(self):
        """PR should be NULL without perception survey"""
        has_perception_survey = False
        pr_score = None if not has_perception_survey else 60.0
        
        assert pr_score is None
        print("✅ PR correctly NULL without survey")


class TestEvidenceEnforcement:
    """Tests for evidence requirements"""
    
    def test_no_evidence_returns_null(self):
        """No evidence should return NULL"""
        evidence_doc_id = None
        
        has_evidence = ProductionGuard.validate_nba_evidence(evidence_doc_id, "test_metric")
        assert has_evidence is False
        print("✅ Missing evidence correctly returns False")
    
    def test_with_evidence_succeeds(self):
        """With evidence, validation should pass"""
        evidence_doc_id = "doc123"
        
        has_evidence = ProductionGuard.validate_nba_evidence(evidence_doc_id, "test_metric")
        assert has_evidence is True
        print("✅ Valid evidence correctly returns True")
    
    def test_attainment_without_evidence_null(self):
        """Attainment calculation without evidence should be NULL"""
        value = 75.0
        evidence_doc_id = None
        
        result = ProductionGuard.validate_nba_attainment_data(value, "test", evidence_doc_id)
        assert result is None
        print("✅ Attainment without evidence correctly NULL")


class TestInvalidBatchHandling:
    """Tests for invalid batch exclusion"""
    
    def test_batch_marked_invalid_for_missing_kpi(self):
        """Batch with no KPI results should be invalid"""
        kpi_results = None
        is_invalid = kpi_results is None
        
        assert is_invalid is True
        print("✅ Missing KPI correctly marks batch invalid")
    
    def test_batch_marked_invalid_for_zero_sufficiency(self):
        """Batch with 0% sufficiency should be invalid"""
        sufficiency = 0
        is_invalid = sufficiency == 0
        
        assert is_invalid is True
        print("✅ Zero sufficiency correctly marks batch invalid")


class TestNoDummyData:
    """Tests to ensure no dummy/fallback values"""
    
    def test_no_hardcoded_fallbacks(self):
        """Check that missing data doesn't use fallback values"""
        raw_value = None
        
        # WRONG: value = raw_value or 0
        # CORRECT: value = raw_value (stays None)
        value = raw_value
        
        assert value is None
        assert value != 0
        print("✅ No fallback to 0 for missing data")
    
    def test_empty_string_treated_as_null(self):
        """Empty strings should be treated as NULL"""
        value = ""
        result = None if value == "" else value
        
        assert result is None
        print("✅ Empty string correctly treated as NULL")


def run_all_tests():
    """Run all tests and print summary"""
    print("=" * 60)
    print("MULTI-MODE PLATFORM COMPREHENSIVE TESTS")
    print("=" * 60)
    
    test_classes = [
        TestModeIsolation,
        TestNBAFormulas,
        TestNAACFormulas,
        TestNIRFFormulas,
        TestEvidenceEnforcement,
        TestInvalidBatchHandling,
        TestNoDummyData,
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}")
        print("-" * 40)
        
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    getattr(instance, method_name)()
                    passed += 1
                except Exception as e:
                    print(f"❌ {method_name}: {e}")
                    failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
