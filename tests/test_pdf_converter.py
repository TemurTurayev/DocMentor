"""
Tests for PDF converter functionality.
"""
import pytest
from pathlib import Path
import tempfile
import os

def test_pdf_extraction(test_pdf_path):
    """Test basic PDF text extraction."""
    from advanced_medical_pdf_converter import process_medical_pdf
    
    # Process test PDF
    result = process_medical_pdf(str(test_pdf_path))
    
    # Basic checks
    assert result is not None
    assert "chunks" in result
    assert len(result["chunks"]) > 0
    assert "metadata" in result
    
def test_chunking_consistency(test_pdf_path):
    """Test that chunking is consistent."""
    from advanced_medical_pdf_converter import process_medical_pdf
    
    # Process same PDF twice
    result1 = process_medical_pdf(str(test_pdf_path))
    result2 = process_medical_pdf(str(test_pdf_path))
    
    # Check consistency
    assert len(result1["chunks"]) == len(result2["chunks"])
    for chunk1, chunk2 in zip(result1["chunks"], result2["chunks"]):
        assert chunk1 == chunk2
        
def test_metadata_extraction(test_pdf_path):
    """Test PDF metadata extraction."""
    from advanced_medical_pdf_converter import process_medical_pdf
    
    result = process_medical_pdf(str(test_pdf_path))
    
    # Check metadata fields
    assert "metadata" in result
    metadata = result["metadata"]
    assert "title" in metadata
    assert "total_pages" in metadata
    assert isinstance(metadata["total_pages"], int)
    assert metadata["total_pages"] > 0
    
def test_large_pdf_handling(test_pdf_path):
    """Test handling of larger PDFs."""
    from advanced_medical_pdf_converter import process_medical_pdf
    import psutil
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Process PDF
    result = process_medical_pdf(str(test_pdf_path))
    
    # Check memory usage
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable (less than 500MB)
    assert memory_increase < 500 * 1024 * 1024  # 500MB in bytes
    
def test_error_handling():
    """Test error handling for invalid PDFs."""
    from advanced_medical_pdf_converter import process_medical_pdf
    import pytest
    
    # Create invalid PDF file
    with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
        temp_file.write(b"This is not a valid PDF")
        temp_file.flush()
        
        # Should raise an exception for invalid PDF
        with pytest.raises(Exception):
            process_medical_pdf(temp_file.name)