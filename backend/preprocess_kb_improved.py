"""
IMPROVED Knowledge Base Preprocessing Script

Better chunking strategy that preserves step-by-step instructions.
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
    """Detect Hindi vs English."""
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    if devanagari_pattern.search(text):
        return "hi"
    return "en"


def extract_parameter_from_filename(filename: str) -> str:
    """Extract parameter from filename."""
    param_mapping = {
        "color": "color",
        "moisture": "moisture",
        "smell": "smell",
        "ph": "ph",
        "soil": "soil_type",
        "earthworm": "earthworms",
        "location": "location",
        "fertilizer": "fertilizer_used",
    }
    
    filename_lower = filename.lower()
    for key, param in param_mapping.items():
        if key in filename_lower:
            return param
    
    return "general"


def chunk_markdown_improved(content: str, filename: str) -> List[Dict[str, Any]]:
    """
    Improved chunking that preserves step-by-step instructions.
    
    Strategy:
    1. Find "कैसे जांचें" or "How to test" sections
    2. Extract step-by-step instructions (कदम 1, कदम 2, Step 1, Step 2)
    3. Keep steps together in chunks
    4. Separate options/examples into different chunks
    """
    chunks = []
    parameter = extract_parameter_from_filename(filename)
    language = detect_language(content)
    
    # Pattern 1: Find "कैसे करें" or "कैसे जांचें" sections with steps
    # Match both formats: **कैसे करें:** and **कैसे जांचें**
    how_to_pattern_hi = r'\*\*कैसे (?:करें|जांचें).*?\*\*\s*(.*?)(?=\n###|\n---|\Z)'
    how_to_matches_hi = re.findall(how_to_pattern_hi, content, re.DOTALL)
    
    for match in how_to_matches_hi:
        # Extract steps (कदम 1, कदम 2, etc.)
        step_pattern = r'####\s*कदम\s*\d+:.*?(?=####|###|\n\n---|\Z)'
        steps = re.findall(step_pattern, match, re.DOTALL)
        
        if steps:
            # Combine all steps into one instructional chunk
            full_instructions = "\n\n".join(steps)
            if len(full_instructions) > 100:
                chunks.append({
                    "text": full_instructions.strip(),
                    "language": "hi",
                    "parameter": parameter,
                    "section_type": "how_to_test",
                    "module_name": Path(filename).stem,
                })
        
        # Also create individual step chunks for better retrieval
        for i, step in enumerate(steps):
            if len(step.strip()) > 50:
                chunks.append({
                    "text": step.strip(),
                    "language": "hi",
                    "parameter": parameter,
                    "section_type": "how_to_test_step",
                    "step_number": i + 1,
                    "module_name": Path(filename).stem,
                })
    
    # Pattern 2: Find English "How to test" sections
    how_to_pattern_en = r'\*\*How to (?:test|check).*?\*\*\s*(.*?)(?=\n###|\n---|\Z)'
    how_to_matches_en = re.findall(how_to_pattern_en, content, re.DOTALL | re.IGNORECASE)
    
    for match in how_to_matches_en:
        step_pattern = r'####\s*Step\s*\d+:.*?(?=####|###|\n\n---|\Z)'
        steps = re.findall(step_pattern, match, re.DOTALL | re.IGNORECASE)
        
        if steps:
            full_instructions = "\n\n".join(steps)
            if len(full_instructions) > 100:
                chunks.append({
                    "text": full_instructions.strip(),
                    "language": "en",
                    "parameter": parameter,
                    "section_type": "how_to_test",
                    "module_name": Path(filename).stem,
                })
        
        for i, step in enumerate(steps):
            if len(step.strip()) > 50:
                chunks.append({
                    "text": step.strip(),
                    "language": "en",
                    "parameter": parameter,
                    "section_type": "how_to_test_step",
                    "step_number": i + 1,
                    "module_name": Path(filename).stem,
                })
    
    # Pattern 3: Extract option descriptions (for reference)
    option_pattern = r'###\s*विकल्प\s*\d+:.*?\n\n(.*?)(?=###|---|\Z)'
    options = re.findall(option_pattern, content, re.DOTALL)
    
    for option in options:
        # Only take first 300 chars of each option
        option_text = option.strip()[:300]
        if len(option_text) > 50 and "```json" not in option_text:
            chunks.append({
                "text": option_text,
                "language": detect_language(option_text),
                "parameter": parameter,
                "section_type": "options",
                "module_name": Path(filename).stem,
            })
    
    return chunks


def process_knowledge_base_improved() -> None:
    """Main preprocessing with improved chunking."""
    backend_dir = Path(__file__).parent
    kb_raw_dir = backend_dir / settings.kb_raw_dir
    kb_processed_dir = backend_dir / settings.kb_processed_dir
    embeddings_dir = backend_dir / settings.embeddings_dir
    
    kb_processed_dir.mkdir(parents=True, exist_ok=True)
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    if not kb_raw_dir.exists():
        print(f"⚠ Warning: Knowledge base directory not found: {kb_raw_dir}")
        return
    
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
    
    # Process all files with improved chunking
    all_chunks = []
    for md_file in md_files:
        print(f"  Processing: {md_file.name}")
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        chunks = chunk_markdown_improved(content, md_file.name)
        all_chunks.extend(chunks)
        
        # Count by type
        how_to_count = sum(1 for c in chunks if c["section_type"] == "how_to_test")
        step_count = sum(1 for c in chunks if c["section_type"] == "how_to_test_step")
        print(f"    → {len(chunks)} chunks ({how_to_count} how-to, {step_count} steps)")
    
    print(f"\n📦 Total chunks: {len(all_chunks)}")
    
    # Show breakdown
    by_type = {}
    for chunk in all_chunks:
        section_type = chunk.get("section_type", "unknown")
        by_type[section_type] = by_type.get(section_type, 0) + 1
    
    print("Chunk breakdown:")
    for chunk_type, count in sorted(by_type.items()):
        print(f"  - {chunk_type}: {count}")
    
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
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Save index
    index_path = embeddings_dir / "kb_index.faiss"
    faiss.write_index(index, str(index_path))
    print(f"✓ Saved FAISS index to {index_path}")
    
    # Save metadata
    metadata_dict = {str(i): chunk for i, chunk in enumerate(all_chunks)}
    meta_path = embeddings_dir / "kb_index_meta.pkl"
    with open(meta_path, "wb") as f:
        pickle.dump(metadata_dict, f)
    print(f"✓ Saved metadata to {meta_path}")
    
    print("\n✅ Improved knowledge base preprocessing complete!")
    print(f"   Index size: {index.ntotal} vectors")
    print(f"   Embedding dimension: {dimension}")


if __name__ == "__main__":
    process_knowledge_base_improved()
