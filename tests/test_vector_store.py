"""
Tests for FAISS vector store functionality.
"""
import pytest
from pathlib import Path
from core.vector_store import FAISSStore

def test_store_initialization(temp_dir):
    """Test vector store initialization."""
    store = FAISSStore()
    assert store is not None
    assert store.dimension == 768  # Default dimension for DistilBERT
    
def test_add_and_search(temp_dir):
    """Test adding texts and searching."""
    store = FAISSStore()
    
    # Test texts
    texts = [
        "Бронхиальная астма - это хроническое воспалительное заболевание дыхательных путей",
        "Основные симптомы астмы включают кашель, одышку и свистящее дыхание",
        "Лечение астмы направлено на контроль воспаления и предотвращение обострений"
    ]
    
    metadata = [{"source": f"test_{i}"} for i in range(len(texts))]
    
    # Add texts
    store.add_texts(texts, metadata)
    
    # Search
    query = "Каковы симптомы астмы?"
    results = store.similarity_search(query, k=2)
    
    assert len(results) == 2
    assert any("симптомы" in result[0] for result in results)
    
def test_metadata_filtering(temp_dir):
    """Test metadata filtering in search."""
    store = FAISSStore()
    
    # Add texts with different metadata
    texts = [
        "Симптомы простуды включают насморк и боль в горле",
        "Симптомы гриппа включают высокую температуру",
    ]
    
    metadata = [
        {"disease": "cold"},
        {"disease": "flu"}
    ]
    
    store.add_texts(texts, metadata)
    
    # Search with filter
    results = store.similarity_search(
        "Какие симптомы?",
        k=1,
        filter_dict={"disease": "flu"}
    )
    
    assert len(results) == 1
    assert "грипп" in results[0][0].lower()
    
def test_save_and_load(temp_dir):
    """Test saving and loading the vector store."""
    store = FAISSStore()
    
    # Add some texts
    texts = ["Текст для теста сохранения и загрузки"]
    store.add_texts(texts)
    
    # Save
    save_path = temp_dir / "test_store"
    store.save_local(str(save_path))
    
    # Load
    loaded_store = FAISSStore.load_local(str(save_path))
    
    # Search in both stores
    query = "тест"
    original_results = store.similarity_search(query, k=1)
    loaded_results = loaded_store.similarity_search(query, k=1)
    
    assert len(original_results) == len(loaded_results)
    assert original_results[0][0] == loaded_results[0][0]
    
def test_batch_processing(temp_dir):
    """Test batch processing of texts."""
    store = FAISSStore()
    
    # Create large number of texts
    texts = [f"Тестовый текст номер {i}" for i in range(100)]
    
    # Add with small batch size
    store.add_texts(texts, batch_size=10)
    
    # Verify all texts are searchable
    results = store.similarity_search("тестовый", k=100)
    assert len(results) == 100
    
def test_error_handling(temp_dir):
    """Test error handling."""
    store = FAISSStore()
    
    # Test empty input
    with pytest.raises(ValueError):
        store.add_texts([], [{"metadata": "test"}])
    
    # Test mismatched metadata length
    with pytest.raises(ValueError):
        store.add_texts(["text1", "text2"], [{"metadata": "test"}])
        
    # Test invalid save path
    with pytest.raises(Exception):
        store.save_local("/nonexistent/path/store")