"""
FastAPI application entry point for Argovers Soil Assistant.

Initializes:
- RAG engine (loads FAISS index)
- LLM adapter (Gemini or local)
- FastAPI app with routes
- CORS middleware

To run:
    uvicorn app.main:app --reload

To change LLM provider:
    Update llm_provider in config.py and set corresponding API key
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .config import settings
from .routes import sessions, reports
from .services.rag_engine import RAGEngine
from .services.llm_adapter import create_llm_adapter

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Soil testing assistant for farmers with RAG-powered help",
    version="1.0.0",
)

# Configure CORS - MUST be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Initialize RAG engine and LLM adapter
rag_engine: RAGEngine | None = None
llm_adapter = None


@app.on_event("startup")
async def startup_event():
    """
    Initialize services on application startup.
    
    Loads:
    - RAG engine (FAISS index + embedding model)

    """
    global rag_engine, llm_adapter
    
    print("🚀 Starting Argovers Soil Assistant...")
    
    # Initialize RAG engine
    try:
        rag_engine = RAGEngine()
        sessions.set_rag_engine(rag_engine)
        print("✓ RAG engine ready")
    except Exception as e:
        print(f"⚠ Warning: RAG engine initialization failed: {e}")
        print("  Helper mode will not work until index is built.")
        # Create a dummy engine that returns empty results
        rag_engine = None
    
    # Initialize LLM adapter
    try:
        llm_adapter = create_llm_adapter()
        sessions.set_llm_adapter(llm_adapter)
        print("✓ LLM adapter ready")
    except Exception as e:
        print(f"✗ Error: LLM adapter initialization failed: {e}")
        print("  Please check your API keys in .env file")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    print("👋 Shutting down Argovers Soil Assistant...")


# Include routers
app.include_router(sessions.router)
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

# Mount static files for audio
audio_dir = Path(__file__).parent / "data" / "audio"
audio_dir.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(audio_dir)), name="audio")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Argovers Soil Assistant API",
        "status": "running",
        "rag_ready": rag_engine.is_ready() if rag_engine else False,
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "rag_ready": rag_engine.is_ready() if rag_engine else False,
    }

