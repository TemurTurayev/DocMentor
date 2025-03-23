"""
Virtual patient module initialization.
"""

from .patient_model import VirtualPatient, VitalSign, Symptom, MedicalHistory, PhysicalExam, LabResult, ImagingStudy
from .case_generator import CaseGenerator

__all__ = [
    'VirtualPatient',
    'VitalSign',
    'Symptom',
    'MedicalHistory',
    'PhysicalExam',
    'LabResult',
    'ImagingStudy',
    'CaseGenerator'
]