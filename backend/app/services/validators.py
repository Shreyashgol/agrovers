"""
Parameter validation logic for soil test answers.

Each validator function checks if a user's input matches expected values
for a parameter. Returns ValidationResult with:
- value: normalized answer if recognized
- is_confident: True if answer is valid, False if needs helper mode

To add new synonyms or values:
- Update the mapping dictionaries below
- No code logic changes needed for simple additions
"""

from typing import Dict, List
from ..models import ValidationResult, Language
import re


# Color mappings (English and Hindi)
COLOR_MAPPINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "black": "black",
        "kali": "black",
        "dark": "black",
        "red": "red",
        "lal": "red",
        "brown": "brown",
        "bhura": "brown",
        "yellow": "yellow",
        "peela": "yellow",
        "grey": "grey",
        "gray": "grey",
        "surahi": "grey",
    },
    "hi": {
        "काली": "black",
        "काला": "black",
        "लाल": "red",
        "भूरा": "brown",
        "भूरी": "brown",
        "पीला": "yellow",
        "पीली": "yellow",
        "सुराही": "grey",
        "ग्रे": "grey",
    }
}


# Moisture mappings
MOISTURE_MAPPINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "dry": "dry",
        "sukhi": "dry",
        "wet": "wet",
        "geeli": "wet",
        "moist": "moist",
        "nam": "moist",
        "very_dry": "very_dry",
        "bahut_sukhi": "very_dry",
    },
    "hi": {
        "सूखी": "dry",
        "सूखा": "dry",
        "गीली": "wet",
        "गीला": "wet",
        "नम": "moist",
        "बहुत सूखी": "very_dry",
    }
}


# Smell mappings
SMELL_MAPPINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "sweet": "sweet",
        "meethi": "sweet",
        "earthy": "earthy",
        "mitti": "earthy",
        "sour": "sour",
        "khatti": "sour",
        "rotten": "rotten",
        "sadhi": "rotten",
        "no_smell": "no_smell",
        "koi_gandh_nahi": "no_smell",
    },
    "hi": {
        "मीठी": "sweet",
        "मीठा": "sweet",
        "मिट्टी": "earthy",
        "खट्टी": "sour",
        "खट्टा": "sour",
        "सड़ी": "rotten",
        "कोई गंध नहीं": "no_smell",
    }
}


# Soil type mappings
SOIL_TYPE_MAPPINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "clay": "clay",
        "chikni": "clay",
        "sandy": "sandy",
        "retili": "sandy",
        "loamy": "loamy",
        "dumat": "loamy",
        "silt": "silt",
    },
    "hi": {
        "चिकनी": "clay",
        "रेतिली": "sandy",
        "दोमट": "loamy",
        "मिट्टी": "loamy",
    }
}


# Earthworms mappings
EARTHWORMS_MAPPINGS: Dict[str, Dict[str, str]] = {
    "en": {
        "yes": "yes",
        "haan": "yes",
        "present": "yes",
        "hain": "yes",
        "no": "no",
        "nahi": "no",
        "absent": "no",
        "many": "many",
        "bahut": "many",
        "few": "few",
        "kam": "few",
    },
    "hi": {
        "हाँ": "yes",
        "हैं": "yes",
        "नहीं": "no",
        "बहुत": "many",
        "कम": "few",
    }
}


# Help/uncertainty indicators
HELP_INDICATORS: Dict[str, List[str]] = {
    "en": ["help", "don't know", "dont know", "dunno", "unsure", "not sure", "?", "idk", "i don't know", "i dont know", "no idea", "need help"],
    "hi": ["मदद", "पता नहीं", "समझ नहीं आया", "?", "नहीं पता", "मुझे नहीं पता", "मुझे पता नहीं", "मालूम नहीं", "मदद चाहिए"],
}


def _normalize_text(text: str) -> str:
    """Normalize text for comparison (lowercase, strip whitespace)."""
    return text.lower().strip()


def _check_help_request(text: str, language: Language) -> bool:
    """Check if user is asking for help."""
    normalized = _normalize_text(text)
    indicators = HELP_INDICATORS.get(language, [])
    return any(indicator in normalized for indicator in indicators)


def _match_in_mapping(text: str, mapping: Dict[str, str], language: Language) -> str | None:
    """Try to match text against a mapping dictionary."""
    normalized = _normalize_text(text)
    
    # Direct match
    if normalized in mapping:
        return mapping[normalized]
    
    # Partial match (contains keyword)
    for key, value in mapping.items():
        if key in normalized or normalized in key:
            return value
    
    return None


