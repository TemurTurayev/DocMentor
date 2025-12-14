"""
DocMentor LLM Module - Local medical language model integration.
Supports GGUF quantized models via llama.cpp for efficient inference on MacBook M4.
"""

from .llm_manager import LLMManager
from .prompt_templates import PromptTemplates
from .rag_pipeline import RAGPipeline

__all__ = ["LLMManager", "PromptTemplates", "RAGPipeline"]
