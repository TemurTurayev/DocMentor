"""
Virtual patient model for DocMentor.
Defines the structure and behavior of virtual patients for medical simulations.
"""

import json
import random
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class VitalSign:
    """Class representing a vital sign with normal range and current value."""
    
    def __init__(
        self,
        name: str,
        current_value: float,
        unit: str,
        min_normal: float,
        max_normal: float,
        critical_low: Optional[float] = None,
        critical_high: Optional[float] = None,
        trend: str = "stable"
    ):
        """
        Initialize a vital sign.
        
        Args:
            name: Name of the vital sign (e.g., "Pulse")
            current_value: Current value
            unit: Unit of measurement (e.g., "bpm")
            min_normal: Minimum normal value
            max_normal: Maximum normal value
            critical_low: Critical low threshold
            critical_high: Critical high threshold
            trend: Current trend ("increasing", "decreasing", or "stable")
        """
        self.name = name
        self.current_value = current_value
        self.unit = unit
        self.min_normal = min_normal
        self.max_normal = max_normal
        self.critical_low = critical_low if critical_low is not None else min_normal * 0.7
        self.critical_high = critical_high if critical_high is not None else max_normal * 1.3
        self.trend = trend
        self.history = [(time.time(), current_value)]
    
    def update(self, new_value: float, timestamp: Optional[float] = None):
        """
        Update the vital sign value.
        
        Args:
            new_value: New value for the vital sign
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()
            
        # Update current value
        old_value = self.current_value
        self.current_value = new_value
        
        # Update trend
        if new_value > old_value:
            self.trend = "increasing"
        elif new_value < old_value:
            self.trend = "decreasing"
        else:
            self.trend = "stable"
            
        # Add to history
        self.history.append((timestamp, new_value))
        
        # Keep history to a reasonable size
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def is_normal(self) -> bool:
        """Check if the vital sign is within normal range."""
        return self.min_normal <= self.current_value <= self.max_normal
    
    def is_critical(self) -> bool:
        """Check if the vital sign is at critical levels."""
        return self.current_value <= self.critical_low or self.current_value >= self.critical_high
    
    def get_status(self) -> str:
        """Get the status of the vital sign."""
        if self.is_critical():
            if self.current_value <= self.critical_low:
                return "critical_low"
            else:
                return "critical_high"
        elif not self.is_normal():
            if self.current_value < self.min_normal:
                return "below_normal"
            else:
                return "above_normal"
        else:
            return "normal"
    
    def to_dict(self) -> Dict:
        """Convert vital sign to dictionary."""
        return {
            "name": self.name,
            "value": self.current_value,
            "unit": self.unit,
            "status": self.get_status(),
            "trend": self.trend,
            "normal_range": (self.min_normal, self.max_normal),
            "critical_range": (self.critical_low, self.critical_high)
        }


class Symptom:
    """Class representing a symptom with severity and timeline."""
    
    def __init__(
        self,
        name: str,
        description: str,
        severity: int = 1,  # 1-10 scale
        onset_time: Optional[float] = None,
        duration: Optional[float] = None,
        characteristics: Optional[List[str]] = None,
        associated_factors: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a symptom.
        
        Args:
            name: Name of the symptom
            description: Description of how the patient experiences it
            severity: Severity on a 1-10 scale
            onset_time: When the symptom started (timestamp)
            duration: How long the symptom has been present (in hours)
            characteristics: Specific characteristics of the symptom
            associated_factors: Factors that worsen or improve the symptom
        """
        self.name = name
        self.description = description
        self.severity = severity
        self.onset_time = onset_time if onset_time is not None else time.time()
        self.duration = duration
        self.characteristics = characteristics or []
        self.associated_factors = associated_factors or {}
        self.history = [(time.time(), severity)]
    
    def update(self, new_severity: int, timestamp: Optional[float] = None):
        """
        Update symptom severity.
        
        Args:
            new_severity: New severity value (1-10)
            timestamp: Optional timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()
            
        # Ensure severity is in valid range
        new_severity = max(1, min(10, new_severity))
        
        # Update severity
        self.severity = new_severity
        
        # Add to history
        self.history.append((timestamp, new_severity))
        
        # Keep history to a reasonable size
        if len(self.history) > 100:
            self.history = self.history[-100:]
    
    def to_dict(self) -> Dict:
        """Convert symptom to dictionary."""
        current_time = time.time()
        
        return {
            "name": self.name,
            "description": self.description,
            "severity": self.severity,
            "onset": self.onset_time,
            "duration": self.duration if self.duration is not None else (current_time - self.onset_time) / 3600,
            "characteristics": self.characteristics,
            "associated_factors": self.associated_factors
        }

class MedicalHistory:
    """Class representing a patient's medical history."""
    
    def __init__(
        self,
        conditions: Optional[List[Dict]] = None,
        surgeries: Optional[List[Dict]] = None,
        medications: Optional[List[Dict]] = None,
        allergies: Optional[List[Dict]] = None,
        family_history: Optional[Dict] = None,
        social_history: Optional[Dict] = None
    ):
        """
        Initialize medical history.
        
        Args:
            conditions: List of medical conditions
            surgeries: List of surgeries
            medications: List of medications
            allergies: List of allergies
            family_history: Family medical history
            social_history: Social history (smoking, alcohol, etc.)
        """
        self.conditions = conditions or []
        self.surgeries = surgeries or []
        self.medications = medications or []
        self.allergies = allergies or []
        self.family_history = family_history or {}
        self.social_history = social_history or {}
    
    def add_condition(self, condition: Dict):
        """Add a medical condition to history."""
        self.conditions.append(condition)
    
    def add_surgery(self, surgery: Dict):
        """Add a surgery to history."""
        self.surgeries.append(surgery)
    
    def add_medication(self, medication: Dict):
        """Add a medication to history."""
        self.medications.append(medication)
    
    def add_allergy(self, allergy: Dict):
        """Add an allergy to history."""
        self.allergies.append(allergy)
    
    def to_dict(self) -> Dict:
        """Convert medical history to dictionary."""
        return {
            "conditions": self.conditions,
            "surgeries": self.surgeries,
            "medications": self.medications,
            "allergies": self.allergies,
            "family_history": self.family_history,
            "social_history": self.social_history
        }


