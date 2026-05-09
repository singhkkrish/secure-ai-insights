"""
PDF document service.
Extracts text from PDFs and provides keyword-based search.
Documents are indexed in-memory at startup for fast retrieval.
"""
import logging
import re
from pathlib import Path
from typing import List, Dict
import PyPDF2

from app.config import settings

logger = logging.getLogger(__name__)

# In-memory document store: [{name, path, content, chunks}]
_document_store: List[Dict] = []


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract all text from a PDF file."""
    text_parts = []
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text_parts.append(page.extract_text() or "")
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path}: {e}")
    return "\n".join(text_parts)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks for retrieval."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def load_documents():
    """Load and index all PDFs from the PDF directory."""
    pdf_dir = Path(settings.PDF_DIR)
    _document_store.clear()

    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        logger.info(f"Indexing PDF: {pdf_path.name}")
        content = extract_pdf_text(pdf_path)
        chunks = chunk_text(content)
        doc_name = pdf_path.stem.replace("_", " ").title()
        _document_store.append({
            "name": doc_name,
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "content": content,
            "chunks": chunks,
        })

    logger.info(f"Indexed {len(_document_store)} PDF documents.")


def search_documents(query: str, top_k: int = 5) -> List[Dict]:
    """
    Simple keyword-based search across document chunks.
    Returns top_k most relevant chunks with source attribution.
    """
    if not _document_store:
        load_documents()

    query_terms = set(re.sub(r"[^\w\s]", "", query.lower()).split())
    results = []

    for doc in _document_store:
        for i, chunk in enumerate(doc["chunks"]):
            chunk_lower = chunk.lower()
            score = sum(1 for term in query_terms if term in chunk_lower)
            # Boost score for longer term matches
            for term in query_terms:
                if len(term) > 4 and term in chunk_lower:
                    score += 2
            if score > 0:
                results.append({
                    "source": doc["name"],
                    "filename": doc["filename"],
                    "chunk_index": i,
                    "content": chunk[:800],  # Limit content length
                    "relevance_score": score,
                })

    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    return results[:top_k]


def list_documents() -> List[Dict]:
    """Return metadata for all indexed documents."""
    if not _document_store:
        load_documents()
    return [
        {"name": d["name"], "filename": d["filename"], "chunks": len(d["chunks"])}
        for d in _document_store
    ]
