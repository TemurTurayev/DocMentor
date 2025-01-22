"""
Enhanced PDF processor with async support and caching.
Integrates features from advanced-medical-pdf-converter.
"""

import os
import asyncio
import fitz  # PyMuPDF
from typing import List, Dict, Optional, Union
from pathlib import Path
import numpy as np
from PIL import Image
import io
import logging
from concurrent.futures import ThreadPoolExecutor
from ..utils.cache_manager import CacheManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedProcessor:
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize enhanced PDF processor.
        
        Args:
            cache_dir: Directory for caching processed documents
        """
        self.cache_manager = CacheManager(cache_dir)
        self.executor = ThreadPoolExecutor(max_workers=os.cpu_count())
        
    async def process_document(self, file_path: Union[str, Path], 
                             use_cache: bool = True) -> Dict:
        """
        Process PDF document asynchronously.
        
        Args:
            file_path: Path to PDF file
            use_cache: Whether to use cache
            
        Returns:
            Dictionary with processed content
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Check cache first
        if use_cache:
            file_hash = self._compute_file_hash(file_path)
            cached = self.cache_manager.get(file_hash)
            if cached is not None:
                logger.info(f"Using cached version of {file_path}")
                return cached
                
        # Process in thread pool
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self.executor, 
                self._process_pdf,
                file_path
            )
            
            # Cache result
            if use_cache:
                self.cache_manager.put(
                    file_hash,
                    result,
                    metadata={"filename": file_path.name}
                )
                
            return result
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            raise
            
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute hash of file for caching."""
        with open(file_path, 'rb') as f:
            return self.cache_manager._compute_hash(f.read())
            
    def _process_pdf(self, file_path: Path) -> Dict:
        """
        Process PDF file and extract content.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with processed content
        """
        doc = fitz.open(file_path)
        
        content = {
            "metadata": self._extract_metadata(doc),
            "pages": [],
            "images": [],
            "tables": [],
            "references": []
        }
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_content = self._process_page(page)
            content["pages"].append(page_content)
            
            # Extract images
            images = self._extract_images(page)
            content["images"].extend(images)
            
            # Extract tables (basic heuristic)
            tables = self._extract_tables(page)
            content["tables"].extend(tables)
            
        # Extract references (if available)
        content["references"] = self._extract_references(doc)
        
        doc.close()
        return content
        
    def _extract_metadata(self, doc: fitz.Document) -> Dict:
        """Extract PDF metadata."""
        metadata = doc.metadata
        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "page_count": len(doc),
            "format": "PDF"
        }
        
    def _process_page(self, page: fitz.Page) -> Dict:
        """
        Process single PDF page.
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            Dictionary with page content
        """
        # Extract text with formatting
        blocks = page.get_text("dict")["blocks"]
        processed_blocks = []
        
        for block in blocks:
            if block["type"] == 0:  # Text block
                text_block = {
                    "type": "text",
                    "text": "",
                    "font": None,
                    "size": None,
                    "flags": [],
                    "bbox": block["bbox"]
                }
                
                # Process spans
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_block["text"] += span["text"] + " "
                        text_block["font"] = span["font"]
                        text_block["size"] = span["size"]
                        text_block["flags"] = self._parse_font_flags(span["flags"])
                        
                text_block["text"] = text_block["text"].strip()
                processed_blocks.append(text_block)
                
            elif block["type"] == 1:  # Image block
                processed_blocks.append({
                    "type": "image",
                    "bbox": block["bbox"]
                })
                
        return {
            "number": page.number + 1,
            "blocks": processed_blocks,
            "size": {"width": page.rect.width, "height": page.rect.height}
        }
        
    def _extract_images(self, page: fitz.Page) -> List[Dict]:
        """Extract images from page with metadata."""
        images = []
        
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            
            if base_image:
                image_data = {
                    "data": base_image["image"],
                    "size": base_image["size"],
                    "colorspace": base_image["colorspace"],
                    "page": page.number + 1,
                    "index": img_index
                }
                
                # Check if image looks like a diagram or chart
                is_diagram = self._check_if_diagram(Image.open(io.BytesIO(base_image["image"])))
                if is_diagram:
                    image_data["type"] = "diagram"
                else:
                    image_data["type"] = "photo"
                    
                images.append(image_data)
                
        return images
        
    def _check_if_diagram(self, img: Image.Image) -> bool:
        """
        Basic heuristic to check if image is likely a diagram.
        Checks for limited color palette and straight lines.
        """
        # Convert to numpy array
        img_array = np.array(img.convert('RGB'))
        
        # Check color diversity
        colors = np.unique(img_array.reshape(-1, 3), axis=0)
        if len(colors) < 50:  # Limited palette suggests diagram
            return True
            
        return False
        
    def _extract_tables(self, page: fitz.Page) -> List[Dict]:
        """
        Basic table detection heuristic.
        Looks for grid-like structures in the page.
        """
        tables = []
        # Get page's drawings (including lines)
        paths = page.get_drawings()
        
        # Look for rectangular shapes formed by lines
        horizontal_lines = []
        vertical_lines = []
        
        for path in paths:
            if path["type"] == "l":  # Line
                p1 = path["pts"][0]
                p2 = path["pts"][1]
                
                if abs(p1.y - p2.y) < 1:  # Horizontal line
                    horizontal_lines.append((min(p1.x, p2.x), max(p1.x, p2.x), p1.y))
                elif abs(p1.x - p2.x) < 1:  # Vertical line
                    vertical_lines.append((min(p1.y, p2.y), max(p1.y, p2.y), p1.x))
        
        # Find potential table regions
        if len(horizontal_lines) >= 2 and len(vertical_lines) >= 2:
            # Sort lines
            horizontal_lines.sort(key=lambda x: x[2])
            vertical_lines.sort(key=lambda x: x[2])
            
            # Find table boundaries
            for i in range(len(horizontal_lines) - 1):
                for j in range(len(vertical_lines) - 1):
                    table = {
                        "type": "table",
                        "bbox": (
                            vertical_lines[j][2],
                            horizontal_lines[i][2],
                            vertical_lines[j+1][2],
                            horizontal_lines[i+1][2]
                        ),
                        "page": page.number + 1
                    }
                    
                    # Extract table content
                    table["content"] = self._extract_table_content(page, table["bbox"])
                    tables.append(table)
        
        return tables
        
    def _extract_table_content(self, page: fitz.Page, bbox: tuple) -> List[List[str]]:
        """Extract text content from table region."""
        content = []
        words = page.get_text("words", clip=bbox)
        
        if not words:
            return content
            
        # Group words into rows based on y-coordinate
        tolerance = 5  # Pixels tolerance for same row
        current_row = []
        current_y = words[0][3]  # Bottom y-coordinate of first word
        
        for word in words:
            if abs(word[3] - current_y) > tolerance:
                # New row
                current_row.sort(key=lambda x: x[0])  # Sort by x-coordinate
                content.append([w[4] for w in current_row])
                current_row = [word]
                current_y = word[3]
            else:
                current_row.append(word)
                
        # Add last row
        if current_row:
            current_row.sort(key=lambda x: x[0])
            content.append([w[4] for w in current_row])
            
        return content
        
    def _extract_references(self, doc: fitz.Document) -> List[Dict]:
        """
        Extract references from the document.
        Looks for reference section at the end of document.
        """
        references = []
        for page in reversed(range(len(doc))):  # Start from last page
            page_obj = doc[page]
            text = page_obj.get_text("text")
            
            # Look for reference section
            ref_starts = ["References", "Bibliography", "Литература"]
            for start in ref_starts:
                if start in text:
                    # Extract text after reference header
                    ref_text = text[text.find(start):]
                    # Split into individual references (basic)
                    ref_list = [ref.strip() for ref in ref_text.split('\n') 
                              if ref.strip() and ref.strip() not in ref_starts]
                    
                    for ref in ref_list:
                        references.append({
                            "text": ref,
                            "page": page + 1
                        })
                    return references
                    
        return references
        
    def _parse_font_flags(self, flags: int) -> List[str]:
        """Parse PDF font flags into list of attributes."""
        attributes = []
        if flags & 2**0:  # superscript
            attributes.append("superscript")
        if flags & 2**1:  # italic
            attributes.append("italic")
        if flags & 2**2:  # serifed
            attributes.append("serifed")
        if flags & 2**3:  # monospace
            attributes.append("monospace")
        if flags & 2**4:  # bold
            attributes.append("bold")
        return attributes
        
    async def process_batch(self, file_paths: List[Union[str, Path]], 
                          use_cache: bool = True) -> List[Dict]:
        """
        Process multiple documents in parallel.
        
        Args:
            file_paths: List of paths to PDF files
            use_cache: Whether to use cache
            
        Returns:
            List of processed documents
        """
        tasks = [self.process_document(path, use_cache) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def extract_toc(self, doc: fitz.Document) -> List[Dict]:
        """
        Extract table of contents (if available).
        
        Args:
            doc: PyMuPDF document
            
        Returns:
            List of TOC entries with page numbers
        """
        try:
            toc = doc.get_toc()
            return [{"title": t[1], "page": t[2], "level": t[0]} for t in toc]
        except:
            return []
