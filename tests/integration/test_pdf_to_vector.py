import unittest
import os
from core.converter.pdf_processor import PDFProcessor
from core.storage.vector_store import FAISSVectorStore
from core.modes.mode_manager import ModeManager, Mode

class TestPDFToVector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_pdf = "test_data/sample_medical_text.pdf"
        cls.test_config = "test_config.json"
        cls.mode_manager = ModeManager(cls.test_config)
        cls.pdf_processor = PDFProcessor()
        cls.vector_store = FAISSVectorStore()
        
        # Create test PDF if it doesn't exist
        if not os.path.exists("test_data"):
            os.makedirs("test_data")
        if not os.path.exists(cls.test_pdf):
            # Create a simple PDF for testing
            with open(cls.test_pdf, "w") as f:
                f.write("Sample medical text for testing")
    
    def setUp(self):
        """Reset mode before each test"""
        self.mode_manager.switch_mode(Mode.PRIVATE)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        if os.path.exists(cls.test_pdf):
            os.remove(cls.test_pdf)
        if os.path.exists(cls.test_config):
            os.remove(cls.test_config)
    
    def test_pdf_processing_and_storage(self):
        """Test full pipeline from PDF to vector storage"""
        # Process PDF
        chunks = self.pdf_processor.process_file(self.test_pdf)
        self.assertIsNotNone(chunks)
        self.assertTrue(len(chunks) > 0)
        
        # Store vectors in private mode
        self.mode_manager.switch_mode(Mode.PRIVATE)
        store_id = self.vector_store.add_document(chunks, source=self.test_pdf)
        self.assertIsNotNone(store_id)
        
        # Verify storage in private mode
        results = self.vector_store.search("sample medical", k=1)
        self.assertTrue(len(results) > 0)
        self.assertIn("sample medical", results[0].text.lower())
        
        # Switch to public mode and verify isolation
        self.mode_manager.switch_mode(Mode.PUBLIC)
        public_results = self.vector_store.search("sample medical", k=1)
        self.assertEqual(len(public_results), 0)
    
    def test_mode_specific_storage(self):
        """Test vector storage in different modes"""
        chunks = self.pdf_processor.process_file(self.test_pdf)
        
        # Store in private mode
        self.mode_manager.switch_mode(Mode.PRIVATE)
        private_id = self.vector_store.add_document(chunks, source=self.test_pdf)
        
        # Store in public mode
        self.mode_manager.switch_mode(Mode.PUBLIC)
        public_id = self.vector_store.add_document(chunks, source=self.test_pdf)
        
        # Verify isolation
        self.assertNotEqual(private_id, public_id)
        
        # Check cross-mode visibility
        private_results = self.vector_store.search("sample", k=1, mode=Mode.PRIVATE)
        public_results = self.vector_store.search("sample", k=1, mode=Mode.PUBLIC)
        
        self.assertTrue(len(private_results) > 0)
        self.assertTrue(len(public_results) > 0)
        self.assertNotEqual(private_results[0].id, public_results[0].id)
    
    def test_error_handling(self):
        """Test error handling in the integration pipeline"""
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            self.pdf_processor.process_file("non_existent.pdf")
        
        # Test with empty chunks
        empty_chunks = []
        with self.assertRaises(ValueError):
            self.vector_store.add_document(empty_chunks, source="empty.pdf")
        
        # Test with invalid mode
        with self.assertRaises(ValueError):
            self.vector_store.search("test", mode="INVALID_MODE")

if __name__ == '__main__':
    unittest.main()