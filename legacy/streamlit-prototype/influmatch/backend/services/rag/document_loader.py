import os
from pathlib import Path
from typing import List, Dict
from loguru import logger

try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class DocumentLoader:
    def load_text_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def load_pdf(self, path: str) -> str:
        if not PDF_AVAILABLE:
            logger.warning("[ARIA::RAG] PyPDF2 not installed, skipping PDF")
            return ""
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def load_directory(self, dir_path: str, extensions: List[str] = None) -> List[Dict]:
        extensions = extensions or [".txt", ".md", ".pdf"]
        docs = []
        for file_path in Path(dir_path).rglob("*"):
            if file_path.suffix in extensions:
                try:
                    content = self.load_pdf(str(file_path)) if file_path.suffix == ".pdf" else self.load_text_file(str(file_path))
                    if content.strip():
                        docs.append({"path": str(file_path), "name": file_path.name, "content": content})
                        logger.info(f"[ARIA::RAG] Loaded: {file_path.name}")
                except Exception as e:
                    logger.error(f"[ARIA::RAG] Failed to load {file_path}: {e}")
        return docs

loader = DocumentLoader()
