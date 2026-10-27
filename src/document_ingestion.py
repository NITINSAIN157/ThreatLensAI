"""
ThreatLens AI - Document Ingestion & Chunking Pipeline
Extracts text from markdown, text, and PDF documents in knowledge_base/documents/,
performs semantic/structural chunking, and attaches rich cybersecurity metadata.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Any

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def extract_text_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """Extracts text per page from a PDF file using pypdf."""
    from pypdf import PdfReader
    pages_data = []
    reader = PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages_data.append({
                "page_number": i + 1,
                "text": text.strip()
            })
    return pages_data

def chunk_markdown_or_text(text: str, chunk_size: int = 500, chunk_overlap: int = 100) -> List[Dict[str, Any]]:
    """
    Chunks markdown text respecting headings (##, ###) and paragraph boundaries.
    """
    # Split by markdown headers or double newlines
    sections = re.split(r'\n(?=#{1,4}\s+)', text)
    chunks = []
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Determine section header if present
        header_match = re.match(r'^(#{1,4}\s+[^\n]+)', section)
        current_header = header_match.group(1).replace('#', '').strip() if header_match else "General"
        
        # If section is small enough, keep as single chunk
        if len(section) <= chunk_size:
            chunks.append({
                "section": current_header,
                "text": section
            })
        else:
            # Subdivide section by paragraphs or words
            paragraphs = section.split('\n\n')
            current_chunk = ""
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue
                if len(current_chunk) + len(para) + 2 <= chunk_size:
                    current_chunk = f"{current_chunk}\n\n{para}".strip()
                else:
                    if current_chunk:
                        chunks.append({
                            "section": current_header,
                            "text": current_chunk
                        })
                    current_chunk = para
                    
            if current_chunk:
                chunks.append({
                    "section": current_header,
                    "text": current_chunk
                })
                
    return chunks

def ingest_knowledge_base(docs_dir: str = "knowledge_base/documents") -> List[Dict[str, Any]]:
    """
    Scans the knowledge base directory, reads all markdown, text, and PDF files,
    and returns chunked records with source, title, and section metadata.
    """
    docs_path = Path(docs_dir)
    if not docs_path.exists():
        docs_path.mkdir(parents=True, exist_ok=True)
        return []
        
    all_chunks = []
    chunk_counter = 0
    
    for file_path in docs_path.iterdir():
        if file_path.suffix.lower() in [".md", ".txt"]:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            doc_title = file_path.stem.replace("_", " ").title()
            first_line = content.strip().split("\n")[0]
            if first_line.startswith("#"):
                doc_title = first_line.replace("#", "").strip()
                
            raw_chunks = chunk_markdown_or_text(content)
            for ch in raw_chunks:
                chunk_counter += 1
                all_chunks.append({
                    "id": f"chunk_{chunk_counter}",
                    "source": file_path.name,
                    "title": doc_title,
                    "section": ch["section"],
                    "page": 1,
                    "text": ch["text"]
                })
                
        elif file_path.suffix.lower() == ".pdf":
            pages = extract_text_from_pdf(str(file_path))
            doc_title = file_path.stem.replace("_", " ").title()
            for p in pages:
                raw_chunks = chunk_markdown_or_text(p["text"])
                for ch in raw_chunks:
                    chunk_counter += 1
                    all_chunks.append({
                        "id": f"chunk_{chunk_counter}",
                        "source": file_path.name,
                        "title": doc_title,
                        "section": ch["section"],
                        "page": p["page_number"],
                        "text": ch["text"]
                    })
                    
    print(f"Ingested {len(all_chunks)} chunks across documents in {docs_dir}")
    return all_chunks

if __name__ == "__main__":
    chunks = ingest_knowledge_base()
    for c in chunks[:3]:
        print(f"\n--- [{c['source']}] {c['title']} | Section: {c['section']} ---")
        print(c["text"][:180] + "...")
