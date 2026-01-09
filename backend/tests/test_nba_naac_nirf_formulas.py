"""
Comprehensive tests for NBA, NAAC, and NIRF official formulas
"""

import pytest
from services.nba_formulas import NBAFormulas
from services.naac_formulas import NAACFormulas
from services.nirf_formulas import NIRFFormulas


class TestNBAFormulas:
    """Tests for NBA (National Board of Accreditation) formulas"""
    
    @pytest.fixture
    def nba_formulas(self):
        return NBAFormulas()
    
    def test_peos_psos_both_present(self, nba_formulas):
        """Test PEOs & PSOs when both are present"""
        data = {
            "peos": ["PEO1", "PEO2", "PEO3"],
            "psos": ["PSO1", "PSO2", "PSO3"]
        }
        score, info = nba_formulas.calculate_peos_psos(data, {})
        assert score == 100.0
        assert "peos" in info["components"]
        assert "psos" in info["components"]
    
    def test_peos_psos_missing(self, nba_formulas):
        """Test PEOs & PSOs when both are missing"""
        data = {}
        score, info = nba_formulas.calculate_peos_psos(data, {})
        assert score is None
        assert "error" in info
    
    def test_faculty_quality_complete(self, nba_formulas):
        """Test Faculty Quality with all components"""
        data = {
            "faculty_count": 20,
            "student_count": 300,  # FSR = 15
            "phd_faculty": 12,  # 60% PhD
            "faculty_development_activities": 10
        }
        score, info = nba_formulas.calculate_faculty_quality(data, {})
        assert score is not None
        assert score > 0
        assert "fsr" in info["components"]
        assert "phd_percentage" in info["components"]
        assert "faculty_development" in info["components"]
    
    def test_student_performance_complete(self, nba_formulas):
        """Test Student Performance with all components"""
        data = {
            "placement_rate": 85.0,
            "pass_percentage": 90.0,
            "higher_studies_count": 30,
            "total_students": 100
        }
        score, info = nba_formulas.calculate_student_performance(data, {})
        assert score is not None
        assert score > 0
        assert "placement_rate" in info["components"]
        assert "pass_percentage" in info["components"]
        assert "higher_studies" in info["components"]
    
    def test_continuous_improvement_both_present(self, nba_formulas):
        """Test Continuous Improvement with both components"""
        data = {
            "action_plan": {"plan": "Improve quality"},
            "feedback_implementation": {"actions": "Implemented"}
        }
        score, info = nba_formulas.calculate_continuous_improvement(data, {})
        assert score == 100.0
        assert "action_plan" in info["components"]
        assert "feedback_implementation" in info["components"]
    
    def test_co_po_mapping_present(self, nba_formulas):
        """Test CO-PO Mapping when present"""
        data = {
            "co_po_mapping": {
                "CO1": ["PO1", "PO2"],
                "CO2": ["PO2", "PO3"]
            }
        }
        score, info = nba_formulas.calculate_co_po_mapping(data, {})
        assert score == 100.0
    
    def test_co_po_mapping_missing(self, nba_formulas):
        """Test CO-PO Mapping when missing (critical)"""
        data = {}
        score, info = nba_formulas.calculate_co_po_mapping(data, {})
        assert score is None
        assert "error" in info
        assert "missing" in info["error"].lower()


