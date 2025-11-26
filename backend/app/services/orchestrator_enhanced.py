"""
Enhanced Orchestrator with Audio Support and Confidence Scoring

Adds:
- Audio input handling (STT)
- Confidence fusion (ASR + Validator + LLM)
- Audit logging
- TTS response generation
"""

from typing import Tuple, Optional, Dict, Any
from ..models import (
    SessionState,
    NextMessageResponse,
    Language,
    ValidationResult,
    SoilTestResult,
)
from .orchestrator import (
    PARAMETER_ORDER,
    PARAMETER_QUESTIONS,
    get_next_parameter,
    get_step_number,
    get_question_for_parameter,
)
from .validators_enhanced import ENHANCED_VALIDATORS
from .orchestrator import validate_name
from .rag_engine import RAGEngine
from .llm_adapter import LLMAdapter
from .stt_service import STTService, ASRResult
from .tts_service import TTSService
from .answer_extractor import get_answer_extractor
from .intent_classifier import get_intent_classifier


# Confidence weights for fusion
W_ASR = 0.20
W_VALIDATOR = 0.60  # Trust validator more
W_LLM = 0.20

# Threshold for auto-fill - Balanced to accept valid answers but reject help requests
AUTO_FILL_THRESHOLD = 0.60


def compute_combined_confidence(
    asr_conf: float,
    validator_conf: float,
    llm_conf: float
) -> float:
    """
    Compute combined confidence using weighted fusion.
    
    Args:
        asr_conf: ASR confidence (0-1)
        validator_conf: Validator confidence (0-1)
        llm_conf: LLM confidence (0-1)
        
    Returns:
        Combined confidence (0-1)
    """
    combined = W_ASR * asr_conf + W_VALIDATOR * validator_conf + W_LLM * llm_conf
    return max(0.0, min(1.0, combined))


