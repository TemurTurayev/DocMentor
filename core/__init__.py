"""
DocMentor Core - Простой и понятный AI-ассистент для медицинского образования.
"""

from .docmentor_core import DocMentorCore

# Алиасы для обратной совместимости
LocalMode = DocMentorCore
PrivateMode = DocMentorCore

__version__ = "2.1.0"  # LLM integration
__all__ = ["DocMentorCore", "LocalMode", "PrivateMode"]
