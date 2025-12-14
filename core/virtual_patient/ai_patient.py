"""
AI Patient - Intelligent virtual patient that responds naturally to student questions.
Uses LLM to generate realistic patient responses in Russian.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AIPatient:
    """
    AI-powered virtual patient that responds naturally to student questions.

    The patient:
    - Responds in character (age, gender, personality)
    - Shows emotions and concerns
    - Gradually reveals information based on questions
    - Speaks like a real person, not a medical textbook
    """

    def __init__(
        self,
        patient_data: Dict,
        llm_pipeline=None,
        language: str = "russian"
    ):
        """
        Initialize AI patient.

        Args:
            patient_data: Patient information (demographics, symptoms, history, etc.)
            llm_pipeline: RAGPipeline instance for AI responses
            language: Response language (russian/english)
        """
        self.patient_data = patient_data
        self.llm = llm_pipeline
        self.language = language

        # Conversation history
        self.conversation_history = []

        # Current stage of consultation
        self.stage = "anamnesis"  # anamnesis -> examination -> diagnosis -> treatment

        # Information revealed so far
        self.revealed_info = {
            "main_complaint": False,
            "symptom_details": False,
            "medical_history": False,
            "social_history": False,
            "physical_exam": False
        }

        # Student actions log
        self.student_actions = []

        logger.info(f"AI Patient initialized: {patient_data.get('name', 'Unknown')}")

    def chat(self, student_message: str) -> Dict:
        """
        Process student's question/statement and generate patient response.

        Args:
            student_message: What the student said/asked

        Returns:
            Dict with patient response and metadata
        """
        if not self.llm:
            return {
                "status": "error",
                "error": "LLM not available",
                "response": "Извините, AI-пациент недоступен без LLM модели."
            }

        # Log student action
        self.student_actions.append({
            "timestamp": datetime.now().isoformat(),
            "stage": self.stage,
            "message": student_message
        })

        # Analyze what student is asking about
        intent = self._analyze_intent(student_message)

        # Update revealed information
        self._update_revealed_info(intent)

        # Generate patient response using LLM
        try:
            # Prepare patient context
            patient_context = self._prepare_patient_context()

            # Get AI response
            result = self.llm.virtual_patient_chat(
                patient_info=patient_context,
                student_question=student_message,
                conversation_history=self.conversation_history
            )

            if result["status"] == "success":
                patient_response = result["patient_response"]

                # Add to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": f"Студент: {student_message}"
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": patient_response
                })

                # Analyze response quality
                feedback = self._analyze_student_question(student_message, intent)

                return {
                    "status": "success",
                    "response": patient_response,
                    "intent": intent,
                    "revealed": self.revealed_info.copy(),
                    "feedback": feedback,
                    "stage": self.stage,
                    "metadata": {
                        "tokens": result["metadata"].get("tokens", 0),
                        "time": result["metadata"].get("time_seconds", 0)
                    }
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Unknown error"),
                    "response": "Извините, я не могу ответить прямо сейчас."
                }

        except Exception as e:
            logger.error(f"Error generating patient response: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "response": "Произошла ошибка при генерации ответа."
            }

    def _prepare_patient_context(self) -> Dict:
        """Prepare patient context for LLM."""
        data = self.patient_data

        # Base context
        context = {
            "name": data.get("name", "Пациент"),
            "age": data.get("age", 35),
            "gender": data.get("gender", "мужской"),
            "symptoms": [],
            "history": "",
            "personality": data.get("personality", "спокойный, открытый")
        }

        # Add information based on what's been revealed
        if self.revealed_info["main_complaint"]:
            context["symptoms"] = data.get("chief_complaint", [])

        if self.revealed_info["symptom_details"]:
            context["symptoms"].extend(data.get("symptoms", []))

        if self.revealed_info["medical_history"]:
            context["history"] = data.get("medical_history", "")

        if self.revealed_info["social_history"]:
            social = data.get("social_history", {})
            context["occupation"] = social.get("occupation", "")
            context["smoking"] = social.get("smoking", False)
            context["alcohol"] = social.get("alcohol", False)

        # Current stage specific info
        if self.stage == "examination" and self.revealed_info["physical_exam"]:
            context["physical_findings"] = data.get("physical_exam", {})

        return context

    def _analyze_intent(self, message: str) -> str:
        """Analyze what the student is asking about."""
        message_lower = message.lower()

        # Keywords for different intents
        if any(word in message_lower for word in ["беспокоит", "жалобы", "жалуетесь", "привело"]):
            return "chief_complaint"
        elif any(word in message_lower for word in ["когда", "как долго", "началось", "продолжается"]):
            return "timeline"
        elif any(word in message_lower for word in ["болел", "болезни", "операции", "лечился", "принимаете"]):
            return "medical_history"
        elif any(word in message_lower for word in ["работаете", "курите", "алкоголь", "живете"]):
            return "social_history"
        elif any(word in message_lower for word in ["аллергия", "реакция"]):
            return "allergies"
        elif any(word in message_lower for word in ["осмотр", "послушать", "пощупать", "измерить", "посмотреть"]):
            return "physical_exam"
        elif any(word in message_lower for word in ["анализы", "обследование", "узи", "рентген"]):
            return "diagnostics"
        else:
            return "general"

    def _update_revealed_info(self, intent: str):
        """Update what information has been revealed."""
        mapping = {
            "chief_complaint": "main_complaint",
            "timeline": "symptom_details",
            "medical_history": "medical_history",
            "social_history": "social_history",
            "allergies": "medical_history",
            "physical_exam": "physical_exam"
        }

        if intent in mapping:
            self.revealed_info[mapping[intent]] = True

    def _analyze_student_question(self, message: str, intent: str) -> Dict:
        """Analyze the quality of student's question."""
        feedback = {
            "quality": "good",
            "tips": []
        }

        # Check for open-ended questions (better)
        if message.strip().endswith("?"):
            if any(word in message.lower() for word in ["как", "что", "когда", "где", "почему", "расскажите"]):
                feedback["quality"] = "excellent"
                feedback["tips"].append("Отлично! Открытые вопросы помогают пациенту подробнее рассказать.")
            else:
                # Closed question (yes/no)
                feedback["quality"] = "fair"
                feedback["tips"].append("Попробуй задавать открытые вопросы (как? что? когда?)")

        # Check for medical jargon
        medical_terms = ["диагноз", "патология", "синдром", "симптоматика"]
        if any(term in message.lower() for term in medical_terms):
            feedback["tips"].append("Используй простые слова, понятные пациенту.")

        # Check for empathy
        empathy_words = ["понимаю", "сочувствую", "переживаете", "беспокоитесь"]
        if any(word in message.lower() for word in empathy_words):
            feedback["quality"] = "excellent"
            feedback["tips"].append("Отлично! Эмпатия важна для доверительного контакта.")

        return feedback

    def set_stage(self, stage: str):
        """
        Change consultation stage.

        Stages: anamnesis -> examination -> diagnosis -> treatment
        """
        valid_stages = ["anamnesis", "examination", "diagnosis", "treatment", "completed"]
        if stage in valid_stages:
            self.stage = stage
            logger.info(f"Stage changed to: {stage}")
        else:
            logger.warning(f"Invalid stage: {stage}")

    def get_progress(self) -> Dict:
        """Get current consultation progress."""
        # Calculate completeness
        revealed_count = sum(1 for v in self.revealed_info.values() if v)
        total_info = len(self.revealed_info)
        completeness = (revealed_count / total_info) * 100

        return {
            "stage": self.stage,
            "completeness": round(completeness, 1),
            "revealed_info": self.revealed_info.copy(),
            "questions_asked": len([a for a in self.student_actions if "?" in a["message"]]),
            "total_messages": len(self.student_actions)
        }

    def get_evaluation(self) -> Dict:
        """
        Evaluate student's performance.

        Returns overall score and feedback.
        """
        progress = self.get_progress()

        # Scoring criteria
        score = 0
        max_score = 100
        feedback = []

        # 1. Information gathering (40 points)
        info_score = (progress["completeness"] / 100) * 40
        score += info_score

        if progress["completeness"] >= 80:
            feedback.append("✅ Отлично собрана информация!")
        elif progress["completeness"] >= 60:
            feedback.append("⚠️ Хорошо, но можно узнать больше деталей.")
        else:
            feedback.append("❌ Недостаточно информации для диагноза.")

        # 2. Question quality (30 points)
        open_questions = len([a for a in self.student_actions if any(
            word in a["message"].lower() for word in ["как", "что", "когда", "расскажите"]
        )])
        total_questions = progress["questions_asked"]

        if total_questions > 0:
            quality_ratio = open_questions / total_questions
            quality_score = quality_ratio * 30
            score += quality_score

            if quality_ratio >= 0.7:
                feedback.append("✅ Хорошие открытые вопросы!")
            else:
                feedback.append("💡 Больше открытых вопросов (как? что? когда?)")
        else:
            feedback.append("❌ Нужно задавать вопросы пациенту!")

        # 3. Efficiency (20 points)
        if total_questions > 0:
            efficiency = revealed_count / total_questions
            efficiency_score = min(efficiency * 20, 20)
            score += efficiency_score

            if efficiency >= 0.5:
                feedback.append("✅ Эффективный сбор анамнеза!")
            else:
                feedback.append("💡 Можно быть более целенаправленным.")

        # 4. Empathy (10 points)
        empathy_count = len([a for a in self.student_actions if any(
            word in a["message"].lower() for word in ["понимаю", "переживаете", "беспокоитесь"]
        )])

        if empathy_count > 0:
            score += 10
            feedback.append("✅ Проявлена эмпатия к пациенту!")
        else:
            feedback.append("💡 Покажи понимание и сочувствие.")

        return {
            "score": round(score, 1),
            "max_score": max_score,
            "percentage": round((score / max_score) * 100, 1),
            "feedback": feedback,
            "details": {
                "information_gathered": round(info_score, 1),
                "question_quality": round(quality_score if 'quality_score' in locals() else 0, 1),
                "efficiency": round(efficiency_score if 'efficiency_score' in locals() else 0, 1),
                "empathy": 10 if empathy_count > 0 else 0
            }
        }

    def reset(self):
        """Reset patient for new consultation."""
        self.conversation_history = []
        self.revealed_info = {k: False for k in self.revealed_info}
        self.student_actions = []
        self.stage = "anamnesis"
        logger.info("Patient reset for new consultation")

    def __repr__(self):
        return f"AIPatient({self.patient_data.get('name', 'Unknown')}, stage={self.stage})"