def handle_user_message_enhanced(
    session: SessionState,
    user_message: Optional[str],
    audio_bytes: Optional[bytes],
    rag_engine: RAGEngine,
    llm: LLMAdapter,
    stt_service: Optional[STTService] = None,
    tts_service: Optional[TTSService] = None,
) -> Tuple[NextMessageResponse, Dict[str, Any]]:
    """
    Enhanced orchestration with audio support and confidence scoring.
    
    Args:
        session: Current session state
        user_message: Text input (optional if audio provided)
        audio_bytes: Audio input (optional if text provided)
        rag_engine: RAG engine for retrieval
        llm: LLM adapter for helper mode
        stt_service: STT service for audio transcription
        tts_service: TTS service for audio responses
        
    Returns:
        Tuple of (NextMessageResponse, audit_dict)
    """
    current_param = session.current_parameter
    language = session.language
    
    # Initialize audit data
    audit = {
        "asr_conf": 0.0,
        "validator_conf": 0.0,
        "llm_conf": 0.0,
        "combined_conf": 0.0,
        "asr_text": None,
        "retrieved_chunks": [],
    }
    
    # Step 1: Handle audio input if provided
    asr_result: Optional[ASRResult] = None
    if audio_bytes and stt_service:
        try:
            asr_result = stt_service.transcribe(audio_bytes, language)
            audit["asr_conf"] = asr_result.asr_confidence
            audit["asr_text"] = asr_result.text
            
            # Use ASR text if no user_message provided
            if not user_message:
                user_message = asr_result.text
        except Exception as e:
            print(f"✗ STT error: {e}")
            audit["asr_conf"] = 0.0
    
    # If still no message, return error
    if not user_message or not user_message.strip():
        return _create_error_response(
            session,
            "No input provided",
            language,
            tts_service
        ), audit
    
    # Step 2: Use LLM to intelligently classify user intent
    classifier = get_intent_classifier()
    intent, intent_confidence = classifier.classify_intent(user_message, current_param, language)
    
    print(f"✓ Intent classification: {intent} (confidence: {intent_confidence:.2f})")
    audit["intent"] = intent
    audit["intent_confidence"] = intent_confidence
    
    # Check if this is a follow-up question (confidence 0.75 indicates follow-up)
    is_follow_up = intent == "help_request" and intent_confidence == 0.75
    
    # If it's clearly a help request, skip extraction and go straight to RAG helper
    if intent == "help_request" and intent_confidence >= 0.70:
        if is_follow_up:
            print(f"✓ Follow-up question detected: '{user_message}' - providing additional guidance")
        else:
            print(f"✓ Help request detected: '{user_message}'")
        
        audit["validator_conf"] = 0.0
        audit["help_request"] = True
        audit["is_follow_up"] = is_follow_up
        # Jump directly to Step 4 (RAG helper mode)
        validation_result = ValidationResult(value=None, is_confident=False)
    else:
        # Try LLM-based answer extraction
        extractor = get_answer_extractor()
        expected_values = _get_expected_values(current_param)
        
        extracted_value, extraction_conf = extractor.extract_answer(
            user_message, current_param, language, expected_values
        )
        
        # If LLM extracted an answer, use it
        if extracted_value and extraction_conf >= 0.80:
            print(f"✓ LLM extracted: '{extracted_value}' (conf: {extraction_conf:.2f})")
            validation_result = ValidationResult(value=extracted_value, is_confident=True)
            audit["validator_conf"] = extraction_conf
            audit["llm_extraction"] = extracted_value
        else:
            # Fall back to traditional validator
            validator_func = ENHANCED_VALIDATORS.get(current_param)
            if not validator_func:
                # Unknown parameter - skip
                return _handle_unknown_parameter(session, language, tts_service), audit
            
            validation_result: ValidationResult = validator_func(user_message, language)
            
            # Calculate validator confidence
            if validation_result.is_confident and validation_result.value:
                audit["validator_conf"] = 0.95  # High confidence
            elif validation_result.value:
                audit["validator_conf"] = 0.70  # Medium confidence
            else:
                audit["validator_conf"] = 0.10  # Very low confidence - likely help request
    
    # Step 3: Decide if we need helper mode
    # If validator is confident AND has a value, accept immediately (skip LLM)
    if validation_result.is_confident and validation_result.value:
        # High confidence from validator - auto-fill immediately
        audit["combined_conf"] = audit["validator_conf"]
        audit["llm_conf"] = 0.0  # Skipped LLM
        return _auto_fill_and_advance(
            session,
            current_param,
            validation_result,
            audit,
            language,
            tts_service
        ), audit
    
    # Compute preliminary combined confidence (without LLM)
    prelim_conf = compute_combined_confidence(
        audit["asr_conf"],
        audit["validator_conf"],
        0.0  # No LLM yet
    )
    
    # If valid answer with decent confidence, auto-fill immediately
    if validation_result.value and prelim_conf >= 0.60:
        audit["combined_conf"] = prelim_conf
        audit["llm_conf"] = 0.0  # Skipped LLM
        return _auto_fill_and_advance(
            session,
            current_param,
            validation_result,
            audit,
            language,
            tts_service
        ), audit
    
    # Step 4: Enter helper mode - call RAG + LLM
    # This happens when:
    # - User explicitly asked for help
    # - No valid answer was extracted
    # - Confidence is too low
    print(f"✓ Entering helper mode for parameter: {current_param}")
    query = _build_rag_query(current_param, user_message, language)
    
    if rag_engine.is_ready():
        chunks = rag_engine.retrieve(query, current_param, language, k=10)  # Get more chunks for better context
        audit["retrieved_chunks"] = chunks[:2]  # Store first 2 for audit (shorter)
        print(f"✓ Retrieved {len(chunks)} chunks for {current_param}")
    else:
        chunks = []
    
    # Call helper LLM with more chunks for better context
    helper_text = llm.generate_helper(
        parameter=current_param,
        language=language,
        user_message=user_message,
        retrieved_chunks=chunks[:5] if chunks else [],  # Use top 5 chunks
    )
    
    # For now, assume LLM confidence based on response length and content
    audit["llm_conf"] = _estimate_llm_confidence(helper_text, chunks)
    
    # Recompute combined confidence with LLM
    audit["combined_conf"] = compute_combined_confidence(
        audit["asr_conf"],
        audit["validator_conf"],
        audit["llm_conf"]
    )
    
    # We're in helper mode - NEVER auto-fill, always show guidance
    # The user needs to provide a proper answer after seeing the help
    session.helper_mode = True
    print(f"✓ Showing helper guidance for: {current_param}")
    
    # Generate TTS for helper text
    audio_url = ""
    if tts_service and helper_text:
        try:
            audio_path = tts_service.synthesize(helper_text, language)
            audio_url = tts_service.get_audio_url(audio_path)
        except Exception as e:
            print(f"✗ TTS error: {e}")
    
    return NextMessageResponse(
        session_id=session.session_id,
        parameter=current_param,
        helper_text=helper_text,
        answers=session.answers,
        is_complete=False,
        step_number=get_step_number(current_param),
        total_steps=len(PARAMETER_ORDER),
        helper_mode=True,
        audio_url=audio_url if audio_url else None,
        audit=audit,
    ), audit


