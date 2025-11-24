# Argovers Soil Assistant - Backend

FastAPI backend for the soil testing assistant that guides farmers through collecting 8 core soil parameters with RAG-powered help.

## Architecture Overview

```
┌─────────────┐
│   Frontend  │ (React + TypeScript)
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌───────────────────────────────┐  │
│  │   Routes (sessions.py)        │  │
│  └───────────┬───────────────────┘  │
│              │                      │
│  ┌───────────▼───────────────────┐  │
│  │   Orchestrator                │  │ ◄── Core logic
│  │   - Parameter flow            │  │
│  │   - Answer validation         │  │
│  │   - Helper mode trigger       │  │
│  └───┬───────────────────┬───────┘  │
│      │                   │          │
│  ┌───▼──────┐    ┌──────▼────────┐  │
│  │Validators│    │  RAG Engine   │  │
│  │          │    │  + LLM        │  │
│  └──────────┘    └──────┬────────┘  │
│                         │           │
│                    ┌────▼────┐      │
│                    │ FAISS   │      │
│                    │ Index   │      │
│                    └─────────┘      │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│     n8n     │ (Webhook)
└─────────────┘
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-1.5-flash
LLM_PROVIDER=gemini

# Hugging Face (for embeddings)
HF_TOKEN=your_hf_token_here

# n8n Integration
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/soil

# Knowledge Base Paths (relative to backend/)
KB_RAW_DIR=app/data/kb_raw
KB_PROCESSED_DIR=app/data/kb_processed
EMBEDDINGS_DIR=app/data/embeddings
```

### 3. Add Knowledge Base Files

Copy your markdown knowledge base files to `backend/app/data/kb_raw/`:

```bash
# Example structure
backend/app/data/kb_raw/
  ├── 01-color-detection.md
  ├── 02-moisture-testing.md
  ├── 03-smell-testing.md
  ├── 04-ph-home-testing.md
  ├── 05-09-combined.md
  ├── 10-crop-recommendations.md
  └── 11-fertilizer-guide.md
```

### 4. Preprocess Knowledge Base

Run the preprocessing script to build FAISS index:

```bash
python preprocess_kb.py
```

This will:
- Read all `.md` files from `kb_raw/`
- Chunk them by headings/paragraphs
- Create embeddings using `sentence-transformers/all-MiniLM-L6-v2`
- Build FAISS index and save to `embeddings/`
- Save chunk metadata to `kb_processed/kb_chunks.jsonl`

### 5. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

## API Endpoints

### `POST /api/v1/session/start`

Start a new session with language selection.

**Request:**
```json
{
  "language": "hi"  // or "en"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "parameter": "color",
  "question": "आपकी मिट्टी का रंग क्या है?",
  "step_number": 1,
  "total_steps": 8
}
```

### `POST /api/v1/session/next`

Submit answer and get next step.

**Request:**
```json
{
  "session_id": "uuid",
  "user_message": "काली"
}
```

**Response (valid answer):**
```json
{
  "session_id": "uuid",
  "parameter": "moisture",
  "question": "आपकी मिट्टी में नमी का स्तर क्या है?",
  "answers": { "color": "black" },
  "is_complete": false,
  "step_number": 2,
  "total_steps": 8,
  "helper_mode": false
}
```

**Response (helper mode):**
```json
{
  "session_id": "uuid",
  "parameter": "color",
  "helper_text": "किसान भाई, मिट्टी का रंग जांचने के लिए...",
  "answers": {},
  "is_complete": false,
  "step_number": 1,
  "total_steps": 8,
  "helper_mode": true
}
```

### `GET /api/v1/session/state/{session_id}`

Get current session state.

## How It Works

### Flow Diagram

1. **User starts session** → `POST /session/start`
   - Creates session with language preference
   - Returns first question (color)

2. **User submits answer** → `POST /session/next`
   - Orchestrator validates answer using `validators.py`
   - If valid:
     - Updates `answers` dict
     - Moves to next parameter
     - Returns next question
   - If invalid/help requested:
     - RAG engine retrieves relevant chunks
     - LLM generates explanation
     - Returns helper text (stays on same step)

