"""
Case generator for virtual patients.
Creates realistic medical cases with varying complexity levels.
"""

import json
import random
import uuid
import os
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
import logging
from datetime import datetime, timedelta
import time

from .patient_model import (
    VirtualPatient, 
    VitalSign, 
    Symptom, 
    MedicalHistory,
    PhysicalExam,
    LabResult,
    ImagingStudy
)

logger = logging.getLogger(__name__)

class CaseGenerator:
    """Generator for virtual patient cases with varying complexity."""
    
    def __init__(
        self,
        templates_path: Union[str, Path],
        difficulty_level: int = 1,  # 1-5 scale
        specialties: Optional[List[str]] = None
    ):
        """
        Initialize case generator.
        
        Args:
            templates_path: Path to case templates directory
            difficulty_level: Default difficulty level (1-5)
            specialties: List of medical specialties to include
        """
        self.templates_path = Path(templates_path)
        self.difficulty_level = max(1, min(5, difficulty_level))
        self.specialties = specialties or [
            "internal_medicine",
            "pediatrics",
            "cardiology",
            "pulmonology",
            "neurology",
            "gastroenterology",
            "nephrology",
            "endocrinology"
        ]
        
        # Load templates
        self.templates = self._load_templates()
        
        # Load case patterns
        self.case_patterns = self._load_case_patterns()
    
    def _load_templates(self) -> Dict:
        """Load all available case templates."""
        templates = {}
        
        try:
            # Ensure templates directory exists
            os.makedirs(self.templates_path, exist_ok=True)
            
            # Load templates for each specialty
            for specialty in self.specialties:
                specialty_path = self.templates_path / specialty
                
                if not specialty_path.exists():
                    logger.warning(f"No templates found for specialty: {specialty}")
                    continue
                
                specialty_templates = []
                
                # Load each template file
                for template_file in specialty_path.glob("*.json"):
                    try:
                        with open(template_file, 'r') as f:
                            template = json.load(f)
                            specialty_templates.append(template)
                    except json.JSONDecodeError:
                        logger.error(f"Error parsing template file: {template_file}")
                
                templates[specialty] = specialty_templates
                logger.info(f"Loaded {len(specialty_templates)} templates for {specialty}")
            
            # If no templates were found, generate some basic templates
            if not any(templates.values()):
                logger.warning("No templates found, generating basic templates")
                templates = self._generate_basic_templates()
            
            return templates
        
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            return self._generate_basic_templates()
    
    def _generate_basic_templates(self) -> Dict:
        """Generate basic templates when none are available."""
        templates = {}
        
        # Basic internal medicine templates
        templates["internal_medicine"] = [
            {
                "name": "Pneumonia Case",
                "chief_complaint": "Cough and fever for 3 days",
                "demographics": {
                    "age_range": [18, 80],
                    "gender": ["male", "female"]
                },
                "history_patterns": [
                    "Patient reports {duration} days of productive cough with {color} sputum.",
                    "Associated symptoms include fever up to {temp}°C, {severity} shortness of breath, and general malaise.",
                    "Patient {has_travel} recent travel history and {has_contacts} known sick contacts."
                ],
                "vital_sign_patterns": {
                    "temperature": {"min": 38.0, "max": 39.5, "unit": "°C"},
                    "heart_rate": {"min": 90, "max": 120, "unit": "bpm"},
                    "respiratory_rate": {"min": 20, "max": 30, "unit": "breaths/min"},
                    "blood_pressure": {"min": [100, 60], "max": [140, 90], "unit": "mmHg"},
                    "oxygen_saturation": {"min": 88, "max": 94, "unit": "%"}
                },
                "symptoms": [
                    {"name": "Cough", "severity_range": [5, 9]},
                    {"name": "Fever", "severity_range": [6, 9]},
                    {"name": "Shortness of Breath", "severity_range": [4, 8]},
                    {"name": "Fatigue", "severity_range": [5, 8]}
                ],
                "physical_exam_findings": {
                    "general_appearance": "Patient appears {appearance}, {position} in bed.",
                    "respiratory": {
                        "patterns": [
                            "Decreased breath sounds in the {location} lung field.",
                            "Crackles heard in the {location} lung base.",
                            "{presence} of wheezing or rhonchi."
                        ]
                    }
                },
                "lab_result_patterns": {
                    "Complete Blood Count": {
                        "White Blood Cell Count": {"min": 12.0, "max": 18.0, "unit": "10^9/L", "reference": [4.5, 11.0]},
                        "Neutrophils": {"min": 70, "max": 85, "unit": "%", "reference": [40, 70]},
                        "Lymphocytes": {"min": 10, "max": 20, "unit": "%", "reference": [20, 40]}
                    },
                    "Basic Metabolic Panel": {
                        "Sodium": {"min": 135, "max": 145, "unit": "mmol/L", "reference": [135, 145]},
                        "Potassium": {"min": 3.5, "max": 5.0, "unit": "mmol/L", "reference": [3.5, 5.0]}
                    }
                },
                "imaging_patterns": {
                    "Chest X-ray": {
                        "findings_patterns": [
                            "There is a {density} opacity in the {location} lung field.",
                            "No pleural effusion is seen.",
                            "Heart size is normal."
                        ],
                        "impression_patterns": [
                            "Findings consistent with {location} pneumonia.",
                            "No evidence of pleural effusion or pneumothorax."
                        ]
                    }
                },
                "diagnoses": [
                    {"name": "Community-acquired Pneumonia", "probability": 0.8},
                    {"name": "Acute Bronchitis", "probability": 0.15},
                    {"name": "COVID-19", "probability": 0.05}
                ],
                "difficulty": 1
            },
            {
                "name": "Diabetic Ketoacidosis Case",
                "chief_complaint": "Extreme thirst, frequent urination, and fatigue",
                "demographics": {
                    "age_range": [18, 65],
                    "gender": ["male", "female"]
                },
                "history_patterns": [
                    "Patient reports {duration} days of increased thirst, frequent urination, and fatigue.",
                    "Patient {has_diabetes|has been newly diagnosed with diabetes|has undiagnosed diabetes}.",
                    "Associated symptoms include {symptoms}."
                ],
                "vital_sign_patterns": {
                    "temperature": {"min": 36.5, "max": 38.5, "unit": "°C"},
                    "heart_rate": {"min": 100, "max": 130, "unit": "bpm"},
                    "respiratory_rate": {"min": 20, "max": 30, "unit": "breaths/min"},
                    "blood_pressure": {"min": [90, 60], "max": [130, 85], "unit": "mmHg"}
                },
                "symptoms": [
                    {"name": "Polydipsia", "severity_range": [7, 10]},
                    {"name": "Polyuria", "severity_range": [7, 10]},
                    {"name": "Fatigue", "severity_range": [6, 9]},
                    {"name": "Nausea", "severity_range": [3, 7]},
                    {"name": "Abdominal Pain", "severity_range": [2, 6]}
                ],
                "physical_exam_findings": {
                    "general_appearance": "Patient appears {appearance}, with {skin_desc} skin.",
                    "respiratory": {
                        "patterns": [
                            "Respiratory rate is increased with deep breathing pattern (Kussmaul respirations).",
                            "No adventitious lung sounds."
                        ]
                    },
                    "cardiovascular": {
                        "patterns": [
                            "Tachycardia present.",
                            "No murmurs, gallops, or rubs."
                        ]
                    }
                },
                "lab_result_patterns": {
                    "Basic Metabolic Panel": {
                        "Glucose": {"min": 300, "max": 600, "unit": "mg/dL", "reference": [70, 110]},
                        "Sodium": {"min": 125, "max": 135, "unit": "mmol/L", "reference": [135, 145]},
                        "Potassium": {"min": 4.5, "max": 6.0, "unit": "mmol/L", "reference": [3.5, 5.0]},
                        "Bicarbonate": {"min": 5, "max": 15, "unit": "mmol/L", "reference": [22, 28]},
                        "BUN": {"min": 20, "max": 40, "unit": "mg/dL", "reference": [7, 20]},
                        "Creatinine": {"min": 1.0, "max": 2.0, "unit": "mg/dL", "reference": [0.6, 1.2]}
                    },
                    "Arterial Blood Gas": {
                        "pH": {"min": 7.0, "max": 7.3, "unit": "", "reference": [7.35, 7.45]},
                        "pCO2": {"min": 15, "max": 30, "unit": "mmHg", "reference": [35, 45]},
                        "pO2": {"min": 80, "max": 100, "unit": "mmHg", "reference": [80, 100]}
                    },
                    "Urinalysis": {
                        "Glucose": {"value": "Positive", "unit": "", "reference": "Negative"},
                        "Ketones": {"value": "Positive", "unit": "", "reference": "Negative"}
                    }
                },
                "diagnoses": [
                    {"name": "Diabetic Ketoacidosis", "probability": 0.9},
                    {"name": "Hyperglycemic Hyperosmolar State", "probability": 0.08},
                    {"name": "Lactic Acidosis", "probability": 0.02}
                ],
                "difficulty": 2
            }
        ]
        
        # Save generated templates
        for specialty, specialty_templates in templates.items():
            specialty_path = self.templates_path / specialty
            os.makedirs(specialty_path, exist_ok=True)
            
            for idx, template in enumerate(specialty_templates):
                template_path = specialty_path / f"{template['name'].lower().replace(' ', '_')}_{idx}.json"
                with open(template_path, 'w') as f:
                    json.dump(template, f, indent=2)
        
        logger.info("Generated and saved basic templates")
        return templates
    
    def _load_case_patterns(self) -> Dict:
        """Load case patterns for generating variations."""
        # These are patterns used to add variety to generated cases
        return {
            "duration": [1, 2, 3, 4, 5, 7, 10, 14, 21, 30],
            "color": ["yellow", "green", "white", "clear", "blood-tinged"],
            "severity": ["mild", "moderate", "severe"],
            "appearance": ["acutely ill", "chronically ill", "mildly distressed", "comfortable", "anxious", "lethargic"],
            "position": ["sitting upright", "lying supine", "in Fowler's position", "restless"],
            "location": ["right upper", "right middle", "right lower", "left upper", "left middle", "left lower", "bilateral"],
            "density": ["patchy", "dense", "diffuse", "mild", "moderate"],
            "presence": ["Presence", "Absence"],
            "has_travel": ["has", "denies"],
            "has_contacts": ["has", "denies"],
            "skin_desc": ["dry", "clammy", "pale", "flushed", "warm", "cool"],
            "temp": [37.8, 38.0, 38.5, 39.0, 39.5, 40.0],
            "has_diabetes": ["has a history of Type 1 Diabetes", "has a history of Type 2 Diabetes", "has newly diagnosed diabetes", "has undiagnosed diabetes"],
            "symptoms": [
                "nausea and vomiting", 
                "abdominal pain", 
                "blurry vision", 
                "headache",
                "weight loss",
                "fruity-smelling breath"
            ]
        }
    
    def select_template(self, specialty: Optional[str] = None, difficulty: Optional[int] = None) -> Dict:
        """
        Select a case template based on specialty and difficulty.
        
        Args:
            specialty: Medical specialty (if None, randomly selected)
            difficulty: Case difficulty (if None, uses default)
            
        Returns:
            Selected case template
        """
        # Use provided values or defaults
        difficulty = difficulty or self.difficulty_level
        
        # Select specialty
        if specialty is None or specialty not in self.templates:
            available_specialties = list(self.templates.keys())
            if not available_specialties:
                raise ValueError("No templates available")
            specialty = random.choice(available_specialties)
        
        # Get templates for the selected specialty
        specialty_templates = self.templates.get(specialty, [])
        if not specialty_templates:
            raise ValueError(f"No templates available for specialty: {specialty}")
        
        # Filter by difficulty if specified
        difficulty_templates = [t for t in specialty_templates if t.get("difficulty", 1) == difficulty]
        
        # If no templates match the difficulty, use all templates
        if not difficulty_templates:
            difficulty_templates = specialty_templates
        
        # Randomly select a template
        return random.choice(difficulty_templates)
    
    def generate_case(
        self,
        specialty: Optional[str] = None,
        difficulty: Optional[int] = None,
        template: Optional[Dict] = None
    ) -> VirtualPatient:
        """
        Generate a virtual patient case.
        
        Args:
            specialty: Medical specialty (if None, randomly selected)
            difficulty: Case difficulty (if None, uses default)
            template: Specific template to use (if None, one is selected)
            
        Returns:
            Generated virtual patient
        """
        # Select template if not provided
        if template is None:
            template = self.select_template(specialty, difficulty)
        
        # Generate a unique ID for the patient
        patient_id = str(uuid.uuid4())
        
        # Generate patient demographics
        demographics = self._generate_demographics(template.get("demographics", {}))
        
        # Generate history of present illness
        history = self._generate_history(template.get("history_patterns", []))
        
        # Generate vital signs
        vital_signs = self._generate_vital_signs(template.get("vital_sign_patterns", {}))
        
        # Generate symptoms
        symptoms = self._generate_symptoms(template.get("symptoms", []))
        
        # Generate physical exam findings
        physical_exam = self._generate_physical_exam(template.get("physical_exam_findings", {}))
        
        # Generate lab results (but don't add them yet - they'll be revealed during the case)
        lab_results = self._generate_lab_results(template.get("lab_result_patterns", {}))
        
        # Generate imaging studies (but don't add them yet - they'll be revealed during the case)
        imaging_studies = self._generate_imaging_studies(template.get("imaging_patterns", {}))
        
        # Create the virtual patient
        patient = VirtualPatient(
            patient_id=patient_id,
            name=demographics["name"],
            age=demographics["age"],
            gender=demographics["gender"],
            chief_complaint=template.get("chief_complaint", ""),
            history_of_present_illness=history,
            vital_signs=vital_signs,
            symptoms=symptoms,
            medical_history=self._generate_medical_history(template.get("medical_history", {})),
            physical_exam=physical_exam,
            # Lab results and imaging studies are empty to start
            lab_results={},
            imaging_studies=[],
            diagnoses=template.get("diagnoses", []),
            scenario_difficulty=template.get("difficulty", self.difficulty_level),
            expert_reasoning=template.get("expert_reasoning", "")
        )
        
        # Store the potential lab results and imaging studies for later revelation
        patient._potential_lab_results = lab_results
        patient._potential_imaging_studies = imaging_studies
        
        return patient
    
    def _generate_demographics(self, demographics_template: Dict) -> Dict:
        """Generate patient demographics based on template."""
        # Generate age
        age_range = demographics_template.get("age_range", [18, 80])
        age = random.randint(age_range[0], age_range[1])
        
        # Generate gender
        gender_options = demographics_template.get("gender", ["male", "female"])
        gender = random.choice(gender_options)
        
        # Generate name based on gender
        if gender.lower() == "male":
            first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
        else:
            first_names = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
            
        last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
        
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        return {
            "name": name,
            "age": age,
            "gender": gender
        }
    
    def _generate_history(self, history_patterns: List[str]) -> str:
        """Generate history of present illness from patterns."""
        if not history_patterns:
            return "Patient presents with chief complaint."
            
        # Process each pattern, replacing placeholders with values
        processed_patterns = []
        for pattern in history_patterns:
            processed = self._process_pattern(pattern)
            processed_patterns.append(processed)
            
        # Join the patterns into a complete history
        return " ".join(processed_patterns)
    
    def _process_pattern(self, pattern: str) -> str:
        """Process a pattern string, replacing placeholders with values."""
        # Handle simple placeholders like {duration}
        for placeholder, values in self.case_patterns.items():
            if f"{{{placeholder}}}" in pattern:
                value = random.choice(values) if isinstance(values, list) else values
                pattern = pattern.replace(f"{{{placeholder}}}", str(value))
                
        # Handle choice placeholders like {option1|option2|option3}
        import re
        choice_pattern = r'\{([^{}]*\|[^{}]*)\}'
        choices = re.findall(choice_pattern, pattern)
        for choice_str in choices:
            options = choice_str.split('|')
            replacement = random.choice(options)
            pattern = pattern.replace(f"{{{choice_str}}}", replacement)
            
        return pattern
    
    def _generate_vital_signs(self, vital_sign_patterns: Dict) -> Dict[str, VitalSign]:
        """Generate vital signs based on patterns."""
        vital_signs = {}
        
        for name, pattern in vital_sign_patterns.items():
            if isinstance(pattern.get("min"), list) and isinstance(pattern.get("max"), list):
                # Handle blood pressure and similar paired values
                min_values = pattern["min"]
                max_values = pattern["max"]
                
                # Generate a value within the range for each component
                values = []
                for i in range(len(min_values)):
                    value = random.uniform(min_values[i], max_values[i])
                    values.append(round(value, 1))
                
                # Format the value (e.g., "120/80")
                current_value = "/".join(str(v) for v in values)
                
                # Use the systolic value as the numerical value for comparison
                numerical_value = values[0]
                
                # Define normal ranges
                if name.lower() == "blood_pressure":
                    min_normal, max_normal = 90, 140  # Systolic
                    critical_low, critical_high = 80, 180  # Systolic
                else:
                    min_normal, max_normal = pattern.get("reference", [0, 100])
                    critical_low = min_normal * 0.7
                    critical_high = max_normal * 1.3
            else:
                # Handle single values
                min_value = pattern.get("min", 0)
                max_value = pattern.get("max", 100)
                
                # Generate a value within the range
                numerical_value = random.uniform(min_value, max_value)
                current_value = round(numerical_value, 1)
                
                # Define normal ranges
                min_normal, max_normal = pattern.get("reference", [min_value, max_value])
                critical_low = pattern.get("critical_low", min_normal * 0.7)
                critical_high = pattern.get("critical_high", max_normal * 1.3)
            
            # Create the vital sign
            vital_sign = VitalSign(
                name=name.replace("_", " ").title(),
                current_value=current_value,
                unit=pattern.get("unit", ""),
                min_normal=min_normal,
                max_normal=max_normal,
                critical_low=critical_low,
                critical_high=critical_high
            )
            
            vital_signs[name] = vital_sign
            
        return vital_signs
    
    def _generate_symptoms(self, symptom_patterns: List[Dict]) -> List[Symptom]:
        """Generate symptoms based on patterns."""
        symptoms = []
        
        for pattern in symptom_patterns:
            name = pattern.get("name", "")
            
            # Generate severity within the specified range
            severity_range = pattern.get("severity_range", [1, 10])
            severity = random.randint(severity_range[0], severity_range[1])
            
            # Generate onset time (between 1 hour and 30 days ago)
            max_onset_days = pattern.get("max_onset_days", 30)
            onset_time = time.time() - random.uniform(3600, max_onset_days * 86400)
            
            # Generate duration
            duration = pattern.get("duration", time.time() - onset_time)
            
            # Create the symptom
            symptom = Symptom(
                name=name,
                description=pattern.get("description", f"Patient reports {name.lower()}"),
                severity=severity,
                onset_time=onset_time,
                duration=duration,
                characteristics=pattern.get("characteristics", []),
                associated_factors=pattern.get("associated_factors", {})
            )
            
            symptoms.append(symptom)
            
        return symptoms
    
    def _generate_physical_exam(self, exam_patterns: Dict) -> PhysicalExam:
        """Generate physical examination findings."""
        # Process general appearance
        general_appearance = {
            "description": self._process_pattern(exam_patterns.get("general_appearance", "Patient appears in no acute distress.")),
            "details": {}
        }
        
        # Process findings by system
        systems = {}
        for system_name, system_data in exam_patterns.items():
            if system_name == "general_appearance":
                continue
                
            # Initialize system
            systems[system_name] = {
                "description": "",
                "findings": {}
            }
            
            # Process patterns for this system
            if isinstance(system_data, dict) and "patterns" in system_data:
                patterns = system_data["patterns"]
                findings = []
                
                for pattern in patterns:
                    processed = self._process_pattern(pattern)
                    findings.append(processed)
                    
                # Update description and findings
                systems[system_name]["description"] = " ".join(findings)
                
                # Add specific findings if provided
                if "findings" in system_data:
                    for finding_name, finding_details in system_data["findings"].items():
                        processed_details = self._process_pattern(finding_details)
                        systems[system_name]["findings"][finding_name] = processed_details
            else:
                # Handle simple string description
                systems[system_name]["description"] = self._process_pattern(str(system_data))
        
        # Create physical exam object
        physical_exam = PhysicalExam(
            general_appearance=general_appearance,
            systems=systems
        )
        
        return physical_exam
    
    def _generate_medical_history(self, history_patterns: Dict) -> MedicalHistory:
        """Generate medical history."""
        # For now, return an empty medical history
        # This would be expanded with more sophisticated logic in a real implementation
        return MedicalHistory()
    
    def _generate_lab_results(self, lab_patterns: Dict) -> Dict[str, LabResult]:
        """Generate laboratory results based on patterns."""
        lab_results = {}
        
        for test_name, test_patterns in lab_patterns.items():
            for component_name, component_pattern in test_patterns.items():
                # Handle numeric values
                if "min" in component_pattern and "max" in component_pattern:
                    min_value = component_pattern["min"]
                    max_value = component_pattern["max"]
                    value = round(random.uniform(min_value, max_value), 1)
                    
                    # Get reference range
                    reference_range = component_pattern.get("reference", [0, 100])
                    
                    # Determine if it's critical
                    critical = False
                    if reference_range[0] > 0 and value < reference_range[0] * 0.5:
                        critical = True
                    elif value > reference_range[1] * 1.5:
                        critical = True
                        
                # Handle non-numeric values
                else:
                    value = component_pattern.get("value", "")
                    reference_range = component_pattern.get("reference", "")
                    critical = component_pattern.get("critical", False)
                
                # Create the lab result
                result_name = f"{test_name} - {component_name}"
                lab_results[result_name] = LabResult(
                    name=result_name,
                    value=value,
                    unit=component_pattern.get("unit", ""),
                    reference_range=reference_range,
                    timestamp=time.time(),
                    critical=critical
                )
                
        return lab_results
    
    def _generate_imaging_studies(self, imaging_patterns: Dict) -> List[ImagingStudy]:
        """Generate imaging studies based on patterns."""
        imaging_studies = []
        
        for study_name, study_pattern in imaging_patterns.items():
            # Process findings patterns
            findings = []
            for pattern in study_pattern.get("findings_patterns", []):
                findings.append(self._process_pattern(pattern))
                
            # Process impression patterns
            impressions = []
            for pattern in study_pattern.get("impression_patterns", []):
                impressions.append(self._process_pattern(pattern))
                
            # Create the imaging study
            study = ImagingStudy(
                name=study_name,
                modality=study_pattern.get("modality", study_name),
                findings=" ".join(findings),
                impression=" ".join(impressions),
                timestamp=time.time(),
                images=study_pattern.get("images", [])
            )
            
            imaging_studies.append(study)
            
        return imaging_studies
    
    def save_patient_to_file(self, patient: VirtualPatient, output_path: Union[str, Path]) -> str:
        """
        Save a virtual patient to a JSON file.
        
        Args:
            patient: Virtual patient object
            output_path: Directory to save the file
            
        Returns:
            Path to saved file
        """
        output_path = Path(output_path)
        os.makedirs(output_path, exist_ok=True)
        
        # Create a filename
        filename = f"{patient.patient_id}_{patient.name.replace(' ', '_').lower()}.json"
        file_path = output_path / filename
        
        # Convert patient to dictionary
        patient_dict = patient.to_dict()
        
        # Add potential lab results and imaging studies if available
        if hasattr(patient, "_potential_lab_results"):
            patient_dict["_potential_lab_results"] = {
                name: result.to_dict() for name, result in patient._potential_lab_results.items()
            }
            
        if hasattr(patient, "_potential_imaging_studies"):
            patient_dict["_potential_imaging_studies"] = [
                study.to_dict() for study in patient._potential_imaging_studies
            ]
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(patient_dict, f, indent=2)
            
        logger.info(f"Saved patient to {file_path}")
        return str(file_path)
    
    def batch_generate(
        self,
        count: int,
        output_path: Union[str, Path],
        specialties: Optional[List[str]] = None,
        difficulty_range: Optional[Tuple[int, int]] = None
    ) -> List[str]:
        """
        Generate multiple virtual patient cases.
        
        Args:
            count: Number of cases to generate
            output_path: Directory to save the files
            specialties: List of specialties to use (if None, uses all available)
            difficulty_range: Range of difficulties to use (if None, uses default)
            
        Returns:
            List of paths to saved files
        """
        output_path = Path(output_path)
        os.makedirs(output_path, exist_ok=True)
        
        # Use provided specialties or default
        if specialties is None:
            specialties = list(self.templates.keys())
            
        # Use provided difficulty range or default
        min_difficulty, max_difficulty = difficulty_range or (1, 5)
        
        # Generate patients
        saved_paths = []
        for _ in range(count):
            try:
                # Select random specialty and difficulty
                specialty = random.choice(specialties)
                difficulty = random.randint(min_difficulty, max_difficulty)
                
                # Generate patient
                patient = self.generate_case(specialty=specialty, difficulty=difficulty)
                
                # Save patient
                saved_path = self.save_patient_to_file(patient, output_path)
                saved_paths.append(saved_path)
                
            except Exception as e:
                logger.error(f"Error generating patient: {str(e)}")
                
        return saved_paths