def _auto_fill_and_advance(
    session: SessionState,
    current_param: str,
    validation: ValidationResult,
    audit: Dict[str, Any],
    language: Language,
    tts_service: Optional[TTSService],
) -> NextMessageResponse:
    """Auto-fill answer and advance to next parameter."""
    print(f"✓ Auto-filling {current_param} with value: {validation.value}")
    
    # Update answers
    _update_answers(session.answers, current_param, validation)
    session.helper_mode = False
    
    # Move to next parameter
    next_param = get_next_parameter(current_param)
    print(f"→ Moving to next parameter: {next_param}")
    
    # Update session's current parameter (None if complete)
    session.current_parameter = next_param
    
    if next_param:
        # More parameters to collect
        next_question = get_question_for_parameter(next_param, language)
        
        # Generate TTS for next question (ALL questions get audio)
        audio_url = ""
        if tts_service:
            print(f"🔊 Generating TTS for {next_param}: '{next_question[:50]}...'")
            try:
                audio_path = tts_service.synthesize(next_question, language)
                audio_url = tts_service.get_audio_url(audio_path)
                print(f"✓ TTS generated: {audio_url}")
            except Exception as e:
                print(f"✗ TTS error: {e}")
        
        return NextMessageResponse(
            session_id=session.session_id,
            parameter=next_param,
            question=next_question,
            answers=session.answers,
            is_complete=False,
            step_number=get_step_number(next_param),
            total_steps=len(PARAMETER_ORDER),
            helper_mode=False,
            audio_url=audio_url if audio_url else None,
            audit=audit,
        )
    else:
        # All parameters collected - set current_parameter to None
        session.current_parameter = None
        return NextMessageResponse(
            session_id=session.session_id,
            parameter="",  # Empty string to indicate completion
            answers=session.answers,
            is_complete=True,
            step_number=len(PARAMETER_ORDER),
            total_steps=len(PARAMETER_ORDER),
            helper_mode=False,
            audit=audit,
        )


def _update_answers(answers: SoilTestResult, parameter: str, validation: ValidationResult) -> None:
    """Update answers dict with validated value."""
    if parameter == "name":
        answers.name = validation.value
    elif parameter == "color":
        answers.color = validation.value
    elif parameter == "moisture":
        answers.moisture = validation.value
    elif parameter == "smell":
        answers.smell = validation.value
    elif parameter == "ph":
        answers.ph_category = validation.value
        if validation.ph_value is not None:
            answers.ph_value = validation.ph_value
    elif parameter == "soil_type":
        answers.soil_type = validation.value
    elif parameter == "earthworms":
        answers.earthworms = validation.value
    elif parameter == "location":
        answers.location = validation.value
    elif parameter == "fertilizer_used":
        answers.fertilizer_used = validation.value