class TestNAACFormulas:
    """Tests for NAAC (National Assessment and Accreditation Council) formulas"""
    
    @pytest.fixture
    def naac_formulas(self):
        return NAACFormulas()
    
    def test_criterion_1_complete(self, naac_formulas):
        """Test Criterion 1: Curricular Aspects"""
        data = {
            "curriculum_design": {"design": "Well-structured"},
            "curriculum_implementation": {"status": "Implemented"},
            "academic_flexibility": {"flexibility": "High"}
        }
        score, info = naac_formulas.calculate_criterion_1(data, {})
        assert score is not None
        assert score > 0
        assert "curriculum_design" in info["components"]
    
    def test_criterion_2_complete(self, naac_formulas):
        """Test Criterion 2: Teaching-Learning & Evaluation"""
        data = {
            "student_enrolment": 2000,
            "teaching_learning_process": {"process": "Effective"},
            "evaluation_process": {"methods": "Comprehensive"}
        }
        score, info = naac_formulas.calculate_criterion_2(data, {})
        assert score is not None
        assert score > 0
    
    def test_criterion_3_complete(self, naac_formulas):
        """Test Criterion 3: Research, Innovations & Extension"""
        data = {
            "research_publications": 50,
            "research_projects": 10,
            "extension_activities": 5
        }
        score, info = naac_formulas.calculate_criterion_3(data, {})
        assert score is not None
        assert score > 0
        assert "publications" in info["components"]
        assert "research_projects" in info["components"]
        assert "extension_activities" in info["components"]
    
    def test_criterion_4_complete(self, naac_formulas):
        """Test Criterion 4: Infrastructure & Learning Resources"""
        data = {
            "built_up_area": 10000,
            "library_books": 50000,
            "it_infrastructure": {"labs": "Well-equipped"}
        }
        score, info = naac_formulas.calculate_criterion_4(data, {})
        assert score is not None
        assert score > 0
    
    def test_criterion_5_complete(self, naac_formulas):
        """Test Criterion 5: Student Support & Progression"""
        data = {
            "student_support_services": {"services": "Comprehensive"},
            "student_progression_rate": 85.0,
            "student_participation": 80,
            "total_students": 100
        }
        score, info = naac_formulas.calculate_criterion_5(data, {})
        assert score is not None
        assert score > 0
    
    def test_criterion_6_complete(self, naac_formulas):
        """Test Criterion 6: Governance, Leadership & Management"""
        data = {
            "governance_structure": {"structure": "Well-defined"},
            "leadership": {"team": "Strong"},
            "management_practices": {"practices": "Effective"}
        }
        score, info = naac_formulas.calculate_criterion_6(data, {})
        assert score is not None
        assert score > 0
    
    def test_criterion_7_complete(self, naac_formulas):
        """Test Criterion 7: Institutional Values & Best Practices"""
        data = {
            "institutional_values": {"values": "Core values defined"},
            "best_practices": {"practices": "Innovative practices"}
        }
        score, info = naac_formulas.calculate_criterion_7(data, {})
        assert score is not None
        assert score > 0
    
    def test_criterion_missing_data(self, naac_formulas):
        """Test criterion with missing data"""
        data = {}
        score, info = naac_formulas.calculate_criterion_1(data, {})
        assert score is None
        assert "error" in info


