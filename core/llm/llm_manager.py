"""
LLM Manager - Manages local language model inference.
Handles model loading, generation, and resource management.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List
import json

logger = logging.getLogger(__name__)


class LLMManager:
    """
    Manages local LLM inference using llama.cpp.
    Optimized for medical question answering with MacBook M4.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        n_ctx: int = 4096,
        n_threads: int = 8,
        use_metal: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 512
    ):
        """
        Initialize LLM Manager.

        Args:
            model_path: Path to GGUF model file
            n_ctx: Context window size
            n_threads: Number of CPU threads (M4 has 10 cores)
            use_metal: Use Metal acceleration on Apple Silicon
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        """
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.use_metal = use_metal
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm = None
        self._stats = {
            "total_requests": 0,
            "total_tokens_generated": 0,
            "average_tokens_per_second": 0.0
        }

        # Check if llama-cpp-python is installed
        try:
            from llama_cpp import Llama
            self.Llama = Llama
            logger.info("llama-cpp-python is available")
        except ImportError:
            self.Llama = None
            logger.warning("llama-cpp-python not installed. Run: pip install llama-cpp-python")

    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Load GGUF model into memory.

        Args:
            model_path: Path to GGUF model (overrides init path)

        Returns:
            True if successful, False otherwise
        """
        if self.Llama is None:
            logger.error("llama-cpp-python not installed")
            return False

        if model_path:
            self.model_path = model_path

        if not self.model_path:
            logger.error("No model path provided")
            return False

        model_file = Path(self.model_path)
        if not model_file.exists():
            logger.error(f"Model file not found: {self.model_path}")
            return False

        try:
            logger.info(f"Loading model from {self.model_path}...")

            # Configure n_gpu_layers based on Metal support
            n_gpu_layers = 99 if self.use_metal else 0

            self.llm = self.Llama(
                model_path=str(model_file),
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                n_gpu_layers=n_gpu_layers,
                verbose=False
            )

            logger.info("✅ Model loaded successfully!")
            logger.info(f"   Context window: {self.n_ctx}")
            logger.info(f"   Threads: {self.n_threads}")
            logger.info(f"   Metal acceleration: {self.use_metal}")

            return True

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            return False

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stop: Optional[List[str]] = None
    ) -> Dict:
        """
        Generate text from prompt.

        Args:
            prompt: Input prompt
            max_tokens: Override default max_tokens
            temperature: Override default temperature
            stop: Stop sequences

        Returns:
            Dictionary with generated text and metadata
        """
        if self.llm is None:
            return {
                "status": "error",
                "error": "Model not loaded. Call load_model() first.",
                "text": ""
            }

        try:
            import time
            start_time = time.time()

            # Use defaults if not specified
            max_tokens = max_tokens or self.max_tokens
            temperature = temperature or self.temperature

            # Generate
            response = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop or ["User:", "Студент:", "\n\n\n"],
                echo=False
            )

            # Extract text
            generated_text = response['choices'][0]['text'].strip()
            tokens_generated = response['usage']['completion_tokens']

            # Calculate stats
            elapsed = time.time() - start_time
            tokens_per_second = tokens_generated / elapsed if elapsed > 0 else 0

            # Update stats
            self._stats['total_requests'] += 1
            self._stats['total_tokens_generated'] += tokens_generated

            # Running average
            prev_avg = self._stats['average_tokens_per_second']
            n = self._stats['total_requests']
            self._stats['average_tokens_per_second'] = (prev_avg * (n-1) + tokens_per_second) / n

            logger.info(f"Generated {tokens_generated} tokens in {elapsed:.2f}s ({tokens_per_second:.1f} t/s)")

            return {
                "status": "success",
                "text": generated_text,
                "tokens": tokens_generated,
                "time_seconds": elapsed,
                "tokens_per_second": tokens_per_second
            }

        except Exception as e:
            logger.error(f"Generation error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "text": ""
            }

    def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """
        Chat-style generation with message history.

        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            max_tokens: Override default max_tokens
            temperature: Override default temperature

        Returns:
            Dictionary with generated response
        """
        # Format messages into prompt
        prompt = self._format_chat_prompt(messages)

        # Generate
        return self.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages into Qwen2.5 chat format.

        Format:
        <|im_start|>system
        You are a helpful medical assistant.<|im_end|>
        <|im_start|>user
        What is asthma?<|im_end|>
        <|im_start|>assistant
        """
        formatted = ""

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            formatted += f"<|im_start|>{role}\n{content}<|im_end|>\n"

        # Add assistant turn
        formatted += "<|im_start|>assistant\n"

        return formatted

    def get_stats(self) -> Dict:
        """Get generation statistics."""
        return {
            **self._stats,
            "model_loaded": self.llm is not None,
            "model_path": self.model_path
        }

    def is_available(self) -> bool:
        """Check if LLM is ready for inference."""
        return self.llm is not None

    def unload_model(self):
        """Unload model from memory."""
        if self.llm:
            del self.llm
            self.llm = None
            logger.info("Model unloaded from memory")

    def __repr__(self):
        status = "loaded" if self.llm else "not loaded"
        return f"LLMManager(model={status}, requests={self._stats['total_requests']})"
