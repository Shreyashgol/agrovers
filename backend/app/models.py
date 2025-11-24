"""
Pydantic models for request/response validation and session state.

These models define the data structures used throughout the application:
- API request/response models
- Session state models
- Soil test result models

To add a new parameter:
1. Add field to SoilTestResult
2. Add to PARAMETER_ORDER in orchestrator.py
3. Add validator in validators.py
4. Update frontend labels/config
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# Type aliases for better readability
Language = Literal["hi", "en"]


class SoilTestResult(BaseModel):
    """
    Complete soil test data collected from farmer.
    
    All fields are optional until filled during the wizard flow.
    """
    color: Optional[str] = None
    moisture: Optional[str] = None
    smell: Optional[str] = None
    ph_category: Optional[str] = None  # e.g. "very_acidic", "neutral", "alkaline"
    ph_value: Optional[float] = None   # Numeric pH if captured (e.g. 6.5)
    soil_type: Optional[str] = None
    earthworms: Optional[str] = None
    location: Optional[str] = None
    fertilizer_used: Optional[str] = None


class SessionState(BaseModel):
    """
    Represents the current state of a farmer's session.
    
    Tracks:
    - Which parameter is currently being collected
    - All answers collected so far
    - Whether helper mode is active
    - Language preference
    """
    session_id: str
    language: Language
    current_parameter: str
    answers: SoilTestResult
    helper_mode: bool = False  # True when showing RAG+LLM explanation
    created_at: float  # Unix timestamp
    updated_at: float  # Unix timestamp


# API Request/Response Models

class StartSessionRequest(BaseModel):
    """Request to start a new session with language selection."""
    language: Language


class StartSessionResponse(BaseModel):
    """Response after starting a session with first question."""
    session_id: str
    parameter: str
    question: str
    step_number: int
    total_steps: int


class NextMessageRequest(BaseModel):
    """Request to submit answer and move to next step."""
    session_id: str
    user_message: str


class NextMessageResponse(BaseModel):
    """Response after processing user message."""
    session_id: str
    parameter: str
    question: Optional[str] = None  # Next question if moving forward
    helper_text: Optional[str] = None  # RAG+LLM explanation if in helper mode
    answers: SoilTestResult
    is_complete: bool
    step_number: int
    total_steps: int
    helper_mode: bool = False
    audio_url: Optional[str] = None  # TTS audio URL for response
    audit: Optional[dict] = None  # Confidence scores and debug info


class SessionStateResponse(BaseModel):
    """Response for getting current session state."""
    session_id: str
    language: Language
    current_parameter: str
    answers: SoilTestResult
    step_number: int
    total_steps: int
    is_complete: bool


class ValidationResult(BaseModel):
    """
    Result of validating a user's answer for a parameter.
    
    Used internally by validators.py to communicate validation status.
    """
    value: Optional[str] = None  # Normalized value if recognized
    ph_value: Optional[float] = None  # For pH parameter
    is_confident: bool  # True if answer is valid, False if uncertain/needs help