def validate_color(text: str, language: Language) -> ValidationResult:
    """
    Validate soil color answer.
    
    Returns ValidationResult with normalized color value or None if uncertain.
    """
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    # Combine both language mappings for better coverage
    combined_mapping = {**COLOR_MAPPINGS.get("en", {}), **COLOR_MAPPINGS.get(language, {})}
    value = _match_in_mapping(text, combined_mapping, language)
    
    if value:
        return ValidationResult(value=value, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)


def validate_moisture(text: str, language: Language) -> ValidationResult:
    """Validate soil moisture answer."""
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    combined_mapping = {**MOISTURE_MAPPINGS.get("en", {}), **MOISTURE_MAPPINGS.get(language, {})}
    value = _match_in_mapping(text, combined_mapping, language)
    
    if value:
        return ValidationResult(value=value, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)


def validate_smell(text: str, language: Language) -> ValidationResult:
    """Validate soil smell answer."""
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    combined_mapping = {**SMELL_MAPPINGS.get("en", {}), **SMELL_MAPPINGS.get(language, {})}
    value = _match_in_mapping(text, combined_mapping, language)
    
    if value:
        return ValidationResult(value=value, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)


def validate_ph(text: str, language: Language) -> ValidationResult:
    """
    Validate pH answer.
    
    Tries to extract numeric pH value (e.g., "6.5", "around 7").
    Also checks for category words like "acidic", "neutral", "alkaline".
    """
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    normalized = _normalize_text(text)
    
    # Try to extract numeric pH
    ph_pattern = r'(\d+\.?\d*)'
    matches = re.findall(ph_pattern, normalized)
    if matches:
        try:
            ph_value = float(matches[0])
            if 0 <= ph_value <= 14:
                # Categorize pH
                if ph_value < 5.5:
                    category = "very_acidic"
                elif ph_value < 6.5:
                    category = "acidic"
                elif ph_value <= 7.5:
                    category = "neutral"
                elif ph_value < 8.5:
                    category = "alkaline"
                else:
                    category = "very_alkaline"
                
                return ValidationResult(
                    value=category,
                    ph_value=ph_value,
                    is_confident=True
                )
        except ValueError:
            pass
    
    # Check for category words
    ph_categories = {
        "en": {
            "acidic": "acidic",
            "acid": "acidic",
            "neutral": "neutral",
            "alkaline": "alkaline",
            "basic": "alkaline",
        },
        "hi": {
            "अम्लीय": "acidic",
            "तटस्थ": "neutral",
            "क्षारीय": "alkaline",
        }
    }
    
    combined = {**ph_categories.get("en", {}), **ph_categories.get(language, {})}
    category = _match_in_mapping(text, combined, language)
    
    if category:
        return ValidationResult(value=category, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)


def validate_soil_type(text: str, language: Language) -> ValidationResult:
    """Validate soil type answer."""
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    combined_mapping = {**SOIL_TYPE_MAPPINGS.get("en", {}), **SOIL_TYPE_MAPPINGS.get(language, {})}
    value = _match_in_mapping(text, combined_mapping, language)
    
    if value:
        return ValidationResult(value=value, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)


def validate_earthworms(text: str, language: Language) -> ValidationResult:
    """Validate earthworms presence answer."""
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    combined_mapping = {**EARTHWORMS_MAPPINGS.get("en", {}), **EARTHWORMS_MAPPINGS.get(language, {})}
    value = _match_in_mapping(text, combined_mapping, language)
    
    if value:
        return ValidationResult(value=value, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)


def validate_location(text: str, language: Language) -> ValidationResult:
    """
    Validate location/topology answer.
    
    This is more flexible - accepts any non-empty text as valid.
    """
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    normalized = _normalize_text(text)
    if len(normalized) > 2:  # At least 3 characters
        return ValidationResult(value=normalized, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)


def validate_fertilizer_used(text: str, language: Language) -> ValidationResult:
    """
    Validate fertilizer usage answer.
    
    Accepts yes/no or fertilizer names.
    """
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    normalized = _normalize_text(text)
    
    # Check for yes/no
    yes_no_mapping = {
        "en": {"yes": "yes", "no": "no", "haan": "yes", "nahi": "no"},
        "hi": {"हाँ": "yes", "नहीं": "no", "हैं": "yes"},
    }
    combined = {**yes_no_mapping.get("en", {}), **yes_no_mapping.get(language, {})}
    yes_no = _match_in_mapping(text, combined, language)
    
    if yes_no:
        return ValidationResult(value=yes_no, is_confident=True)
    
    # If not yes/no, accept as fertilizer name (if reasonable length)
    if len(normalized) > 2:
        return ValidationResult(value=normalized, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)

