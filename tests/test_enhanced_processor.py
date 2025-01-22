"""
Tests for enhanced PDF processor.
"""

import unittest
import asyncio
import os
from pathlib import Path
import tempfile
import shutil
from PIL import Image
import numpy as np
import fitz
from core.converter.enhanced_processor import EnhancedProcessor

class TestEnhancedProcessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create temporary directory for test files
        cls.test_dir = Path(tempfile.mkdtemp())
        cls.cache_dir = cls.test_dir / "cache"
        cls.processor = EnhancedProcessor(cache_dir=str(cls.cache_dir))
        
        # Create test PDF
        cls.test_pdf = cls.test_dir / "test.pdf"
        cls._create_test_pdf(cls.test_pdf)
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        shutil.rmtree(cls.test_dir)
        
    @classmethod
    def _create_test_pdf(cls, path: Path):
        """Create a test PDF with various elements."""
        doc = fitz.open()
        page = doc.new_page()
        
        # Add text with different styles
        page.insert_text((50, 50), "Test Document", fontsize=16)
        page.insert_text((50, 100), "Regular text", fontsize=12)
        page.insert_text((150, 100), "Bold text", fontname="helv-b", fontsize=12)
        page.insert_text((250, 100), "Italic text", fontname="helv-o", fontsize=12)
        
        # Add a simple table
        y = 150
        for i in range(3):
            x = 50
            for j in range(3):
                page.draw_rect([x, y, x+50, y+20])
                page.insert_text((x+5, y+15), f"Cell {i},{j}")
                x += 50
            y += 20
            
        # Add a simple diagram
        page.draw_rect([50, 250, 100, 300])
        page.draw_line([100, 275], [150, 275])
        page.draw_circle([175, 275], 25)
        
        # Add reference section
        page.insert_text((50, 350), "References", fontsize=14)
        page.insert_text((50, 380), "1. Test Reference 1", fontsize=10)
        page.insert_text((50, 400), "2. Test Reference 2", fontsize=10)
        
        doc.save(path)
        doc.close()
        
    def setUp(self):
        """Reset caches before each test."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
        os.makedirs(self.cache_dir)
        
    def test_basic_processing(self):
        """Test basic PDF processing."""
        async def _test():
            result = await self.processor.process_document(self.test_pdf)
            self.assertIsNotNone(result)
            self.assertIn("metadata", result)
            self.assertIn("pages", result)
            self.assertTrue(len(result["pages"]) > 0)
            
        asyncio.run(_test())
        
    def test_caching(self):
        """Test PDF processing cache."""
        async def _test():
            # First processing
            start_time = asyncio.get_event_loop().time()
            result1 = await self.processor.process_document(self.test_pdf)
            first_duration = asyncio.get_event_loop().time() - start_time
            
            # Second processing (should use cache)
            start_time = asyncio.get_event_loop().time()
            result2 = await self.processor.process_document(self.test_pdf)
            second_duration = asyncio.get_event_loop().time() - start_time
            
            # Verify cache was used
            self.assertLess(second_duration, first_duration)
            self.assertEqual(result1["metadata"], result2["metadata"])
            
        asyncio.run(_test())
        
    def test_batch_processing(self):
        """Test batch document processing."""
        async def _test():
            # Create additional test PDFs
            pdf_paths = [self.test_pdf]
            for i in range(2):
                path = self.test_dir / f"test{i}.pdf"
                self._create_test_pdf(path)
                pdf_paths.append(path)
                
            results = await self.processor.process_batch(pdf_paths)
            self.assertEqual(len(results), len(pdf_paths))
            for result in results:
                self.assertIsNotNone(result)
                self.assertIn("metadata", result)
                
        asyncio.run(_test())
        
    def test_text_extraction(self):
        """Test text extraction and formatting detection."""
        async def _test():
            result = await self.processor.process_document(self.test_pdf)
            first_page = result["pages"][0]
            
            # Verify text content
            found_title = False
            found_bold = False
            found_italic = False
            
            for block in first_page["blocks"]:
                if block["type"] == "text":
                    if "Test Document" in block["text"]:
                        found_title = True
                    if "Bold text" in block["text"]:
                        found_bold = True
                    if "Italic text" in block["text"]:
                        found_italic = True
                        
            self.assertTrue(found_title)
            self.assertTrue(found_bold)
            self.assertTrue(found_italic)
            
        asyncio.run(_test())
        
    def test_table_detection(self):
        """Test table detection and content extraction."""
        async def _test():
            result = await self.processor.process_document(self.test_pdf)
            self.assertTrue(len(result["tables"]) > 0)
            
            # Verify table structure
            table = result["tables"][0]
            self.assertIn("type", table)
            self.assertEqual(table["type"], "table")
            self.assertIn("content", table)
            self.assertTrue(len(table["content"]) > 0)
            
        asyncio.run(_test())
        
    def test_reference_extraction(self):
        """Test reference extraction."""
        async def _test():
            result = await self.processor.process_document(self.test_pdf)
            references = result["references"]
            
            self.assertTrue(len(references) > 0)
            self.assertTrue(any("Test Reference" in ref["text"] for ref in references))
            
        asyncio.run(_test())
        
    def test_error_handling(self):
        """Test error handling for invalid files."""
        async def _test():
            # Test with non-existent file
            with self.assertRaises(FileNotFoundError):
                await self.processor.process_document("nonexistent.pdf")
                
            # Test with invalid file
            invalid_pdf = self.test_dir / "invalid.pdf"
            with open(invalid_pdf, "w") as f:
                f.write("Not a PDF file")
                
            with self.assertRaises(Exception):
                await self.processor.process_document(invalid_pdf)
                
        asyncio.run(_test())
        
    def test_resource_cleanup(self):
        """Test proper resource cleanup."""
        async def _test():
            # Process file multiple times
            for _ in range(3):
                result = await self.processor.process_document(self.test_pdf)
                self.assertIsNotNone(result)
                
            # Check that temporary files are cleaned up
            temp_files = list(self.test_dir.glob("*.tmp"))
            self.assertEqual(len(temp_files), 0)
            
        asyncio.run(_test())
        
if __name__ == "__main__":
    unittest.main()