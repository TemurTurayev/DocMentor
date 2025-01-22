import pytest
from core.tread.medical_processor import MedicalTermProcessor
from core.tread.optimization import TREADOptimizer

@pytest.fixture
def medical_processor():
    return MedicalTermProcessor()

@pytest.fixture
def sample_medical_text():
    return """
    Patient presents with acute myocardial infarction.
    BP: 140/90 mmHg
    Prescribed aspirin 81mg daily.
    Laboratory values show elevated troponin levels.
    """

def test_medical_term_detection(medical_processor, sample_medical_text):
    terms = medical_processor.extract_medical_terms(sample_medical_text)
    assert 'myocardial infarction' in terms
    assert 'troponin' in terms

def test_measurement_parsing(medical_processor, sample_medical_text):
    measurements = medical_processor.extract_measurements(sample_medical_text)
    assert any(m['value'] == '140/90' and m['unit'] == 'mmHg' for m in measurements)
    assert any(m['value'] == '81' and m['unit'] == 'mg' for m in measurements)

def test_tread_optimization_with_medical_terms(medical_processor):
    text = "Patient diagnosed with pneumonia. Prescribed antibiotics."
    optimized = medical_processor.optimize_medical_content(text)
    assert 'pneumonia' in optimized.important_terms
    assert 'antibiotics' in optimized.important_terms
"""