"""
RAG Pipeline - Retrieval-Augmented Generation for medical Q&A.
Combines vector search with LLM generation for accurate, grounded answers.
"""

import logging
from typing import List, Dict, Optional
from .llm_manager import LLMManager
from .prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    RAG (Retrieval-Augmented Generation) Pipeline.

    Flow:
    1. Student asks question
    2. Search relevant chunks in vector DB (retrieval)
    3. Create prompt with context (augmentation)
    4. Generate answer with LLM (generation)
    """

    def __init__(
        self,
        llm_manager: LLMManager,
        vector_store=None,
        top_k: int = 3,
        min_score: float = 0.5
    ):
        """
        Initialize RAG Pipeline.

        Args:
            llm_manager: LLM manager instance
            vector_store: Vector store for retrieval (DocMentorCore.vector_store)
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score for chunks
        """
        self.llm = llm_manager
        self.vector_store = vector_store
        self.top_k = top_k
        self.min_score = min_score

    def answer_question(
        self,
        question: str,
        use_context: bool = True,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict:
        """
        Answer medical question using RAG.

        Args:
            question: Student's question
            use_context: Whether to use retrieved context (if False, just LLM)
            max_tokens: Max tokens to generate
            temperature: Sampling temperature

        Returns:
            Dictionary with answer, sources, and metadata
        """
        if not self.llm.is_available():
            return {
                "status": "error",
                "error": "LLM not loaded",
                "answer": "",
                "sources": []
            }

        # Step 1: Retrieve context
        context_chunks = []
        sources = []

        if use_context and self.vector_store:
            try:
                # Search vector store
                results = self.vector_store.similarity_search(
                    query=question,
                    k=self.top_k
                )

                # Filter by score
                for text, metadata, score in results:
                    if score >= self.min_score:
                        context_chunks.append(text)
                        sources.append({
                            "text": text[:200] + "..." if len(text) > 200 else text,
                            "metadata": metadata,
                            "score": float(score)
                        })

                logger.info(f"Retrieved {len(context_chunks)} relevant chunks")

            except Exception as e:
                logger.error(f"Retrieval error: {str(e)}")
                # Continue without context

        # Step 2: Create prompt
        if context_chunks:
            messages = PromptTemplates.question_answering(question, context_chunks)
        else:
            # No context - direct question
            messages = [
                {"role": "system", "content": PromptTemplates.SYSTEM_MEDICAL_ASSISTANT},
                {"role": "user", "content": f"Ответь на вопрос студента-медика: {question}"}
            ]

        # Step 3: Generate answer
        response = self.llm.chat(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        if response["status"] == "success":
            return {
                "status": "success",
                "answer": response["text"],
                "sources": sources,
                "metadata": {
                    "tokens": response["tokens"],
                    "time_seconds": response["time_seconds"],
                    "tokens_per_second": response["tokens_per_second"],
                    "used_context": len(context_chunks) > 0
                }
            }
        else:
            return {
                "status": "error",
                "error": response.get("error", "Unknown error"),
                "answer": "",
                "sources": []
            }

    def explain_term(self, term: str) -> Dict:
        """
        Explain medical term using RAG.

        Args:
            term: Medical term to explain

        Returns:
            Dictionary with explanation
        """
        if not self.llm.is_available():
            return {"status": "error", "error": "LLM not loaded"}

        # Try to find context
        context = ""
        if self.vector_store:
            try:
                results = self.vector_store.similarity_search(query=term, k=1)
                if results:
                    context = results[0][0]  # First chunk text
            except Exception as e:
                logger.error(f"Context retrieval error: {str(e)}")

        # Generate explanation
        messages = PromptTemplates.explain_term(term, context)
        response = self.llm.chat(messages=messages, max_tokens=400)

        if response["status"] == "success":
            return {
                "status": "success",
                "explanation": response["text"],
                "metadata": {
                    "tokens": response["tokens"],
                    "time_seconds": response["time_seconds"]
                }
            }
        else:
            return {"status": "error", "error": response.get("error", "Unknown error")}

    def differential_diagnosis(self, symptoms: List[str]) -> Dict:
        """
        Generate differential diagnosis based on symptoms.

        Args:
            symptoms: List of patient symptoms

        Returns:
            Dictionary with differential diagnosis
        """
        if not self.llm.is_available():
            return {"status": "error", "error": "LLM not loaded"}

        # Retrieve relevant medical knowledge
        context_chunks = []
        if self.vector_store:
            try:
                # Search for each symptom
                for symptom in symptoms[:3]:  # Limit to avoid too many searches
                    results = self.vector_store.similarity_search(query=symptom, k=2)
                    for text, _, score in results:
                        if score >= self.min_score:
                            context_chunks.append(text)

                # Remove duplicates
                context_chunks = list(set(context_chunks))[:5]  # Max 5 chunks

            except Exception as e:
                logger.error(f"Context retrieval error: {str(e)}")

        # Generate differential
        messages = PromptTemplates.differential_diagnosis(symptoms, context_chunks)
        response = self.llm.chat(messages=messages, max_tokens=600, temperature=0.5)

        if response["status"] == "success":
            return {
                "status": "success",
                "diagnosis": response["text"],
                "metadata": {
                    "tokens": response["tokens"],
                    "time_seconds": response["time_seconds"]
                }
            }
        else:
            return {"status": "error", "error": response.get("error", "Unknown error")}

    def virtual_patient_chat(
        self,
        patient_info: Dict,
        student_question: str,
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Simulate conversation with virtual patient.

        Args:
            patient_info: Patient data
            student_question: Student's question to patient
            conversation_history: Previous conversation

        Returns:
            Dictionary with patient's response
        """
        if not self.llm.is_available():
            return {"status": "error", "error": "LLM not loaded"}

        messages = PromptTemplates.virtual_patient_response(
            patient_info=patient_info,
            student_question=student_question,
            conversation_history=conversation_history or []
        )

        response = self.llm.chat(
            messages=messages,
            max_tokens=300,
            temperature=0.8  # Higher for more natural conversation
        )

        if response["status"] == "success":
            return {
                "status": "success",
                "patient_response": response["text"],
                "metadata": {
                    "tokens": response["tokens"],
                    "time_seconds": response["time_seconds"]
                }
            }
        else:
            return {"status": "error", "error": response.get("error", "Unknown error")}

    def check_student_answer(
        self,
        question: str,
        student_answer: str,
        correct_answer: str
    ) -> Dict:
        """
        Check and provide feedback on student's answer.

        Args:
            question: The question
            student_answer: Student's answer
            correct_answer: Reference answer

        Returns:
            Dictionary with feedback
        """
        if not self.llm.is_available():
            return {"status": "error", "error": "LLM not loaded"}

        messages = PromptTemplates.check_answer(
            question=question,
            student_answer=student_answer,
            correct_answer=correct_answer
        )

        response = self.llm.chat(messages=messages, max_tokens=500, temperature=0.6)

        if response["status"] == "success":
            return {
                "status": "success",
                "feedback": response["text"],
                "metadata": {
                    "tokens": response["tokens"],
                    "time_seconds": response["time_seconds"]
                }
            }
        else:
            return {"status": "error", "error": response.get("error", "Unknown error")}

    def set_vector_store(self, vector_store):
        """Update vector store reference."""
        self.vector_store = vector_store
        logger.info("Vector store updated in RAG pipeline")

    def __repr__(self):
        llm_status = "ready" if self.llm.is_available() else "not ready"
        vs_status = "connected" if self.vector_store else "not connected"
        return f"RAGPipeline(llm={llm_status}, vector_store={vs_status}, top_k={self.top_k})"
