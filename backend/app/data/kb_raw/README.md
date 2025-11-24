# Knowledge Base Raw Files

Place your markdown knowledge base files in this directory.

## File Naming Convention

Files should follow the pattern: `NN-description.md`

Examples:
- `01-color-detection.md`
- `02-moisture-testing.md`
- `03-smell-testing.md`
- `04-ph-home-testing.md`
- `05-09-combined.md`
- `10-crop-recommendations.md`
- `11-fertilizer-guide.md`

## File Format

Each markdown file should contain:
- Headings (##, ###) for sections
- Bilingual content (Hindi and English)
- Step-by-step instructions
- Parameter-specific information

The preprocessing script (`preprocess_kb.py`) will:
- Extract metadata from filenames
- Chunk content by headings/paragraphs
- Detect language (Hindi vs English)
- Create embeddings and FAISS index

## After Adding Files

Run the preprocessing script:

```bash
cd backend
python preprocess_kb.py
```

This will create:
- `kb_processed/kb_chunks.jsonl` - Chunked content
- `embeddings/kb_index.faiss` - FAISS index
- `embeddings/kb_index_meta.pkl` - Metadata

