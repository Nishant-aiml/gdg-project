"""
Official KPI Formula Tests
Tests for AICTE, NBA, NAAC, NIRF modes
Ensures formulas are deterministic and match official rules
"""

import unittest
from services.kpi_official import OfficialKPIService
from services.evidence_tracker import EvidenceTracker


class TestAICTEFormulas(unittest.TestCase):
    """Test AICTE mode formulas"""
    
    def setUp(self):
        self.service = OfficialKPIService()
        self.evidence_map = {}
    
    def test_fsr_formula_correct(self):
        """Test FSR = Students/Faculty (NOT Faculty/Students)"""
        data = {
            "faculty_count_num": 100,
            "student_count_num": 1500
        }
        
        score, info = self.service.calculate_aicte_fsr(data, self.evidence_map)
        
        # FSR = 1500/100 = 15
        # FSR ≤ 15 → Score = 100
        self.assertEqual(score, 100.0)
        self.assertEqual(info["fsr_value"], 15.0)
    
    def test_fsr_scoring_rule_15(self):
        """Test FSR ≤ 15 → Score = 100"""
        data = {
            "faculty_count_num": 100,
            "student_count_num": 1500  # FSR = 15
        }
        score, _ = self.service.calculate_aicte_fsr(data, self.evidence_map)
        self.assertEqual(score, 100.0)
    
    def test_fsr_scoring_rule_20(self):
        """Test FSR = 20 → Score = 60"""
        data = {
            "faculty_count_num": 100,
            "student_count_num": 2000  # FSR = 20
        }
        score, _ = self.service.calculate_aicte_fsr(data, self.evidence_map)
        self.assertEqual(score, 60.0)
    
    def test_fsr_scoring_rule_linear(self):
        """Test 15 < FSR ≤ 20 → Linear scale"""
        data = {
            "faculty_count_num": 100,
            "student_count_num": 1750  # FSR = 17.5
        }
        score, _ = self.service.calculate_aicte_fsr(data, self.evidence_map)
        # Expected: 100 + (17.5 - 15) * (-8) = 100 - 20 = 80
        self.assertEqual(score, 80.0)
    
    def test_fsr_scoring_rule_penalty(self):
        """Test FSR > 20 → Proportional penalty"""
        data = {
            "faculty_count_num": 100,
            "student_count_num": 2500  # FSR = 25
        }
        score, _ = self.service.calculate_aicte_fsr(data, self.evidence_map)
        # Expected: 60 - (25 - 20) * 3 = 60 - 15 = 45
        self.assertEqual(score, 45.0)
    
    def test_fsr_missing_data(self):
        """Test FSR returns None when data missing"""
        data = {
            "faculty_count_num": 100
            # student_count missing
        }
        score, info = self.service.calculate_aicte_fsr(data, self.evidence_map)
        self.assertIsNone(score)
        self.assertIn("missing_inputs", info)
    
    def test_infrastructure_weighted_formula(self):
        """Test Infrastructure weighted formula"""
        data = {
            "total_students_num": 1000,
            "built_up_area_sqm_num": 5000,  # 5 sqm per student (above 4 sqm norm)
            "total_classrooms_num": 30,  # 33.3 students per classroom (above 40 norm)
            "library_area_sqm_num": 600,  # 0.6 sqm per student (above 0.5 norm)
            "digital_library_resources_num": 600,  # Above 500 target
            "hostel_capacity_num": 500  # 50% of students (above 40% norm)
        }
        
        score, info = self.service.calculate_aicte_infrastructure(data, self.evidence_map)
        
        # Area: min(100, (5000/4000)*100) = 100 → 0.40 * 1.0 = 0.40
        # Classrooms: min(100, (30/25)*100) = 100 → 0.25 * 1.0 = 0.25
        # Library: min(100, (600/500)*100) = 100 → 0.15 * 1.0 = 0.15
        # Digital: min(100, (600/500)*100) = 100 → 0.10 * 1.0 = 0.10
        # Hostel: min(100, (500/400)*100) = 100 → 0.10 * 1.0 = 0.10
        # Total: 100 * (0.40 + 0.25 + 0.15 + 0.10 + 0.10) = 100
        self.assertAlmostEqual(score, 100.0, places=1)
    
    def test_placement_formula(self):
        """Test Placement Index formula"""
        data = {
            "students_placed_num": 400,
            "students_eligible_num": 500
        }
        
        score, info = self.service.calculate_aicte_placement(data, self.evidence_map)
        
        # Placement % = (400/500) * 100 = 80%
        self.assertEqual(score, 80.0)
        self.assertEqual(info["placement_rate"], 80.0)
    
    def test_placement_capped_at_100(self):
        """Test Placement Index capped at 100"""
        data = {
            "students_placed_num": 600,
            "students_eligible_num": 500  # More placed than eligible (data error, but cap at 100)
        }
        
        score, _ = self.service.calculate_aicte_placement(data, self.evidence_map)
        self.assertEqual(score, 100.0)  # Capped
    
    def test_lab_compliance_formula(self):
        """Test Lab Compliance formula"""
        data = {
            "total_labs_num": 10,
            "total_students_num": 500
        }
        
        score, info = self.service.calculate_aicte_lab_compliance(data, self.evidence_map)
        
        # Required labs = max(5, 500/50) = 10
        # Compliance = (10/10) * 100 = 100
        self.assertEqual(score, 100.0)
    
    def test_aicte_overall_average(self):
        """Test AICTE Overall = Average of available KPIs"""
        kpi_scores = {
            "fsr_score": 100.0,
            "infrastructure_score": 80.0,
            "placement_index": 90.0,
            "lab_compliance_index": 70.0
        }
        
        score, info = self.service.calculate_aicte_overall(kpi_scores)
        
        # Average = (100 + 80 + 90 + 70) / 4 = 85
        self.assertEqual(score, 85.0)
        self.assertEqual(len(info["included"]), 4)
    
    def test_aicte_overall_missing_kpis(self):
        """Test AICTE Overall excludes missing KPIs"""
        kpi_scores = {
            "fsr_score": None,  # Missing
            "infrastructure_score": 80.0,
            "placement_index": 90.0,
            "lab_compliance_index": None  # Missing
        }
        
        score, info = self.service.calculate_aicte_overall(kpi_scores)
        
        # Average = (80 + 90) / 2 = 85
        self.assertEqual(score, 85.0)
        self.assertEqual(len(info["included"]), 2)
        self.assertEqual(len(info["excluded"]), 2)
    
    def test_aicte_overall_all_missing(self):
        """Test AICTE Overall returns None if all KPIs missing"""
        kpi_scores = {
            "fsr_score": None,
            "infrastructure_score": None,
            "placement_index": None,
            "lab_compliance_index": None
        }
        
        score, info = self.service.calculate_aicte_overall(kpi_scores)
        self.assertIsNone(score)
        self.assertIn("error", info)


