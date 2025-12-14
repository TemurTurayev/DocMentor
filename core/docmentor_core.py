"""
DocMentor Core - Единый движок для работы с медицинскими документами и AI-ассистентом.
Простая и понятная реализация без избыточной сложности.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
import shutil

from .vector_store import FAISSStore

logger = logging.getLogger(__name__)

# LLM imports (optional - only if llama-cpp-python is installed)
try:
    from .llm import LLMManager, RAGPipeline
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.info("LLM module not available. Install llama-cpp-python for AI features.")


class DocMentorCore:
    """
    Основной класс DocMentor.
    Управляет документами, поиском и AI-ассистентом.
    """

    def __init__(
        self,
        storage_path: Union[str, Path] = "./data",
        model_name: str = "distilbert-base-multilingual-cased",
        llm_model_path: Optional[str] = None,
        enable_llm: bool = True
    ):
        """
        Инициализация DocMentor.

        Args:
            storage_path: Путь для хранения данных
            model_name: Название модели для эмбеддингов
            llm_model_path: Путь к GGUF модели (опционально)
            enable_llm: Включить LLM функции (если доступны)
        """
        self.storage_path = Path(storage_path)
        self.model_name = model_name
        self.vector_store = self._initialize_vector_store()

        # LLM integration
        self.llm_manager = None
        self.rag_pipeline = None

        if enable_llm and LLM_AVAILABLE:
            self._initialize_llm(llm_model_path)

        logger.info(f"DocMentor initialized at {self.storage_path}")

    def _initialize_vector_store(self) -> FAISSStore:
        """Инициализация векторного хранилища."""
        store_path = self.storage_path / "vector_store"

        if store_path.exists():
            logger.info(f"Loading existing vector store from {store_path}")
            try:
                return FAISSStore.load_local(str(store_path), self.model_name)
            except Exception as e:
                logger.warning(f"Failed to load vector store: {e}. Creating new one.")

        logger.info("Creating new vector store")
        store = FAISSStore(model_name=self.model_name)

        # Create directory and save empty store
        store_path.mkdir(parents=True, exist_ok=True)
        store.save_local(str(store_path))

        return store

    def process_document(
        self,
        file_path: Union[str, Path],
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Обработка PDF документа.

        Args:
            file_path: Путь к PDF файлу
            metadata: Дополнительные метаданные

        Returns:
            Результат обработки (количество фрагментов, метаданные)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if metadata is None:
            metadata = {}

        # Добавляем базовые метаданные
        metadata.update({
            "filename": file_path.name,
            "source": "user_upload"
        })

        # Копируем документ в хранилище
        doc_storage = self.storage_path / "documents"
        doc_storage.mkdir(parents=True, exist_ok=True)

        target_path = doc_storage / file_path.name
        if not target_path.exists():
            shutil.copy2(file_path, target_path)
            logger.info(f"Document copied to {target_path}")

        # Обрабатываем документ
        try:
            from .converter.enhanced_processor import EnhancedProcessor

            processor = EnhancedProcessor(cache_dir=str(self.storage_path / "cache"))

            # Обработка асинхронного метода синхронно
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            doc_data = loop.run_until_complete(
                processor.process_document(target_path, use_cache=True)
            )

            # Извлекаем текстовые фрагменты
            chunks = []
            for page_data in doc_data.get("pages", []):
                text = page_data.get("text", "").strip()
                if text:
                    chunks.append(text)

            if not chunks:
                raise ValueError("No text content extracted from document")

            # Обновляем метаданные
            metadata.update({
                "title": doc_data.get("metadata", {}).get("title", file_path.name),
                "total_pages": len(doc_data.get("pages", [])),
                "author": doc_data.get("metadata", {}).get("author", ""),
            })

            # Добавляем в векторное хранилище
            chunk_metadata = [metadata.copy() for _ in chunks]
            self.vector_store.add_texts(chunks, chunk_metadata)
            self.save()

            logger.info(f"Successfully processed {file_path.name}: {len(chunks)} chunks")

            return {
                "status": "success",
                "filename": file_path.name,
                "chunks": len(chunks),
                "metadata": metadata
            }

        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise

    def search(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Поиск по базе знаний.

        Args:
            query: Поисковый запрос
            k: Количество результатов
            filter_dict: Фильтры по метаданным

        Returns:
            Список найденных фрагментов с метаданными
        """
        try:
            # Выполняем поиск
            results = self.vector_store.similarity_search(query, k=k, filter_dict=filter_dict)

            # Форматируем результаты
            formatted_results = []
            for text, metadata, score in results:
                formatted_results.append({
                    "text": text,
                    "metadata": metadata,
                    "score": float(score),
                    "source": metadata.get("filename", "Unknown")
                })

            logger.info(f"Search '{query}' returned {len(formatted_results)} results")
            return formatted_results

        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise

    def get_documents(self) -> List[Dict]:
        """
        Получить список загруженных документов.

        Returns:
            Список документов с метаданными
        """
        doc_storage = self.storage_path / "documents"
        if not doc_storage.exists():
            return []

        documents = []
        for file_path in doc_storage.glob("*.pdf"):
            try:
                doc_info = {
                    "filename": file_path.name,
                    "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                    "path": str(file_path)
                }
                documents.append(doc_info)
            except Exception as e:
                logger.error(f"Error getting info for {file_path}: {str(e)}")
                continue

        return documents

    def get_stats(self) -> Dict:
        """
        Получить статистику системы.

        Returns:
            Статистика (количество документов, фрагментов и т.д.)
        """
        return {
            "total_documents": len(self.get_documents()),
            "total_chunks": len(self.vector_store.texts),
            "storage_path": str(self.storage_path),
            "model_name": self.model_name
        }

    def clear_cache(self):
        """Очистить кэш обработанных документов."""
        cache_path = self.storage_path / "cache"
        if cache_path.exists():
            import shutil
            shutil.rmtree(cache_path)
            cache_path.mkdir(parents=True, exist_ok=True)
            logger.info("Cache cleared")

    def save(self):
        """Сохранить текущее состояние векторного хранилища."""
        store_path = self.storage_path / "vector_store"
        self.vector_store.save_local(str(store_path))
        logger.info(f"Vector store saved to {store_path}")

    # ==================== LLM Methods ====================

    def _initialize_llm(self, model_path: Optional[str] = None):
        """
        Инициализация LLM.

        Args:
            model_path: Путь к GGUF модели
        """
        if not LLM_AVAILABLE:
            logger.warning("LLM not available")
            return

        try:
            # Auto-detect model if not provided
            if not model_path:
                models_dir = Path("./models")
                if models_dir.exists():
                    gguf_files = list(models_dir.glob("*.gguf"))
                    if gguf_files:
                        model_path = str(gguf_files[0])
                        logger.info(f"Auto-detected model: {model_path}")

            if model_path and Path(model_path).exists():
                self.llm_manager = LLMManager(
                    model_path=model_path,
                    n_ctx=4096,
                    n_threads=8,
                    use_metal=True
                )

                # Load model
                if self.llm_manager.load_model():
                    # Create RAG pipeline
                    self.rag_pipeline = RAGPipeline(
                        llm_manager=self.llm_manager,
                        vector_store=self.vector_store
                    )
                    logger.info("✅ LLM initialized successfully")
                else:
                    logger.warning("Failed to load LLM model")
                    self.llm_manager = None
            else:
                logger.info("No LLM model found. Run: python setup_llm.py")

        except Exception as e:
            logger.error(f"LLM initialization error: {str(e)}")
            self.llm_manager = None
            self.rag_pipeline = None

    def ask_ai(
        self,
        question: str,
        use_context: bool = True,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict:
        """
        Задать вопрос AI ассистенту (с RAG).

        Args:
            question: Вопрос студента
            use_context: Использовать контекст из учебников
            max_tokens: Максимум токенов в ответе
            temperature: Температура генерации (0.0-1.0)

        Returns:
            Словарь с ответом и метаданными
        """
        if not self.rag_pipeline:
            return {
                "status": "error",
                "error": "LLM not available. Run: python setup_llm.py",
                "answer": ""
            }

        return self.rag_pipeline.answer_question(
            question=question,
            use_context=use_context,
            max_tokens=max_tokens,
            temperature=temperature
        )

    def explain_term(self, term: str) -> Dict:
        """
        Объяснить медицинский термин через AI.

        Args:
            term: Медицинский термин

        Returns:
            Словарь с объяснением
        """
        if not self.rag_pipeline:
            return {"status": "error", "error": "LLM not available"}

        return self.rag_pipeline.explain_term(term)

    def is_llm_available(self) -> bool:
        """Проверить, доступен ли LLM."""
        return self.llm_manager is not None and self.llm_manager.is_available()

    def get_llm_stats(self) -> Dict:
        """Получить статистику LLM."""
        if self.llm_manager:
            return self.llm_manager.get_stats()
        return {"model_loaded": False}

    def __repr__(self):
        stats = self.get_stats()
        llm_status = "✓" if self.is_llm_available() else "✗"
        return f"DocMentorCore(documents={stats['total_documents']}, chunks={stats['total_chunks']}, LLM={llm_status})"


# Для обратной совместимости
LocalMode = DocMentorCore
PrivateMode = DocMentorCore
