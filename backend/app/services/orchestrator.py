"""
Orchestrator - Core logic for managing the soil test wizard flow.

Coordinates:
- Parameter order and progression
- Answer validation
- Helper mode activation (RAG + LLM)
- Session state updates

To add a new parameter:
1. Add to PARAMETER_ORDER list below
2. Add question text to PARAMETER_QUESTIONS
3. Add validator function in validators.py
4. Update SoilTestResult model in models.py
5. Update frontend labels/config
"""

from typing import Tuple
from ..models import (
    SessionState,
    NextMessageResponse,
    Language,
    ValidationResult,
    SoilTestResult,
)
from .validators import (
    validate_color,
    validate_moisture,
    validate_smell,
    validate_ph,
    validate_soil_type,
    validate_earthworms,
    validate_location,
    validate_fertilizer_used,
)
from .rag_engine import RAGEngine
from .llm_adapter import LLMAdapter


# Parameter order - defines the wizard flow
PARAMETER_ORDER = [
    "color",
    "moisture",
    "smell",
    "ph",
    "soil_type",
    "earthworms",
    "location",
    "fertilizer_used",
]


# Question text for each parameter (can be overridden by knowledge base)
PARAMETER_QUESTIONS: dict[str, dict[Language, str]] = {
    "color": {
        "en": "What is the color of your soil?",
        "hi": "आपकी मिट्टी का रंग क्या है?",
    },
    "moisture": {
        "en": "What is the moisture level of your soil?",
        "hi": "आपकी मिट्टी में नमी का स्तर क्या है?",
    },
    "smell": {
        "en": "What does your soil smell like?",
        "hi": "आपकी मिट्टी से कैसी गंध आती है?",
    },
    "ph": {
        "en": "What is the pH level of your soil?",
        "hi": "आपकी मिट्टी का pH स्तर क्या है?",
    },
    "soil_type": {
        "en": "What type of soil do you have?",
        "hi": "आपकी मिट्टी किस प्रकार की है?",
    },
    "earthworms": {
        "en": "Are there earthworms in your soil?",
        "hi": "क्या आपकी मिट्टी में केंचुए हैं?",
    },
    "location": {
        "en": "Where is your farm located? (village, district, state)",
        "hi": "आपका खेत कहाँ स्थित है? (गाँव, जिला, राज्य)",
    },
    "fertilizer_used": {
        "en": "What fertilizers have you used recently?",
        "hi": "आपने हाल ही में कौन सी खाद का उपयोग किया है?",
    },
}


# Validator function mapping
VALIDATORS = {
    "color": validate_color,
    "moisture": validate_moisture,
    "smell": validate_smell,
    "ph": validate_ph,
    "soil_type": validate_soil_type,
    "earthworms": validate_earthworms,
    "location": validate_location,
    "fertilizer_used": validate_fertilizer_used,
}


def get_initial_question(language: Language) -> Tuple[str, str]:
    """
    Get the first question for a new session.
    
    Returns:
        Tuple of (parameter_name, question_text)
    """
    first_param = PARAMETER_ORDER[0]
    question = PARAMETER_QUESTIONS[first_param][language]
    return first_param, question


def get_question_for_parameter(parameter: str, language: Language) -> str:
    """
    Get question text for a parameter.
    
    Args:
        parameter: Parameter name
        language: Language preference
        
    Returns:
        Question text in requested language
    """
    return PARAMETER_QUESTIONS.get(parameter, {}).get(language, "Please provide information.")


def get_next_parameter(current_parameter: str) -> str | None:
    """
    Get the next parameter in the order.
    
    Args:
        current_parameter: Current parameter name
        
    Returns:
        Next parameter name, or None if last parameter
    """
    try:
        current_idx = PARAMETER_ORDER.index(current_parameter)
        if current_idx < len(PARAMETER_ORDER) - 1:
            return PARAMETER_ORDER[current_idx + 1]
    except ValueError:
        pass
    return None


def get_step_number(parameter: str) -> int:
    """Get step number (1-indexed) for a parameter."""
    try:
        return PARAMETER_ORDER.index(parameter) + 1
    except ValueError:
        return 0


def handle_user_message(
    session: SessionState,
    user_message: str,
    rag_engine: RAGEngine,
    llm: LLMAdapter,
) -> NextMessageResponse:
    """
    Core orchestration logic - processes user message and returns next state.
    
    Flow:
    1. Validate user's answer for current parameter
    2. If valid -> update answers, move to next parameter
    3. If invalid/help -> activate helper mode (RAG + LLM)
    4. Return appropriate response
    
    Args:
        session: Current session state
        user_message: Farmer's input
        rag_engine: RAG engine for knowledge retrieval
        llm: LLM adapter for generating explanations
        
    Returns:
        NextMessageResponse with updated state
    """
    current_param = session.current_parameter
    language = session.language
    
    # Get validator for current parameter
    validator_func = VALIDATORS.get(current_param)
    if not validator_func:
        # Unknown parameter - skip to next
        next_param = get_next_parameter(current_param)
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
            # All parameters complete
            session.helper_mode = False
            return NextMessageResponse(
                session_id=session.session_id,
                parameter=current_param,
                answers=session.answers,
                is_complete=True,
                step_number=len(PARAMETER_ORDER),
                total_steps=len(PARAMETER_ORDER),
                helper_mode=False,
            )
    
    # Validate user's answer
    validation_result: ValidationResult = validator_func(user_message, language)
    
    if validation_result.is_confident and validation_result.value:
        # Valid answer - update session and move forward
        _update_answers(session.answers, current_param, validation_result)
        session.helper_mode = False
        
        # Move to next parameter
        next_param = get_next_parameter(current_param)
        
        if next_param:
            # More parameters to collect
            session.current_parameter = next_param
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
            # All parameters collected
            return NextMessageResponse(
                session_id=session.session_id,
                parameter=current_param,
                answers=session.answers,
                is_complete=True,
                step_number=len(PARAMETER_ORDER),
                total_steps=len(PARAMETER_ORDER),
                helper_mode=False,
            )
    
    else:
        # Invalid/uncertain answer - activate helper mode
        session.helper_mode = True
        
        # Build query for RAG
        query = _build_rag_query(current_param, user_message, language)
        
        # Retrieve relevant chunks
        if rag_engine.is_ready():
            chunks = rag_engine.retrieve(query, current_param, language, k=4)
        else:
            chunks = []
        
        # Generate helper text using LLM
        helper_text = llm.generate_helper(
            parameter=current_param,
            language=language,
            user_message=user_message,
            retrieved_chunks=chunks,
        )
        
        return NextMessageResponse(
            session_id=session.session_id,
            parameter=current_param,
            helper_text=helper_text,
            answers=session.answers,
            is_complete=False,
            step_number=get_step_number(current_param),
            total_steps=len(PARAMETER_ORDER),
            helper_mode=True,
        )


def _update_answers(answers: SoilTestResult, parameter: str, validation: ValidationResult) -> None:
    """
    Update answers dict with validated value.
    
    Args:
        answers: SoilTestResult to update
        parameter: Parameter name
        validation: ValidationResult with value
    """
    if parameter == "color":
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
    """
    Build query string for RAG retrieval.
    
    Args:
        parameter: Current parameter
        user_message: User's input
        language: Language preference
        
    Returns:
        Query string for RAG
    """
    # Parameter-specific query templates
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

