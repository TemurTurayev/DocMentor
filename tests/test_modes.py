"""
Tests for mode system functionality.
"""
import pytest
from pathlib import Path
import shutil
from core.modes import PrivateMode, PublicMode

def test_private_mode_initialization(temp_dir):
    """Test private mode initialization."""
    mode = PrivateMode(storage_path=temp_dir / "private")
    assert mode.storage_path.exists()
    assert (mode.storage_path / "vector_store").exists()
    
def test_public_mode_initialization(temp_dir):
    """Test public mode initialization."""
    mode = PublicMode(storage_path=temp_dir / "public")
    assert mode.storage_path.exists()
    assert (mode.storage_path / "vector_store").exists()
    
def test_document_processing(private_mode, test_pdf_path):
    """Test document processing in private mode."""
    result = private_mode.process_document(
        test_pdf_path,
        metadata={"test": True}
    )
    
    assert result["status"] == "success"
    assert result["chunks"] > 0
    assert result["metadata"]["mode"] == "private"
    assert result["metadata"]["test"] is True
    
def test_search_functionality(private_mode, test_pdf_path):
    """Test search functionality."""
    # First add a document
    private_mode.process_document(test_pdf_path)
    
    # Perform search
    results = private_mode.search("test query", k=2)
    
    assert isinstance(results, list)
    assert len(results) <= 2
    for result in results:
        assert "text" in result
        assert "metadata" in result
        assert "score" in result
        
def test_mode_separation(temp_dir):
    """Test separation between private and public modes."""
    private_mode = PrivateMode(storage_path=temp_dir / "private")
    public_mode = PublicMode(storage_path=temp_dir / "public")
    
    # Process same document in both modes
    test_file = Path(__file__).parent / "data" / "test.pdf"
    
    private_result = private_mode.process_document(test_file)
    public_result = public_mode.process_document(test_file)
    
    # Check storage separation
    private_docs = list((temp_dir / "private" / "documents").glob("*.pdf"))
    public_docs = list((temp_dir / "public" / "documents").glob("*.pdf"))
    
    assert len(private_docs) == 1
    assert len(public_docs) == 1
    assert private_docs[0] != public_docs[0]
    
def test_metadata_handling(private_mode, test_pdf_path):
    """Test metadata handling in modes."""
    # Process with custom metadata
    custom_metadata = {
        "author": "Test Author",
        "subject": "Medicine",
        "tags": ["test", "medical"]
    }
    
    result = private_mode.process_document(
        test_pdf_path,
        metadata=custom_metadata
    )
    
    # Check metadata preservation
    assert result["metadata"]["author"] == "Test Author"
    assert result["metadata"]["subject"] == "Medicine"
    assert "test" in result["metadata"]["tags"]
    
    # Search with metadata filter
    search_results = private_mode.search(
        "test",
        filter_dict={"author": "Test Author"}
    )
    
    assert len(search_results) > 0
    assert all(r["metadata"]["author"] == "Test Author" for r in search_results)
    
def test_error_handling(private_mode):
    """Test error handling in modes."""
    # Test with non-existent file
    with pytest.raises(Exception):
        private_mode.process_document("nonexistent.pdf")
        
    # Test with invalid metadata
    with pytest.raises(Exception):
        private_mode.process_document(
            test_pdf_path,
            metadata="invalid"  # Should be dict
        )
        
def test_mode_persistence(temp_dir):
    """Test mode state persistence."""
    mode_path = temp_dir / "test_mode"
    
    # Create and use mode
    mode1 = PrivateMode(storage_path=mode_path)
    mode1.process_document(Path(__file__).parent / "data" / "test.pdf")
    
    # Create new instance with same path
    mode2 = PrivateMode(storage_path=mode_path)
    
    # Search should work in new instance
    results = mode2.search("test")
    assert len(results) > 0