class PhysicalExam:
    """Class representing a physical examination."""
    
    def __init__(
        self,
        general_appearance: Dict,
        systems: Optional[Dict[str, Dict]] = None
    ):
        """
        Initialize physical exam.
        
        Args:
            general_appearance: Description of general appearance
            systems: Findings by body system
        """
        self.general_appearance = general_appearance
        self.systems = systems or {}
    
    def add_system_finding(self, system: str, description: str, findings: Optional[Dict] = None):
        """
        Add findings for a body system.
        
        Args:
            system: Name of the body system
            description: General description of findings
            findings: Specific findings as key-value pairs
        """
        if system not in self.systems:
            self.systems[system] = {
                "description": description,
                "findings": findings or {}
            }
        else:
            self.systems[system]["description"] = description
            if findings:
                self.systems[system]["findings"].update(findings)
    
    def to_dict(self) -> Dict:
        """Convert physical exam to dictionary."""
        return {
            "general_appearance": self.general_appearance,
            "systems": self.systems
        }


class LabResult:
    """Class representing a laboratory result."""
    
    def __init__(
        self,
        name: str,
        value: Union[float, str],
        unit: str,
        reference_range: Union[Tuple[float, float], str],
        timestamp: float,
        critical: bool = False,
        notes: Optional[str] = None
    ):
        """
        Initialize lab result.
        
        Args:
            name: Name of the test
            value: Result value
            unit: Unit of measurement
            reference_range: Normal range as tuple (min, max) or string
            timestamp: When the test was performed
            critical: Whether the result is critical
            notes: Additional notes
        """
        self.name = name
        self.value = value
        self.unit = unit
        self.reference_range = reference_range
        self.timestamp = timestamp
        self.critical = critical
        self.notes = notes
    
    def is_normal(self) -> bool:
        """Check if the result is within normal range."""
        if isinstance(self.value, (int, float)) and isinstance(self.reference_range, tuple):
            return self.reference_range[0] <= self.value <= self.reference_range[1]
        return False
    
    def to_dict(self) -> Dict:
        """Convert lab result to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "reference_range": self.reference_range,
            "timestamp": self.timestamp,
            "critical": self.critical,
            "notes": self.notes,
            "is_normal": self.is_normal() if isinstance(self.value, (int, float)) and isinstance(self.reference_range, tuple) else None
        }


class ImagingStudy:
    """Class representing an imaging study."""
    
    def __init__(
        self,
        name: str,
        modality: str,
        findings: str,
        impression: str,
        timestamp: float,
        images: Optional[List[str]] = None,
        notes: Optional[str] = None
    ):
        """
        Initialize imaging study.
        
        Args:
            name: Name of the study
            modality: Imaging modality (e.g., X-ray, MRI)
            findings: Description of findings
            impression: Clinical impression
            timestamp: When the study was performed
            images: List of image references
            notes: Additional notes
        """
        self.name = name
        self.modality = modality
        self.findings = findings
        self.impression = impression
        self.timestamp = timestamp
        self.images = images or []
        self.notes = notes
    
    def add_image(self, image_reference: str):
        """Add an image to the study."""
        self.images.append(image_reference)
    
    def to_dict(self) -> Dict:
        """Convert imaging study to dictionary."""
        return {
            "name": self.name,
            "modality": self.modality,
            "findings": self.findings,
            "impression": self.impression,
            "timestamp": self.timestamp,
            "images": self.images,
            "notes": self.notes
        }


class VirtualPatient:
    """Class representing a virtual patient for medical simulations."""
    
    def __init__(
        self,
        patient_id: str,
        name: str,
        age: int,
        gender: str,
        chief_complaint: str,
        history_of_present_illness: str,
        vital_signs: Dict[str, VitalSign],
        symptoms: List[Symptom],
        medical_history: MedicalHistory,
        physical_exam: PhysicalExam,
        lab_results: Dict[str, LabResult],
        imaging_studies: List[ImagingStudy],
        diagnoses: List[Dict],
        scenario_difficulty: int = 1,
        expert_reasoning: Optional[str] = None
    ):
        """
        Initialize a virtual patient.
        
        Args:
            patient_id: Unique identifier
            name: Patient name
            age: Patient age
            gender: Patient gender
            chief_complaint: Primary complaint
            history_of_present_illness: Detailed history
            vital_signs: Dictionary of vital signs
            symptoms: List of symptoms
            medical_history: Medical history
            physical_exam: Physical examination findings
            lab_results: Dictionary of lab results
            imaging_studies: List of imaging studies
            diagnoses: List of diagnoses with probabilities
            scenario_difficulty: Difficulty level (1-5)
            expert_reasoning: Expert explanation of the case
        """
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.chief_complaint = chief_complaint
        self.history_of_present_illness = history_of_present_illness
        self.vital_signs = vital_signs
        self.symptoms = symptoms
        self.medical_history = medical_history
        self.physical_exam = physical_exam
        self.lab_results = lab_results
        self.imaging_studies = imaging_studies
        self.diagnoses = diagnoses
        self.scenario_difficulty = scenario_difficulty
        self.expert_reasoning = expert_reasoning
        
        # Track which information has been revealed to the student
        self.revealed_info = {
            "vital_signs": False,
            "symptoms": False,
            "medical_history": False,
            "physical_exam": False,
            "lab_results": {},
            "imaging_studies": {}
        }
    
    def reveal_info(self, category: str, item_name: Optional[str] = None) -> Dict:
        """
        Reveal information to the student.
        
        Args:
            category: Information category
            item_name: Specific item name (for lab results and imaging)
            
        Returns:
            Revealed information
        """
        if category in ["vital_signs", "symptoms", "medical_history", "physical_exam"]:
            self.revealed_info[category] = True
            
            if category == "vital_signs":
                return {name: vs.to_dict() for name, vs in self.vital_signs.items()}
            elif category == "symptoms":
                return [symptom.to_dict() for symptom in self.symptoms]
            elif category == "medical_history":
                return self.medical_history.to_dict()
            elif category == "physical_exam":
                return self.physical_exam.to_dict()
                
        elif category == "lab_results" and item_name:
            if item_name in self.lab_results:
                self.revealed_info["lab_results"][item_name] = True
                return self.lab_results[item_name].to_dict()
            
            if hasattr(self, "_potential_lab_results") and item_name in self._potential_lab_results:
                self.lab_results[item_name] = self._potential_lab_results[item_name]
                self.revealed_info["lab_results"][item_name] = True
                return self.lab_results[item_name].to_dict()
                
        elif category == "imaging_studies" and item_name:
            for i, study in enumerate(self.imaging_studies):
                if study.name == item_name:
                    self.revealed_info["imaging_studies"][item_name] = True
                    return study.to_dict()
            
            if hasattr(self, "_potential_imaging_studies"):
                for study in self._potential_imaging_studies:
                    if study.name == item_name:
                        self.imaging_studies.append(study)
                        self.revealed_info["imaging_studies"][item_name] = True
                        return study.to_dict()
        
        return {}
    
    def get_revealed_info(self) -> Dict:
        """Get all information that has been revealed so far."""
        revealed = {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "chief_complaint": self.chief_complaint,
            "history_of_present_illness": self.history_of_present_illness
        }
        
        if self.revealed_info["vital_signs"]:
            revealed["vital_signs"] = {name: vs.to_dict() for name, vs in self.vital_signs.items()}
            
        if self.revealed_info["symptoms"]:
            revealed["symptoms"] = [symptom.to_dict() for symptom in self.symptoms]
            
        if self.revealed_info["medical_history"]:
            revealed["medical_history"] = self.medical_history.to_dict()
            
        if self.revealed_info["physical_exam"]:
            revealed["physical_exam"] = self.physical_exam.to_dict()
            
        revealed["lab_results"] = {}
        for test_name, revealed_status in self.revealed_info["lab_results"].items():
            if revealed_status and test_name in self.lab_results:
                revealed["lab_results"][test_name] = self.lab_results[test_name].to_dict()
                
        revealed["imaging_studies"] = []
        for study_name, revealed_status in self.revealed_info["imaging_studies"].items():
            if revealed_status:
                for study in self.imaging_studies:
                    if study.name == study_name:
                        revealed["imaging_studies"].append(study.to_dict())
        
        return revealed
    
    def evaluate_diagnosis(self, diagnoses: List[Dict]) -> Dict:
        """
        Evaluate student's diagnosis.
        
        Args:
            diagnoses: List of diagnoses from the student
            
        Returns:
            Evaluation result
        """
        correct_diagnoses = {d["name"]: d["probability"] for d in self.diagnoses}
        student_diagnoses = {d["name"]: d.get("probability", 0) for d in diagnoses}
        
        # Calculate score
        score = 0
        max_score = 0
        feedback = []
        
        for diagnosis, probability in correct_diagnoses.items():
            max_score += probability * 100
            
            if diagnosis in student_diagnoses:
                # Award points based on probability matching
                student_prob = student_diagnoses[diagnosis]
                score_factor = 1 - min(abs(probability - student_prob), 0.5) * 2
                diagnosis_score = probability * 100 * score_factor
                score += diagnosis_score
                
                feedback.append({
                    "diagnosis": diagnosis,
                    "correct": True,
                    "correct_probability": probability,
                    "student_probability": student_prob,
                    "score": diagnosis_score
                })
            else:
                feedback.append({
                    "diagnosis": diagnosis,
                    "correct": False,
                    "correct_probability": probability,
                    "student_probability": 0,
                    "score": 0,
                    "message": "Missed diagnosis"
                })
        
        # Check for incorrect diagnoses
        for diagnosis, probability in student_diagnoses.items():
            if diagnosis not in correct_diagnoses and probability > 0.1:
                penalty = probability * 50  # Penalty for incorrect diagnosis
                score -= penalty
                
                feedback.append({
                    "diagnosis": diagnosis,
                    "correct": False,
                    "correct_probability": 0,
                    "student_probability": probability,
                    "score": -penalty,
                    "message": "Incorrect diagnosis"
                })
        
        # Normalize score
        final_score = max(0, min(100, (score / max_score) * 100)) if max_score > 0 else 0
        
        return {
            "score": final_score,
            "feedback": feedback,
            "correct_diagnoses": self.diagnoses,
            "expert_reasoning": self.expert_reasoning
        }
    
    def to_dict(self) -> Dict:
        """Convert virtual patient to dictionary."""
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "chief_complaint": self.chief_complaint,
            "history_of_present_illness": self.history_of_present_illness,
            "vital_signs": {name: vs.to_dict() for name, vs in self.vital_signs.items()},
            "symptoms": [symptom.to_dict() for symptom in self.symptoms],
            "medical_history": self.medical_history.to_dict(),
            "physical_exam": self.physical_exam.to_dict(),
            "lab_results": {name: test.to_dict() for name, test in self.lab_results.items()},
            "imaging_studies": [study.to_dict() for study in self.imaging_studies],
            "diagnoses": self.diagnoses,
            "scenario_difficulty": self.scenario_difficulty,
            "expert_reasoning": self.expert_reasoning
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "VirtualPatient":
        """Create a virtual patient from dictionary."""
        # Convert dictionary representations back to objects
        vital_signs = {}
        for name, vs_data in data.get("vital_signs", {}).items():
            vital_signs[name] = VitalSign(
                name=vs_data["name"],
                current_value=vs_data["value"],
                unit=vs_data["unit"],
                min_normal=vs_data["normal_range"][0],
                max_normal=vs_data["normal_range"][1],
                critical_low=vs_data["critical_range"][0],
                critical_high=vs_data["critical_range"][1],
                trend=vs_data.get("trend", "stable")
            )
        
        symptoms = []
        for s_data in data.get("symptoms", []):
            symptoms.append(Symptom(
                name=s_data["name"],
                description=s_data["description"],
                severity=s_data["severity"],
                onset_time=s_data.get("onset"),
                duration=s_data.get("duration"),
                characteristics=s_data.get("characteristics"),
                associated_factors=s_data.get("associated_factors")
            ))
        
        medical_history = MedicalHistory(
            conditions=data.get("medical_history", {}).get("conditions"),
            surgeries=data.get("medical_history", {}).get("surgeries"),
            medications=data.get("medical_history", {}).get("medications"),
            allergies=data.get("medical_history", {}).get("allergies"),
            family_history=data.get("medical_history", {}).get("family_history"),
            social_history=data.get("medical_history", {}).get("social_history")
        )
        
        physical_exam = PhysicalExam(
            general_appearance=data.get("physical_exam", {}).get("general_appearance", {}),
            systems=data.get("physical_exam", {}).get("systems", {})
        )
        
        lab_results = {}
        for name, lr_data in data.get("lab_results", {}).items():
            lab_results[name] = LabResult(
                name=lr_data["name"],
                value=lr_data["value"],
                unit=lr_data["unit"],
                reference_range=lr_data["reference_range"],
                timestamp=lr_data["timestamp"],
                critical=lr_data.get("critical", False),
                notes=lr_data.get("notes")
            )
        
        imaging_studies = []
        for is_data in data.get("imaging_studies", []):
            imaging_studies.append(ImagingStudy(
                name=is_data["name"],
                modality=is_data["modality"],
                findings=is_data["findings"],
                impression=is_data["impression"],
                timestamp=is_data["timestamp"],
                images=is_data.get("images"),
                notes=is_data.get("notes")
            ))
        
        return cls(
            patient_id=data["patient_id"],
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            chief_complaint=data["chief_complaint"],
            history_of_present_illness=data["history_of_present_illness"],
            vital_signs=vital_signs,
            symptoms=symptoms,
            medical_history=medical_history,
            physical_exam=physical_exam,
            lab_results=lab_results,
            imaging_studies=imaging_studies,
            diagnoses=data.get("diagnoses", []),
            scenario_difficulty=data.get("scenario_difficulty", 1),
            expert_reasoning=data.get("expert_reasoning")
        )