class TestValidationRules(unittest.TestCase):
    """Test validation rules"""
    
    def setUp(self):
        self.service = OfficialKPIService()
    
    def test_year_validation_renewal(self):
        """Test year validation for renewal"""
        from datetime import datetime
        current_year = datetime.now().year
        
        # Valid renewal year (current_year - 1)
        is_valid, error = self.service.validate_year(f"{current_year - 1}-{current_year}", is_new=False)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Invalid renewal year (current_year - 3)
        is_valid, error = self.service.validate_year(f"{current_year - 3}-{current_year - 2}", is_new=False)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_year_validation_new(self):
        """Test year validation for new institution"""
        from datetime import datetime
        current_year = datetime.now().year
        
        # Valid new year (current_year)
        is_valid, error = self.service.validate_year(f"{current_year}-{current_year + 1}", is_new=True)
        self.assertTrue(is_valid)
        
        # Invalid new year (current_year - 1)
        is_valid, error = self.service.validate_year(f"{current_year - 1}-{current_year}", is_new=True)
        self.assertFalse(is_valid)
    
    def test_numeric_sanity_students_faculty(self):
        """Test numeric sanity: Students ≥ Faculty"""
        data = {
            "faculty_count_num": 100,
            "student_count_num": 50  # Invalid: students < faculty
        }
        
        is_valid, errors = self.service.validate_numeric_sanity(data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_numeric_sanity_placement(self):
        """Test numeric sanity: Placement ≤ Eligible"""
        data = {
            "students_placed_num": 600,
            "students_eligible_num": 500  # Invalid: placed > eligible
        }
        
        is_valid, errors = self.service.validate_numeric_sanity(data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_numeric_sanity_area(self):
        """Test numeric sanity: Areas > 0"""
        data = {
            "built_up_area_num": 0  # Invalid: area = 0
        }
        
        is_valid, errors = self.service.validate_numeric_sanity(data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestEvidenceTracking(unittest.TestCase):
    """Test evidence tracking"""
    
    def test_evidence_map_building(self):
        """Test evidence map building from blocks"""
        from config.database import Block
        
        blocks = [
            Block(
                id="block1",
                batch_id="batch1",
                block_type="faculty_information",
                data={"faculty_count": 100},
                evidence_snippet="Total Faculty: 100",
                evidence_page=5,
                source_doc="report.pdf",
                extraction_confidence=0.95
            )
        ]
        
        evidence_map = EvidenceTracker.build_evidence_map(blocks)
        
        self.assertIn("faculty_count", evidence_map)
        self.assertEqual(evidence_map["faculty_count"]["page"], 5)
        self.assertEqual(evidence_map["faculty_count"]["source_doc"], "report.pdf")
        self.assertEqual(evidence_map["faculty_count"]["snippet"], "Total Faculty: 100")
    
    def test_evidence_validation(self):
        """Test evidence validation"""
        # Valid evidence
        evidence = {
            "snippet": "Total Faculty: 100",
            "page": 5,
            "source_doc": "report.pdf"
        }
        is_valid, error = EvidenceTracker.validate_evidence(100, evidence)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Missing evidence
        is_valid, error = EvidenceTracker.validate_evidence(100, {})
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
        
        # None value doesn't need evidence
        is_valid, error = EvidenceTracker.validate_evidence(None, {})
        self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main()

