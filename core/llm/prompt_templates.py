"""
Prompt Templates - Specialized prompts for medical education contexts.
"""

from typing import List, Dict


class PromptTemplates:
    """
    Collection of prompt templates for different medical tasks.
    Optimized for Qwen2.5-7B-Instruct medical reasoning.
    """

    # System prompts
    SYSTEM_MEDICAL_ASSISTANT = """Ты опытный медицинский преподаватель и ассистент для студентов медицинского университета.

Твои задачи:
- Давать точные, научно обоснованные ответы на основе учебников
- Объяснять сложные концепции простым языком
- Использовать медицинскую терминологию, но всегда объяснять термины
- Помогать развивать клиническое мышление
- Указывать на источники информации

Важно:
- Не давай медицинских советов для реальных пациентов
- Всегда подчеркивай, что это образовательный контекст
- При неуверенности - честно признавай это"""

    SYSTEM_VIRTUAL_PATIENT = """Ты виртуальный пациент в образовательной симуляции для студентов-медиков.

Твоя роль:
- Отвечай на вопросы студента как реальный пациент
- Описывай симптомы естественным языком (не медицинскими терминами)
- Будь последовательным в своих ответах
- Проявляй эмоции и переживания пациента
- Не давай диагноз сам - пусть студент его поставит

Стиль общения: разговорный, как обычный человек описывает свое состояние."""

    SYSTEM_EXAM_TUTOR = """Ты преподаватель, проверяющий знания студента-медика.

Твои задачи:
- Задавать вопросы для проверки понимания
- Давать обратную связь на ответы студента
- Объяснять ошибки подробно и конструктивно
- Хвалить правильные ответы
- Помогать понять, а не просто дать правильный ответ

Стиль: строгий но справедливый преподаватель."""

    @staticmethod
    def question_answering(question: str, context_chunks: List[str]) -> List[Dict[str, str]]:
        """
        Template for answering medical questions using RAG.

        Args:
            question: Student's question
            context_chunks: Relevant text chunks from textbooks

        Returns:
            Formatted messages for chat
        """
        # Format context
        context = "\n\n---\n\n".join([
            f"[Фрагмент {i+1}]\n{chunk}"
            for i, chunk in enumerate(context_chunks)
        ])

        user_message = f"""На основе следующих фрагментов из медицинских учебников ответь на вопрос студента.

КОНТЕКСТ ИЗ УЧЕБНИКОВ:
{context}

ВОПРОС СТУДЕНТА:
{question}

ИНСТРУКЦИИ:
1. Используй только информацию из предоставленных фрагментов
2. Дай точный и понятный ответ
3. Объясни сложные термины
4. Если информации недостаточно - честно скажи об этом
5. Структурируй ответ с подзаголовками если нужно

ОТВЕТ:"""

        return [
            {"role": "system", "content": PromptTemplates.SYSTEM_MEDICAL_ASSISTANT},
            {"role": "user", "content": user_message}
        ]

    @staticmethod
    def explain_term(term: str, context: str = "") -> List[Dict[str, str]]:
        """
        Template for explaining medical terminology.

        Args:
            term: Medical term to explain
            context: Optional context from textbooks

        Returns:
            Formatted messages
        """
        user_message = f"""Объясни медицинский термин: **{term}**

{"Контекст из учебника:\n" + context if context else ""}

Объясни:
1. Что это значит простыми словами
2. Этимология (происхождение термина)
3. Синонимы если есть
4. Пример использования в клинической практике

Ответ должен быть понятен студенту 5 курса медицинского университета."""

        return [
            {"role": "system", "content": PromptTemplates.SYSTEM_MEDICAL_ASSISTANT},
            {"role": "user", "content": user_message}
        ]

    @staticmethod
    def virtual_patient_response(
        patient_info: Dict,
        student_question: str,
        conversation_history: List[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Template for virtual patient simulation.

        Args:
            patient_info: Patient data (symptoms, vitals, history)
            student_question: What student asked the patient
            conversation_history: Previous conversation

        Returns:
            Formatted messages
        """
        # Format patient data
        patient_desc = f"""ТЫ ИГРАЕШЬ РОЛЬ ПАЦИЕНТА:
- Имя: {patient_info.get('name', 'Иван')}
- Возраст: {patient_info.get('age', 35)} лет
- Пол: {patient_info.get('gender', 'мужской')}

ТВОИ СИМПТОМЫ:
{chr(10).join(f"- {s}" for s in patient_info.get('symptoms', []))}

ТВОЯ ИСТОРИЯ:
{patient_info.get('history', 'Не указано')}

ВАЖНО: Отвечай как обычный человек, не как врач. Используй разговорный язык."""

        messages = [{"role": "system", "content": PromptTemplates.SYSTEM_VIRTUAL_PATIENT}]

        # Add patient description
        messages.append({"role": "system", "content": patient_desc})

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current question
        messages.append({"role": "user", "content": f"Студент спрашивает: {student_question}"})

        return messages

    @staticmethod
    def differential_diagnosis(
        symptoms: List[str],
        context_chunks: List[str]
    ) -> List[Dict[str, str]]:
        """
        Template for differential diagnosis reasoning.

        Args:
            symptoms: List of symptoms
            context_chunks: Relevant medical knowledge

        Returns:
            Formatted messages
        """
        symptoms_list = "\n".join(f"- {s}" for s in symptoms)
        context = "\n\n---\n\n".join(context_chunks)

        user_message = f"""СИМПТОМЫ ПАЦИЕНТА:
{symptoms_list}

КОНТЕКСТ ИЗ УЧЕБНИКОВ:
{context}

ЗАДАЧА:
Проведи дифференциальную диагностику.

Структура ответа:
1. **Наиболее вероятный диагноз** (с обоснованием)
2. **Дифференциальный ряд** (2-3 альтернативных диагноза)
3. **Необходимые обследования** для подтверждения
4. **"Красные флаги"** - что нельзя пропустить

Рассуждай как опытный клиницист, обучай студента методу мышления."""

        return [
            {"role": "system", "content": PromptTemplates.SYSTEM_MEDICAL_ASSISTANT},
            {"role": "user", "content": user_message}
        ]

    @staticmethod
    def check_answer(
        question: str,
        student_answer: str,
        correct_answer: str
    ) -> List[Dict[str, str]]:
        """
        Template for checking student answers.

        Args:
            question: The question asked
            student_answer: What student answered
            correct_answer: Reference correct answer

        Returns:
            Formatted messages
        """
        user_message = f"""ВОПРОС:
{question}

ОТВЕТ СТУДЕНТА:
{student_answer}

ПРАВИЛЬНЫЙ ОТВЕТ:
{correct_answer}

ЗАДАЧА:
Оцени ответ студента и дай обратную связь.

Структура:
1. **Оценка** (правильно/частично правильно/неправильно)
2. **Что верно** в ответе студента
3. **Что упущено или неверно**
4. **Объяснение** правильного ответа
5. **Советы** для лучшего запоминания

Будь конструктивным и поддерживающим."""

        return [
            {"role": "system", "content": PromptTemplates.SYSTEM_EXAM_TUTOR},
            {"role": "user", "content": user_message}
        ]

    @staticmethod
    def summarize_case(case_data: Dict) -> List[Dict[str, str]]:
        """
        Template for summarizing clinical case.

        Args:
            case_data: Clinical case information

        Returns:
            Formatted messages
        """
        user_message = f"""КЛИНИЧЕСКИЙ СЛУЧАЙ:

Пациент: {case_data.get('name', 'Не указано')}, {case_data.get('age')} лет

Жалобы:
{chr(10).join(f"- {c}" for c in case_data.get('complaints', []))}

Анамнез:
{case_data.get('history', 'Не указано')}

Объективно:
{case_data.get('physical_exam', 'Не указано')}

ЗАДАЧА:
Составь краткое медицинское резюме этого случая для учебных целей.

Структура:
1. **Краткое описание** (2-3 предложения)
2. **Ключевые находки**
3. **Предполагаемый диагноз**
4. **Учебные моменты** (что важно запомнить)"""

        return [
            {"role": "system", "content": PromptTemplates.SYSTEM_MEDICAL_ASSISTANT},
            {"role": "user", "content": user_message}
        ]

    @staticmethod
    def custom_prompt(system_prompt: str, user_prompt: str) -> List[Dict[str, str]]:
        """
        Create custom prompt.

        Args:
            system_prompt: System message
            user_prompt: User message

        Returns:
            Formatted messages
        """
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
