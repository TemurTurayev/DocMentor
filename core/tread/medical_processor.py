import spacy
from typing import List, Dict, Set
import re
from dataclasses import dataclass

@dataclass
class OptimizedContent:
    text: str
    important_terms: Set[str]
    measurements: List[Dict]
    confidence: float

class MedicalTermProcessor:
    def __init__(self):
        self.nlp = spacy.load('en_core_sci_md')  # Medical-specific model
        self.measurement_patterns = {
            'pressure': r'\d+/\d+\s*(?:mmHg|mm Hg)',
            'dosage': r'\d+(?:\.\d+)?\s*(?:mg|g|mcg|µg|ml)',
            'lab_values': r'\d+(?:\.\d+)?\s*(?:mg/dL|mmol/L|mEq/L)'
        }

    def extract_medical_terms(self, text: str) -> Set[str]:
        doc = self.nlp(text)
        medical_terms = set()
        
        for ent in doc.ents:
            if ent.label_ in {'DISEASE', 'CHEMICAL', 'PROCEDURE'}:
                medical_terms.add(ent.text.lower())
                
        return medical_terms

    def extract_measurements(self, text: str) -> List[Dict]:
        measurements = []
        for category, pattern in self.measurement_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                value, unit = self._split_measurement(match.group())
                measurements.append({
                    'category': category,
                    'value': value,
                    'unit': unit,
                    'original': match.group()
                })
        return measurements

    def optimize_medical_content(self, text: str) -> OptimizedContent:
        medical_terms = self.extract_medical_terms(text)
        measurements = self.extract_measurements(text)
        
        # Calculate confidence based on medical term density
        word_count = len(text.split())
        medical_term_count = len(medical_terms)
        confidence = medical_term_count / word_count if word_count > 0 else 0
        
        return OptimizedContent(
            text=text,
            important_terms=medical_terms,
            measurements=measurements,
            confidence=confidence
        )

    def _split_measurement(self, measurement: str) -> tuple[str, str]:
        match = re.match(r'([\d./]+)\s*(\w+/?\w*)', measurement)
        if match:
            return match.group(1), match.group(2)
        return measurement, ''
