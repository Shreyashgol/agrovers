"""
API routes for session management and soil test wizard.

Endpoints:
- POST /api/v1/session/start - Start new session
- POST /api/v1/session/next - Submit answer and get next step
- GET /api/v1/session/state/{session_id} - Get current session state
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Optional
from ..models import (
    StartSessionRequest,
    StartSessionResponse,
    NextMessageRequest,
    NextMessageResponse,
    SessionStateResponse,
    SessionState,
)
from ..services.session_manager import session_manager
from ..services.orchestrator import (
    get_initial_question,
    get_step_number,
    PARAMETER_ORDER,
    handle_user_message,
)
from ..services.orchestrator_enhanced import handle_user_message_enhanced
from ..services.rag_engine import RAGEngine
from ..services.llm_adapter import LLMAdapter
from ..services.n8n_client import send_to_n8n
from ..services.stt_service import create_stt_service
from ..services.tts_service import create_tts_service

router = APIRouter(prefix="/api/v1/session", tags=["sessions"])


# Dependency injection for RAG engine and LLM
# These will be initialized in main.py and passed via dependency
def get_rag_engine() -> RAGEngine:
    """Dependency to get RAG engine instance."""
    # This will be overridden in main.py with actual instance
    raise RuntimeError("RAG engine not initialized")


def get_llm() -> LLMAdapter:
    """Dependency to get LLM adapter instance."""
    # This will be overridden in main.py with actual instance
    raise RuntimeError("LLM adapter not initialized")


# Store instances (set by main.py)
_rag_engine: RAGEngine | None = None
_llm_adapter: LLMAdapter | None = None


def set_rag_engine(engine: RAGEngine) -> None:
    """Set RAG engine instance (called from main.py)."""
    global _rag_engine
    _rag_engine = engine


def set_llm_adapter(adapter: LLMAdapter) -> None:
    """Set LLM adapter instance (called from main.py)."""
    global _llm_adapter
    _llm_adapter = adapter


def get_rag_engine_dep() -> RAGEngine:
    """Dependency function that returns RAG engine."""
    if _rag_engine is None:
        raise HTTPException(status_code=500, detail="RAG engine not initialized")
    return _rag_engine


def get_llm_dep() -> LLMAdapter:
    """Dependency function that returns LLM adapter."""
    if _llm_adapter is None:
        raise HTTPException(status_code=500, detail="LLM adapter not initialized")
    return _llm_adapter


@router.post("/start", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest) -> StartSessionResponse:
    """
    Start a new soil test session.
    
    Creates a new session with selected language and returns first question.
    """
    session = session_manager.create_session(request.language)
    parameter, question = get_initial_question(request.language)
    
    # Generate TTS for first question (ALL questions get audio)
    tts_service = create_tts_service()
    audio_url = ""
    try:
        audio_path = tts_service.synthesize(question, request.language)
        audio_url = tts_service.get_audio_url(audio_path, base_url="http://localhost:8001")
        print(f"✓ TTS generated for first question: {audio_url}")
    except Exception as e:
        print(f"✗ TTS error for first question: {e}")
    
    return StartSessionResponse(
        session_id=session.session_id,
        parameter=parameter,
        question=question,
        step_number=1,
        total_steps=len(PARAMETER_ORDER),
        audio_url=audio_url if audio_url else None,
    )


@router.post("/next", response_model=NextMessageResponse)
async def next_message(
    session_id: str = Form(...),
    user_text: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    rag_engine: RAGEngine = Depends(get_rag_engine_dep),
    llm: LLMAdapter = Depends(get_llm_dep),
) -> NextMessageResponse:
    """
    Process user message (text or audio) and move to next step.
    
    Accepts either:
    - user_text: Text input
    - audio_file: Audio file (wav, mp3, etc.)
    - Both (text takes precedence)
    
    Returns next question or helper text with optional audio URL.
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Read audio bytes if provided
    audio_bytes = None
    if audio_file:
        audio_bytes = await audio_file.read()
    
    # Initialize services
    stt_service = create_stt_service() if audio_bytes else None
    tts_service = create_tts_service()
    
    # Process through enhanced orchestrator
    response, audit = handle_user_message_enhanced(
        session=session,
        user_message=user_text,
        audio_bytes=audio_bytes,
        rag_engine=rag_engine,
        llm=llm,
        stt_service=stt_service,
        tts_service=tts_service,
    )
    
    # Update session state
    session.current_parameter = response.parameter
    session.helper_mode = response.helper_mode
    session.answers = response.answers
    session_manager.update_session(session)
    
    # Log audit data
    print(f"📊 Audit: {audit}")
    
    # If complete, send to n8n
    if response.is_complete:
        success, error = send_to_n8n(response.answers)
        if not success:
            print(f"⚠ Warning: Failed to send to n8n: {error}")
    
    return response


@router.get("/state/{session_id}", response_model=SessionStateResponse)
async def get_session_state(session_id: str) -> SessionStateResponse:
    """
    Get current state of a session.
    
    Returns current parameter, collected answers, and progress.
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if complete - use the session's is_complete method
    is_complete = session.is_complete()
    
    return SessionStateResponse(
        session_id=session.session_id,
        language=session.language,
        current_parameter=session.current_parameter,
        answers=session.answers,
        step_number=get_step_number(session.current_parameter),
        total_steps=len(PARAMETER_ORDER),
        is_complete=is_complete,
    )

