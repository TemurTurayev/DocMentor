"""
Diagnostic engine for virtual patients.
Evaluates diagnostic decisions and provides feedback.
"""

import logging
from typing import Dict, List, Optional, Union, Any

from .patient_model import VirtualPatient

logger = logging.getLogger(__name__)

class DiagnosticEngine:
    """Engine for evaluating diagnostic decisions in virtual patient scenarios."""
    
    def __init__(self):
        """Initialize diagnostic engine."""
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2
        }
    
    def evaluate_diagnosis(
        self, 
        patient: VirtualPatient, 
        student_diagnosis: List[Dict],
        revealed_info: Dict
    ) -> Dict:
        """
        Evaluate student's diagnostic process.
        
        Args:
            patient: Virtual patient object
            student_diagnosis: List of diagnoses with probability estimates
            revealed_info: Information that was revealed during the case
            
        Returns:
            Dict with evaluation results and feedback
        """
        # Get patient's actual diagnoses
        actual_diagnoses = {d["name"]: d["probability"] for d in patient.diagnoses}
        student_diagnoses = {d["name"]: d.get("probability", 0) for d in student_diagnosis}
        
        # Calculate score
        score = self._calculate_score(actual_diagnoses, student_diagnoses)
        
        # Generate feedback
        feedback = self._generate_feedback(
            actual_diagnoses, 
            student_diagnoses, 
            revealed_info
        )
        
        # Create evaluation result
        evaluation = {
            "score": score,
            "feedback": feedback,
            "correct_diagnoses": patient.diagnoses,
            "used_information": self._analyze_information_usage(revealed_info),
            "expert_reasoning": patient.expert_reasoning
        }
        
        return evaluation
    
    def _calculate_score(self, actual_diagnoses: Dict, student_diagnoses: Dict) -> float:
        """
        Calculate diagnostic score.
        
        Args:
            actual_diagnoses: Actual diagnoses with probabilities
            student_diagnoses: Student's diagnoses with probabilities
            
        Returns:
            Score (0-100)
        """
        # Placeholder implementation
        # The full implementation will provide more comprehensive scoring
        return 75.0
    
    def _generate_feedback(
        self, 
        actual_diagnoses: Dict, 
        student_diagnoses: Dict,
        revealed_info: Dict
    ) -> List[Dict]:
        """
        Generate detailed feedback on diagnostic process.
        
        Args:
            actual_diagnoses: Actual diagnoses with probabilities
            student_diagnoses: Student's diagnoses with probabilities
            revealed_info: Information revealed during diagnosis
            
        Returns:
            List of feedback items
        """
        # Placeholder implementation
        feedback = []
        
        for diagnosis, probability in actual_diagnoses.items():
            if diagnosis in student_diagnoses:
                student_prob = student_diagnoses[diagnosis]
                accuracy = 1 - min(abs(probability - student_prob), 0.5) * 2
                
                feedback.append({
                    "diagnosis": diagnosis,
                    "correct": True,
                    "actual_probability": probability,
                    "student_probability": student_prob,
                    "accuracy": accuracy,
                    "comment": "Good job identifying this diagnosis."
                })
            else:
                feedback.append({
                    "diagnosis": diagnosis,
                    "correct": False,
                    "actual_probability": probability,
                    "student_probability": 0,
                    "accuracy": 0,
                    "comment": "You missed this diagnosis."
                })
                
        # Check for incorrect diagnoses
        for diagnosis, probability in student_diagnoses.items():
            if diagnosis not in actual_diagnoses and probability > 0.1:
                feedback.append({
                    "diagnosis": diagnosis,
                    "correct": False,
                    "actual_probability": 0,
                    "student_probability": probability,
                    "accuracy": 0,
                    "comment": "This diagnosis is not correct for this patient."
                })
                
        return feedback
    
    def _analyze_information_usage(self, revealed_info: Dict) -> Dict:
        """
        Analyze how effectively the student used available information.
        
        Args:
            revealed_info: Information revealed during diagnosis
            
        Returns:
            Analysis of information usage
        """
        # Placeholder implementation
        return {
            "vital_signs_usage": "good",
            "symptoms_usage": "good",
            "lab_results_usage": "medium",
            "imaging_studies_usage": "low",
            "suggestion": "Consider utilizing imaging studies more effectively in your diagnostic process."
        }