3. **All parameters collected** → `POST /session/next` (last step)
   - Orchestrator detects completion
   - Sends data to n8n webhook
   - Returns `is_complete: true`

### Key Components

#### Orchestrator (`services/orchestrator.py`)

- Manages parameter order (`PARAMETER_ORDER`)
- Coordinates validation → RAG → LLM flow
- Decides when to advance or show helper

**To add a new parameter:**
1. Add to `PARAMETER_ORDER` list
2. Add question to `PARAMETER_QUESTIONS`
3. Add validator function in `validators.py`
4. Update `SoilTestResult` model in `models.py`

#### Validators (`services/validators.py`)

- Maps user input to normalized values
- Supports Hindi and English synonyms
- Returns `ValidationResult` with confidence flag

**To add synonyms:**
- Update mapping dictionaries (e.g., `COLOR_MAPPINGS`, `MOISTURE_MAPPINGS`)
- No code changes needed for simple additions

#### RAG Engine (`services/rag_engine.py`)

- Loads FAISS index on startup
- Retrieves top-k chunks filtered by:
  - Parameter name
  - Language preference
- Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings

**To change embedding model:**
- Update `embedding_model_name` in `config.py`
- Re-run `preprocess_kb.py`

#### LLM Adapter (`services/llm_adapter.py`)

- Abstract interface for LLM providers
- Current: Gemini API
- Future: Local models (Llama3, Phi3)

**To swap LLM:**
1. Implement new adapter class
2. Update `llm_provider` in `config.py`
3. Set corresponding API key

#### n8n Client (`services/n8n_client.py`)

- Sends final `SoilTestResult` to n8n webhook
- Called automatically when all parameters collected

**To change webhook URL:**
- Update `N8N_WEBHOOK_URL` in `.env`

## Configuration

### Parameter List

Edit `services/orchestrator.py`:

```python
PARAMETER_ORDER = [
    "color",
    "moisture",
    # ... add more
]
```

### Questions

Edit `PARAMETER_QUESTIONS` in `services/orchestrator.py`:

```python
PARAMETER_QUESTIONS = {
    "color": {
        "en": "What is the color?",
        "hi": "रंग क्या है?",
    },
    # ...
}
```

### Validation Synonyms

Edit mapping dictionaries in `services/validators.py`:

```python
COLOR_MAPPINGS = {
    "en": {
        "black": "black",
        "dark": "black",
        # add more
    },
    # ...
}
```

## Troubleshooting

### RAG Engine Not Ready

**Error:** "RAG engine not initialized"

**Solution:**
1. Ensure markdown files are in `app/data/kb_raw/`
2. Run `python preprocess_kb.py`
3. Check that `kb_index.faiss` and `kb_index_meta.pkl` exist in `app/data/embeddings/`

### LLM API Errors

**Error:** "LLM adapter initialization failed"

**Solution:**
1. Check `.env` file has correct `GEMINI_API_KEY`
2. Verify API key is valid
3. Check internet connection (for API calls)

### n8n Webhook Fails

**Warning:** "Failed to send to n8n"

**Solution:**
1. Verify `N8N_WEBHOOK_URL` is correct
2. Test webhook URL manually with curl
3. Check n8n workflow is active

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests (when implemented)
pytest
```

### Code Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entrypoint
│   ├── config.py            # Settings and env vars
│   ├── models.py            # Pydantic models
│   ├── routes/
│   │   └── sessions.py      # API endpoints
│   ├── services/
│   │   ├── session_manager.py
│   │   ├── orchestrator.py
│   │   ├── validators.py
│   │   ├── rag_engine.py
│   │   ├── llm_adapter.py
│   │   └── n8n_client.py
│   └── data/
│       ├── kb_raw/          # Input markdown files
│       ├── kb_processed/    # Chunked JSONL
│       └── embeddings/      # FAISS index
├── preprocess_kb.py         # Knowledge base preprocessing
├── requirements.txt
├── .env                     # Environment variables
└── README.md
```

## Future Enhancements

- [ ] Redis/PostgreSQL session storage
- [ ] Local LLM adapter (Llama3/Phi3)
- [ ] Fine-tuning data collection from interactions
- [ ] Analytics and logging
- [ ] Docker containerization
- [ ] Unit and integration tests

