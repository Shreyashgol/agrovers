# Argovers Soil Assistant - System Info

## Quick Start
```bash
# Start all services
./start_backend.sh    # Backend on :8001
./start_frontend.sh   # Frontend on :5174
ollama serve          # LLM on :11434
```

## Configuration
- **LLM**: Ollama Phi3 (local, fast)
- **STT**: Groq Whisper (cloud)
- **TTS**: gTTS (cloud)
- **RAG**: 484 chunks, FAISS index

## Key Features
- ✅ LLM-based answer extraction from natural language
- ✅ RAG-powered help when user says "I don't know"
- ✅ Chat-based UI with voice input
- ✅ Bilingual (Hindi/English)
- ✅ Auto-play audio responses

## Architecture
```
User Input → LLM Extraction → Validation → Decision
                                              ↓
                                    Valid? → Next Question
                                    Help? → RAG Guidance
```

## API Endpoints
- POST `/api/v1/session/start` - Start new session
- POST `/api/v1/session/next` - Submit answer (text/audio)
- GET `/api/v1/session/state/{id}` - Get session state

## Environment Variables
See `backend/.env` for configuration.

## URLs
- Backend: http://localhost:8001
- Frontend: http://localhost:5174
- Ollama: http://localhost:11434
