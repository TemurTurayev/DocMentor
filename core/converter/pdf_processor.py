from typing import List, Dict
from PyPDF2 import PdfReader
import os

class PDFProcessor:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        # Check cache first
        cache_path = os.path.join(
            self.cache_dir, 
            f"{os.path.basename(pdf_path)}.txt"
        )
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # Extract text if not cached
        reader = PdfReader(pdf_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        # Cache the result
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return text
    
    def create_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks with overlap"""
        chunks = []
        overlap = 100
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            chunks.append(chunk)
        
        return chunks