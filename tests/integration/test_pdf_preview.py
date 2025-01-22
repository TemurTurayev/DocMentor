import unittest
import os
import streamlit as st
from streamlit.testing.v1 import AppTest
from core.converter.pdf_processor import PDFProcessor
from app.components.pdf_preview import PDFPreview

class TestPDFPreview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.test_pdf = "test_data/sample_preview.pdf"
        cls.pdf_processor = PDFProcessor()
        cls.at = AppTest.from_file("app/main.py")
        
        # Create test PDF if it doesn't exist
        if not os.path.exists("test_data"):
            os.makedirs("test_data")
        if not os.path.exists(cls.test_pdf):
            # Create a simple PDF for testing
            with open(cls.test_pdf, "w") as f:
                f.write("Sample medical text for preview testing")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test files"""
        if os.path.exists(cls.test_pdf):
            os.remove(cls.test_pdf)
    
    def test_pdf_preview_generation(self):
        """Test PDF preview generation"""
        preview = PDFPreview(self.test_pdf)
        
        # Verify preview was generated
        self.assertTrue(preview.is_generated())
        
        # Check preview properties
        self.assertIsNotNone(preview.get_total_pages())
        self.assertGreater(preview.get_total_pages(), 0)
    
    def test_preview_navigation(self):
        """Test PDF preview navigation controls"""
        preview = PDFPreview(self.test_pdf)
        
        # Test page navigation
        self.assertEqual(preview.get_current_page(), 1)
        preview.next_page()
        self.assertEqual(preview.get_current_page(), min(2, preview.get_total_pages()))
        preview.previous_page()
        self.assertEqual(preview.get_current_page(), 1)
    
    def test_preview_caching(self):
        """Test preview caching functionality"""
        preview = PDFPreview(self.test_pdf)
        
        # Initial generation
        first_gen_time = preview.get_generation_time()
        
        # Second generation (should use cache)
        preview2 = PDFPreview(self.test_pdf)
        second_gen_time = preview2.get_generation_time()
        
        # Verify cache was used
        self.assertLess(second_gen_time, first_gen_time)
    
    def test_preview_error_handling(self):
        """Test error handling in preview generation"""
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            PDFPreview("non_existent.pdf")
        
        # Test with invalid PDF
        with open("test_data/invalid.pdf", "w") as f:
            f.write("Invalid PDF content")
        
        with self.assertRaises(ValueError):
            PDFPreview("test_data/invalid.pdf")
        
        # Clean up
        os.remove("test_data/invalid.pdf")
    
    def test_ui_integration(self):
        """Test integration with Streamlit UI"""
        # Initialize preview component
        preview = self.at.select("pdf_preview")
        self.assertIsNotNone(preview)
        
        # Test file upload and preview
        with open(self.test_pdf, "rb") as f:
            content = f.read()
        
        upload = self.at.select("pdf_uploader")
        upload.upload("test.pdf", content)
        
        # Verify preview appears
        preview_container = self.at.select("preview_container")
        self.assertTrue(preview_container.exists())
        
        # Test navigation controls
        next_button = self.at.select("next_page_button")
        prev_button = self.at.select("prev_page_button")
        
        self.assertTrue(next_button.exists())
        self.assertTrue(prev_button.exists())
    
    def test_performance(self):
        """Test preview performance with large files"""
        # Create a larger test PDF
        large_pdf = "test_data/large_sample.pdf"
        with open(large_pdf, "w") as f:
            f.write("Large PDF content\n" * 1000)  # Create larger content
        
        preview = PDFPreview(large_pdf)
        
        # Verify performance metrics
        self.assertLess(preview.get_generation_time(), 5.0)  # Should generate within 5 seconds
        self.assertLess(preview.get_memory_usage(), 100 * 1024 * 1024)  # Should use less than 100MB
        
        # Clean up
        os.remove(large_pdf)

if __name__ == '__main__':
    unittest.main()