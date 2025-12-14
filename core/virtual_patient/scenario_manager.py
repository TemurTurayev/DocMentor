"""
Scenario Manager - Manages clinical scenarios with staged progression.
Handles: anamnesis → physical exam → diagnosis → treatment plan
"""

import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ScenarioStage(Enum):
    """Stages of clinical consultation."""
    ANAMNESIS = "anamnesis"
    EXAMINATION = "examination"
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    COMPLETED = "completed"


class ScenarioManager:
    """
    Manages progression through clinical scenario stages.

    Stages:
    1. Anamnesis - collect patient history
    2. Examination - physical exam and vitals
    3. Diagnosis - formulate differential diagnosis
    4. Treatment - create treatment plan
    5. Completed - review and feedback
    """

    def __init__(self, patient_data: Dict, ai_patient=None):
        """
        Initialize scenario manager.

        Args:
            patient_data: Complete patient case data
            ai_patient: AIPatient instance
        """
        self.patient_data = patient_data
        self.ai_patient = ai_patient
        self.current_stage = ScenarioStage.ANAMNESIS

        # Track student's decisions
        self.student_decisions = {
            "differential_diagnosis": [],
            "diagnostic_tests": [],
            "treatment_plan": [],
            "final_diagnosis": None
        }

        # Expected answers (from patient data)
        self.expected = {
            "diagnoses": patient_data.get("diagnoses", []),
            "recommended_tests": patient_data.get("recommended_tests", []),
            "treatment": patient_data.get("treatment", {})
        }

        logger.info(f"ScenarioManager initialized for: {patient_data.get('name', 'Unknown')}")

    def get_current_stage(self) -> str:
        """Get current stage name."""
        return self.current_stage.value

    def can_proceed_to_next_stage(self) -> tuple[bool, str]:
        """
        Check if student can move to next stage.

        Returns:
            (can_proceed: bool, message: str)
        """
        if self.current_stage == ScenarioStage.ANAMNESIS:
            # Check if enough information gathered
            if self.ai_patient:
                progress = self.ai_patient.get_progress()
                if progress["completeness"] >= 60:
                    return True, "Достаточно информации для осмотра."
                else:
                    return False, f"Соберите больше информации (сейчас {progress['completeness']}%)"
            else:
                return True, "Можно переходить к осмотру."

        elif self.current_stage == ScenarioStage.EXAMINATION:
            # Always can proceed after exam
            return True, "Осмотр завершен, можно ставить диагноз."

        elif self.current_stage == ScenarioStage.DIAGNOSIS:
            # Check if diagnosis provided
            if self.student_decisions["differential_diagnosis"]:
                return True, "Диагноз сформулирован, можно планировать лечение."
            else:
                return False, "Сформулируйте дифференциальный диагноз."

        elif self.current_stage == ScenarioStage.TREATMENT:
            # Check if treatment plan provided
            if self.student_decisions["treatment_plan"]:
                return True, "План лечения готов."
            else:
                return False, "Составьте план лечения."

        elif self.current_stage == ScenarioStage.COMPLETED:
            return False, "Сценарий уже завершен."

        return False, "Неизвестная стадия."

    def proceed_to_next_stage(self) -> Dict:
        """
        Move to next stage if possible.

        Returns:
            Dict with status and message
        """
        can_proceed, message = self.can_proceed_to_next_stage()

        if not can_proceed:
            return {
                "status": "blocked",
                "message": message,
                "current_stage": self.current_stage.value
            }

        # Move to next stage
        stages_order = [
            ScenarioStage.ANAMNESIS,
            ScenarioStage.EXAMINATION,
            ScenarioStage.DIAGNOSIS,
            ScenarioStage.TREATMENT,
            ScenarioStage.COMPLETED
        ]

        current_index = stages_order.index(self.current_stage)
        if current_index < len(stages_order) - 1:
            self.current_stage = stages_order[current_index + 1]

            # Update AI patient stage
            if self.ai_patient:
                self.ai_patient.set_stage(self.current_stage.value)

            logger.info(f"Progressed to stage: {self.current_stage.value}")

            return {
                "status": "success",
                "message": f"Переход на этап: {self._stage_name_ru(self.current_stage)}",
                "current_stage": self.current_stage.value,
                "next_instructions": self._get_stage_instructions()
            }
        else:
            return {
                "status": "completed",
                "message": "Сценарий завершен!",
                "current_stage": self.current_stage.value
            }

    def _stage_name_ru(self, stage: ScenarioStage) -> str:
        """Get Russian name for stage."""
        names = {
            ScenarioStage.ANAMNESIS: "Сбор анамнеза",
            ScenarioStage.EXAMINATION: "Физикальный осмотр",
            ScenarioStage.DIAGNOSIS: "Постановка диагноза",
            ScenarioStage.TREATMENT: "План лечения",
            ScenarioStage.COMPLETED: "Завершено"
        }
        return names.get(stage, stage.value)

    def _get_stage_instructions(self) -> str:
        """Get instructions for current stage."""
        instructions = {
            ScenarioStage.ANAMNESIS: "Задавайте вопросы пациенту, чтобы собрать анамнез. Узнайте о жалобах, истории заболевания, сопутствующих болезнях.",
            ScenarioStage.EXAMINATION: "Проведите физикальный осмотр. Данные осмотра, пульс, давление, температура и другие показатели доступны.",
            ScenarioStage.DIAGNOSIS: "Сформулируйте дифференциальный диагноз на основе собранной информации. Укажите наиболее вероятный диагноз и альтернативы.",
            ScenarioStage.TREATMENT: "Составьте план лечения. Включите медикаментозную терапию, режим, диету, рекомендации пациенту.",
            ScenarioStage.COMPLETED: "Сценарий завершен. Посмотрите оценку своей работы и экспертное мнение."
        }
        return instructions.get(self.current_stage, "")

    def add_differential_diagnosis(self, diagnosis: str, probability: float = 0.0):
        """Add diagnosis to differential list."""
        self.student_decisions["differential_diagnosis"].append({
            "diagnosis": diagnosis,
            "probability": probability
        })
        logger.info(f"Added diagnosis: {diagnosis} ({probability}%)")

    def add_diagnostic_test(self, test: str):
        """Add diagnostic test to plan."""
        self.student_decisions["diagnostic_tests"].append(test)
        logger.info(f"Added diagnostic test: {test}")

    def add_treatment(self, treatment: str, category: str = "medication"):
        """Add treatment to plan."""
        self.student_decisions["treatment_plan"].append({
            "treatment": treatment,
            "category": category
        })
        logger.info(f"Added treatment: {treatment}")

    def set_final_diagnosis(self, diagnosis: str):
        """Set final primary diagnosis."""
        self.student_decisions["final_diagnosis"] = diagnosis
        logger.info(f"Final diagnosis set: {diagnosis}")

    def get_examination_data(self) -> Dict:
        """
        Get physical examination data for current stage.

        Returns data based on stage:
        - Anamnesis: None (not yet examined)
        - Examination: All vitals and findings
        - Later: All data available
        """
        if self.current_stage == ScenarioStage.ANAMNESIS:
            return {
                "available": False,
                "message": "Физикальный осмотр еще не проведен."
            }

        exam_data = self.patient_data.get("physical_exam", {})
        vitals = self.patient_data.get("vitals", {})

        return {
            "available": True,
            "vitals": vitals,
            "general": exam_data.get("general", ""),
            "systems": exam_data.get("systems", {}),
            "findings": exam_data.get("key_findings", [])
        }

    def get_diagnostic_results(self, test_name: str) -> Optional[Dict]:
        """
        Get results of diagnostic test.

        Only available after ordering the test.
        """
        if self.current_stage.value in ["anamnesis", "examination"]:
            return {
                "available": False,
                "message": "Анализы доступны после постановки предварительного диагноза."
            }

        # Check if test was ordered
        if test_name not in self.student_decisions["diagnostic_tests"]:
            return {
                "available": False,
                "message": "Этот анализ не был назначен."
            }

        # Get results from patient data
        all_results = self.patient_data.get("lab_results", {})
        imaging = self.patient_data.get("imaging", {})

        # Check lab results
        if test_name in all_results:
            return {
                "available": True,
                "type": "lab",
                "results": all_results[test_name]
            }

        # Check imaging
        if test_name in imaging:
            return {
                "available": True,
                "type": "imaging",
                "results": imaging[test_name]
            }

        return {
            "available": False,
            "message": "Результаты этого исследования недоступны в данном случае."
        }

    def evaluate_diagnosis(self) -> Dict:
        """
        Evaluate student's differential diagnosis.

        Compares with expected diagnoses.
        """
        student_diagnoses = [d["diagnosis"] for d in self.student_decisions["differential_diagnosis"]]
        expected_diagnoses = [d["name"] for d in self.expected["diagnoses"]]

        # Check matches
        correct = []
        for student_dx in student_diagnoses:
            for expected_dx in expected_diagnoses:
                # Simple matching (can be improved)
                if student_dx.lower() in expected_dx.lower() or expected_dx.lower() in student_dx.lower():
                    correct.append({
                        "student": student_dx,
                        "expected": expected_dx,
                        "probability": next(
                            (d["probability"] for d in self.expected["diagnoses"] if d["name"] == expected_dx),
                            0
                        )
                    })

        # Calculate score
        score = (len(correct) / len(expected_diagnoses)) * 100 if expected_diagnoses else 0

        return {
            "score": round(score, 1),
            "correct_diagnoses": correct,
            "missed_diagnoses": [d for d in expected_diagnoses if not any(
                d.lower() in c["student"].lower() for c in correct
            )],
            "incorrect_diagnoses": [d for d in student_diagnoses if not any(
                d.lower() in c["student"].lower() for c in correct
            )],
            "expected": expected_diagnoses,
            "student": student_diagnoses
        }

    def evaluate_treatment(self) -> Dict:
        """Evaluate student's treatment plan."""
        student_treatments = [t["treatment"] for t in self.student_decisions["treatment_plan"]]
        expected_treatments = self.expected["treatment"].get("medications", [])

        # Simple matching
        matches = 0
        for student_tx in student_treatments:
            for expected_tx in expected_treatments:
                if expected_tx.lower() in student_tx.lower():
                    matches += 1
                    break

        score = (matches / len(expected_treatments)) * 100 if expected_treatments else 0

        return {
            "score": round(score, 1),
            "matches": matches,
            "total_expected": len(expected_treatments),
            "student_plan": student_treatments,
            "expected_plan": expected_treatments
        }

    def get_expert_feedback(self) -> Dict:
        """
        Get expert feedback on the entire case.

        Includes correct diagnosis, reasoning, and treatment.
        """
        expert_diagnosis = self.patient_data.get("expert_reasoning", {})

        return {
            "final_diagnosis": self.expected["diagnoses"][0] if self.expected["diagnoses"] else "Неизвестно",
            "reasoning": expert_diagnosis.get("reasoning", "Нет экспертного мнения"),
            "key_findings": expert_diagnosis.get("key_findings", []),
            "differential": expert_diagnosis.get("differential_diagnosis", []),
            "treatment_rationale": self.expected["treatment"].get("rationale", "")
        }

    def get_summary(self) -> Dict:
        """Get complete scenario summary."""
        return {
            "patient": {
                "name": self.patient_data.get("name"),
                "age": self.patient_data.get("age"),
                "chief_complaint": self.patient_data.get("chief_complaint")
            },
            "stage": self.current_stage.value,
            "student_performance": {
                "anamnesis": self.ai_patient.get_evaluation() if self.ai_patient else {},
                "diagnosis": self.evaluate_diagnosis(),
                "treatment": self.evaluate_treatment()
            },
            "decisions": self.student_decisions,
            "expert_feedback": self.get_expert_feedback()
        }

    def __repr__(self):
        return f"ScenarioManager(patient={self.patient_data.get('name')}, stage={self.current_stage.value})"