class TestNIRFFormulas:
    """Tests for NIRF (National Institutional Ranking Framework) formulas"""
    
    @pytest.fixture
    def nirf_formulas(self):
        return NIRFFormulas()
    
    def test_tlr_complete(self, nirf_formulas):
        """Test TLR: Teaching, Learning & Resources"""
        data = {
            "total_students": 2000,
            "faculty_count": 100,  # FSR = 20
            "financial_resources": 10,  # 10 crores
            "library_books": 50000
        }
        score, info = nirf_formulas.calculate_tlr(data, {})
        assert score is not None
        assert score > 0
        assert "student_strength" in info["components"]
        assert "fsr" in info["components"]
        assert "financial_resources" in info["components"]
        assert "library_resources" in info["components"]
    
    def test_rp_complete(self, nirf_formulas):
        """Test RP: Research & Professional Practice"""
        data = {
            "research_publications": 100,
            "citations": 500,
            "patents": 10
        }
        score, info = nirf_formulas.calculate_rp(data, {})
        assert score is not None
        assert score > 0
        assert "publications" in info["components"]
        assert "citations" in info["components"]
        assert "patents" in info["components"]
    
    def test_go_complete(self, nirf_formulas):
        """Test GO: Graduation Outcomes"""
        data = {
            "placement_rate": 85.0,
            "higher_studies_count": 30,
            "total_students": 100,
            "graduation_rate": 90.0
        }
        score, info = nirf_formulas.calculate_go(data, {})
        assert score is not None
        assert score > 0
        assert "placement_rate" in info["components"]
        assert "higher_studies" in info["components"]
        assert "graduation_rate" in info["components"]
    
    def test_oi_complete(self, nirf_formulas):
        """Test OI: Outreach & Inclusivity"""
        data = {
            "women_students": 40,
            "total_students": 100,  # 40% women
            "economically_disadvantaged_students": 20,  # 20% disadvantaged
            "outreach_activities": 10
        }
        score, info = nirf_formulas.calculate_oi(data, {})
        assert score is not None
        assert score > 0
        assert "women_students" in info["components"]
        assert "economically_disadvantaged" in info["components"]
        assert "outreach_activities" in info["components"]
    
    def test_pr_complete(self, nirf_formulas):
        """Test PR: Perception"""
        data = {
            "peer_perception": 85.0,
            "employer_perception": 80.0,
            "public_perception": 75.0
        }
        score, info = nirf_formulas.calculate_pr(data, {})
        assert score is not None
        assert score > 0
        assert "peer_perception" in info["components"]
        assert "employer_perception" in info["components"]
        assert "public_perception" in info["components"]
    
    def test_parameter_missing_data(self, nirf_formulas):
        """Test parameter with missing data"""
        data = {}
        score, info = nirf_formulas.calculate_tlr(data, {})
        assert score is None
        assert "error" in info


class TestOverallScores:
    """Tests for overall score calculations"""
    
    def test_nba_overall(self):
        """Test NBA overall score calculation"""
        from services.kpi_official import OfficialKPIService
        
        service = OfficialKPIService()
        criterion_scores = {
            "peos_psos": 100.0,
            "faculty_quality": 80.0,
            "student_performance": 85.0,
            "continuous_improvement": 90.0,
            "co_po_mapping": 100.0
        }
        
        overall_score, info = service.calculate_nba_overall(criterion_scores)
        assert overall_score is not None
        assert overall_score > 0
        # Should be average of all scores
        expected = sum(criterion_scores.values()) / len(criterion_scores)
        assert abs(overall_score - expected) < 0.01
    
    def test_naac_overall(self):
        """Test NAAC overall score calculation"""
        from services.kpi_official import OfficialKPIService
        
        service = OfficialKPIService()
        criterion_scores = {
            "criterion_1": 80.0,
            "criterion_2": 85.0,
            "criterion_3": 75.0,
            "criterion_4": 90.0,
            "criterion_5": 80.0,
            "criterion_6": 85.0,
            "criterion_7": 90.0
        }
        
        criterion_weights = {
            "criterion_1": 0.15,
            "criterion_2": 0.15,
            "criterion_3": 0.15,
            "criterion_4": 0.15,
            "criterion_5": 0.15,
            "criterion_6": 0.15,
            "criterion_7": 0.10
        }
        
        overall_score, info = service.calculate_naac_overall(criterion_scores, criterion_weights)
        assert overall_score is not None
        assert overall_score > 0
    
    def test_nirf_overall(self):
        """Test NIRF overall score calculation"""
        from services.kpi_official import OfficialKPIService
        
        service = OfficialKPIService()
        parameter_scores = {
            "tlr": 80.0,
            "rp": 75.0,
            "go": 85.0,
            "oi": 70.0,
            "pr": 80.0
        }
        
        parameter_weights = {
            "tlr": 0.30,
            "rp": 0.30,
            "go": 0.20,
            "oi": 0.10,
            "pr": 0.10
        }
        
        overall_score, info = service.calculate_nirf_overall(parameter_scores, parameter_weights)
        assert overall_score is not None
        assert overall_score > 0

