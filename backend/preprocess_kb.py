"""
Knowledge Base Preprocessing Script

Converts markdown knowledge base files into:
1. Chunked JSONL file (kb_chunks.jsonl)
2. FAISS index (kb_index.faiss)
3. Metadata pickle (kb_index_meta.pkl)

Usage:
    python preprocess_kb.py

To modify chunking strategy:
    - Edit _chunk_markdown() function
    - Adjust metadata extraction logic
"""

import os
import json
import pickle
import re
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.config import settings


def detect_language(text: str) -> str:
    """
    Simple language detection (Hindi vs English).
    
    Checks for Devanagari script characters.
    """
    # Check for Devanagari Unicode range
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    if devanagari_pattern.search(text):
        return "hi"
    return "en"


def extract_metadata_from_filename(filename: str) -> Dict[str, Any]:
    """
    Extract metadata from filename.
    
    Examples:
        "01-color-detection.md" -> {module_id: "01", module_name: "color_detection", parameter: "color"}
        "05-09-combined.md" -> {module_id: "05-09", module_name: "combined"}
    """
    base = Path(filename).stem
    parts = base.split("-", 1)
    
    metadata = {
        "module_id": parts[0] if parts else "",
        "module_name": parts[1] if len(parts) > 1 else base,
    }
    
    # Try to infer parameter from module name
    param_mapping = {
        "color": "color",
        "moisture": "moisture",
        "smell": "smell",
        "ph": "ph",
        "soil_type": "soil_type",
        "earthworms": "earthworms",
        "location": "location",
        "fertilizer": "fertilizer_used",
        "crop": "crop_recommendation",
    }
    
    for key, param in param_mapping.items():
        if key in metadata["module_name"].lower():
            metadata["parameter"] = param
            break
    
    return metadata


def chunk_markdown(content: str, filename: str) -> List[Dict[str, Any]]:
    """
    Split markdown content into chunks.
    
    Strategy:
    - Split on headings (##, ###)
    - Split on bullet points for lists
    - Each chunk should be 100-500 characters ideally
    """
    chunks = []
    base_metadata = extract_metadata_from_filename(filename)
    
    # Split by headings first
    sections = re.split(r'\n(#{2,3}\s+.+?)\n', content, flags=re.MULTILINE)
    
    current_section = ""
    current_heading = ""
    
    for i, section in enumerate(sections):
        if section.startswith("#"):
            # This is a heading
            current_heading = section.strip()
            continue
        
        # This is content
        if section.strip():
            current_section = section.strip()
            
            # Further split by paragraphs
            paragraphs = re.split(r'\n\n+', current_section)
            
            for para in paragraphs:
                if not para.strip():
                    continue
                
                # If paragraph is too long, split by sentences
                if len(para) > 500:
                    sentences = re.split(r'[.!?]\s+', para)
                    current_chunk = ""
                    
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) > 500:
                            if current_chunk:
                                chunks.append(_create_chunk(
                                    current_chunk,
                                    base_metadata,
                                    current_heading
                                ))
                            current_chunk = sentence
                        else:
                            current_chunk += " " + sentence if current_chunk else sentence
                    
                    if current_chunk:
                        chunks.append(_create_chunk(
                            current_chunk,
                            base_metadata,
                            current_heading
                        ))
                else:
                    chunks.append(_create_chunk(
                        para,
                        base_metadata,
                        current_heading
                    ))
    
    # If no chunks created (no headings), chunk by paragraphs
    if not chunks:
        paragraphs = re.split(r'\n\n+', content)
        for para in paragraphs:
            if para.strip() and len(para.strip()) > 50:
                chunks.append(_create_chunk(
                    para.strip(),
                    base_metadata,
                    ""
                ))
    
    return chunks


def _create_chunk(
    text: str,
    base_metadata: Dict[str, Any],
    heading: str
) -> Dict[str, Any]:
    """Create a chunk dictionary with metadata."""
    language = detect_language(text)
    
    # Determine section type
    section_type = "explanation"
    if "how" in text.lower() or "कैसे" in text:
        section_type = "how_to_test"
    elif "?" in text or "?" in text:
        section_type = "question"
    elif re.match(r'^[-*•]', text, re.MULTILINE):
        section_type = "options"
    
    chunk_meta = {
        **base_metadata,
        "text": text.strip(),
        "language": language,
        "section_type": section_type,
        "heading": heading,
    }
    
    return chunk_meta


def process_knowledge_base() -> None:
    """
    Main preprocessing function.
    
    Reads all .md files from kb_raw/, chunks them, creates embeddings,
    and saves to FAISS index.
    """
    # Resolve paths relative to backend/ directory
    backend_dir = Path(__file__).parent
    kb_raw_dir = backend_dir / settings.kb_raw_dir
    kb_processed_dir = backend_dir / settings.kb_processed_dir
    embeddings_dir = backend_dir / settings.embeddings_dir
    
    # Create output directories
    kb_processed_dir.mkdir(parents=True, exist_ok=True)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    if not kb_raw_dir.exists():
        print(f"⚠ Warning: Knowledge base directory not found: {kb_raw_dir}")
        print("  Please copy your .md files to this directory first.")
        return
    
    # Find all markdown files
    md_files = list(kb_raw_dir.glob("*.md"))
    if not md_files:
        print(f"⚠ Warning: No .md files found in {kb_raw_dir}")
        return
    
    print(f"📚 Found {len(md_files)} markdown files")
    
    # Load embedding model
    print("🔄 Loading embedding model...")
    model_kwargs = {}
    if settings.hf_token:
        model_kwargs["token"] = settings.hf_token
    
    embedding_model = SentenceTransformer(
        settings.embedding_model_name,
        **model_kwargs
    )
    print(f"✓ Loaded: {settings.embedding_model_name}")
    
    # Process all files and create chunks
    all_chunks = []
    for md_file in md_files:
        print(f"  Processing: {md_file.name}")
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        chunks = chunk_markdown(content, md_file.name)
        all_chunks.extend(chunks)
        print(f"    → Created {len(chunks)} chunks")
    
    print(f"\n📦 Total chunks: {len(all_chunks)}")
    
    # Save chunks to JSONL
    jsonl_path = kb_processed_dir / "kb_chunks.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    print(f"✓ Saved chunks to {jsonl_path}")
    
    # Create embeddings
    print("🔄 Creating embeddings...")
    texts = [chunk["text"] for chunk in all_chunks]
    embeddings = embedding_model.encode(texts, show_progress_bar=True)
    embeddings = embeddings.astype('float32')
    
    print(f"✓ Created {len(embeddings)} embeddings (dim: {embeddings.shape[1]})")
    
    # Create FAISS index
    print("🔄 Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)  # L2 distance
    index.add(embeddings)
    
    # Save index
    index_path = embeddings_dir / "kb_index.faiss"
    faiss.write_index(index, str(index_path))
    print(f"✓ Saved FAISS index to {index_path}")
    
    # Save metadata (chunk_id -> metadata mapping)
    metadata_dict = {str(i): chunk for i, chunk in enumerate(all_chunks)}
    meta_path = embeddings_dir / "kb_index_meta.pkl"
    with open(meta_path, "wb") as f:
        pickle.dump(metadata_dict, f)
    print(f"✓ Saved metadata to {meta_path}")
    
    print("\n✅ Knowledge base preprocessing complete!")
    print(f"   Index size: {index.ntotal} vectors")
    print(f"   Embedding dimension: {dimension}")


if __name__ == "__main__":
    process_knowledge_base()