def _build_rag_query(parameter: str, user_message: str, language: Language) -> str:
    """Build query string for RAG retrieval."""
    query_templates = {
        "color": {
            "en": "How to identify soil color at home step by step",
            "hi": "घर पर मिट्टी का रंग कैसे पहचानें चरणबद्ध तरीके से",
        },
        "moisture": {
            "en": "How to test soil moisture level at home step by step",
            "hi": "घर पर मिट्टी की नमी का स्तर कैसे जांचें चरणबद्ध तरीके से",
        },
        "smell": {
            "en": "How to test soil smell at home step by step",
            "hi": "घर पर मिट्टी की गंध कैसे जांचें चरणबद्ध तरीके से",
        },
        "ph": {
            "en": "How to test soil pH at home step by step",
            "hi": "घर पर मिट्टी का pH कैसे जांचें चरणबद्ध तरीके से",
        },
        "soil_type": {
            "en": "How to identify soil type at home step by step",
            "hi": "घर पर मिट्टी का प्रकार कैसे पहचानें चरणबद्ध तरीके से",
        },
        "earthworms": {
            "en": "How to check for earthworms in soil",
            "hi": "मिट्टी में केंचुए कैसे जांचें",
        },
        "location": {
            "en": "soil location and geography",
            "hi": "मिट्टी का स्थान और भूगोल",
        },
        "fertilizer_used": {
            "en": "fertilizer types and usage",
            "hi": "खाद के प्रकार और उपयोग",
        },
    }
    
    base_query = query_templates.get(parameter, {}).get(language, parameter)
    return f"{base_query} {user_message}"


def _get_expected_values(parameter: str) -> list[str]:
    """Get list of expected values for a parameter."""
    expected_values_map = {
        "color": ["black", "red", "brown", "yellow", "grey"],
        "moisture": ["dry", "wet", "moist", "very_dry"],
        "smell": ["sweet", "earthy", "sour", "rotten", "no_smell"],
        "ph": ["acidic", "neutral", "alkaline", "very_acidic", "very_alkaline"],
        "soil_type": ["clay", "sandy", "loamy", "silt"],
        "earthworms": ["yes", "no", "many", "few"],
        "location": [],  # Free text
        "fertilizer_used": [],  # Free text or yes/no
    }
    return expected_values_map.get(parameter, [])


def _estimate_llm_confidence(helper_text: str, chunks: list) -> float:
    """Estimate LLM confidence from response."""
    # Simple heuristic - if response is long and chunks were found, higher confidence
    if not helper_text or len(helper_text) < 20:
        return 0.40
    
    if len(chunks) >= 3 and len(helper_text) > 100:
        return 0.85
    elif len(chunks) >= 1:
        return 0.70
    else:
        return 0.50


def _handle_unknown_parameter(
    session: SessionState,
    language: Language,
    tts_service: Optional[TTSService],
) -> NextMessageResponse:
    """Handle unknown parameter by skipping to next."""
    next_param = get_next_parameter(session.current_parameter)
    
    if next_param:
        session.current_parameter = next_param
        session.helper_mode = False
        return NextMessageResponse(
            session_id=session.session_id,
            parameter=next_param,
            question=get_question_for_parameter(next_param, language),
            answers=session.answers,
            is_complete=False,
            step_number=get_step_number(next_param),
            total_steps=len(PARAMETER_ORDER),
            helper_mode=False,
        )
    else:
        return NextMessageResponse(
            session_id=session.session_id,
            parameter=session.current_parameter,
            answers=session.answers,
            is_complete=True,
            step_number=len(PARAMETER_ORDER),
            total_steps=len(PARAMETER_ORDER),
            helper_mode=False,
        )


def _create_error_response(
    session: SessionState,
    error_msg: str,
    language: Language,
    tts_service: Optional[TTSService],
) -> NextMessageResponse:
    """Create error response."""
    if language == "hi":
        helper_text = f"माफ करें, {error_msg}। कृपया पुनः प्रयास करें।"
    else:
        helper_text = f"Sorry, {error_msg}. Please try again."
    
    audio_url = ""
    if tts_service:
        try:
            audio_path = tts_service.synthesize(helper_text, language)
            audio_url = tts_service.get_audio_url(audio_path)
        except:
            pass
    
    return NextMessageResponse(
        session_id=session.session_id,
        parameter=session.current_parameter,
        helper_text=helper_text,
        answers=session.answers,
        is_complete=False,
        step_number=get_step_number(session.current_parameter),
        total_steps=len(PARAMETER_ORDER),
        helper_mode=True,
        audio_url=audio_url if audio_url else None,
    )
