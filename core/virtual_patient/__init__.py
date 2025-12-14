"""
Virtual Patient Module - AI-powered patient simulations.
Interactive clinical scenarios for medical education.
"""

from .ai_patient import AIPatient
from .scenario_manager import ScenarioManager
from .patient_loader import PatientLoader

__all__ = ["AIPatient", "ScenarioManager", "PatientLoader"]
