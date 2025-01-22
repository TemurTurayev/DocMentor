"""
Pytest configuration and fixtures.
"""
import pytest
import tempfile
from pathlib import Path
import shutil
from core.modes import PrivateMode, PublicMode

@pytest.fixture(scope="function")
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    shutil.rmtree(temp_path)

@pytest.fixture(scope="function")
def private_mode(temp_dir):
    """Initialize private mode with temporary storage."""
    mode = PrivateMode(storage_path=temp_dir / "private")
    yield mode

@pytest.fixture(scope="function")
def public_mode(temp_dir):
    """Initialize public mode with temporary storage."""
    mode = PublicMode(storage_path=temp_dir / "public")
    yield mode

@pytest.fixture(scope="session")
def test_pdf_path():
    """Path to test PDF file."""
    return Path(__file__).parent / "data" / "test.pdf"