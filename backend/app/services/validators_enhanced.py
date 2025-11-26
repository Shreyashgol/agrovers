"""
Enhanced Parameter Validation with Semantic Matching

Adds confidence scoring and semantic similarity matching to validators.
Uses sentence embeddings to match user input to canonical labels.
"""

from typing import Dict, List, Tuple, Optional
from ..models import ValidationResult, Language
import re


# Import the original mappings
from .validators import (
    COLOR_MAPPINGS,
    MOISTURE_MAPPINGS,
    SMELL_MAPPINGS,
    SOIL_TYPE_MAPPINGS,
    EARTHWORMS_MAPPINGS,
    HELP_INDICATORS,
)


class SemanticValidator:
    """
    Enhanced validator with semantic matching using embeddings.
    
    Falls back to exact/fuzzy matching if embeddings not available.
    """
    
    def __init__(self, use_embeddings: bool = True):
        """
        Initialize semantic validator.
        
        Args:
            use_embeddings: Whether to use sentence embeddings for matching
        """
        self.use_embeddings = use_embeddings
        self.model = None
        
        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                from ..config import settings
                self.model = SentenceTransformer(settings.embedding_model_name)
                print("✓ Semantic validator initialized with embeddings")
            except Exception as e:
                print(f"⚠️  Could not load embeddings for validator: {e}")
                self.use_embeddings = False
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.
        
        Returns:
            Similarity score 0.0 to 1.0
        """
        if not self.use_embeddings or not self.model:
            # Fallback to simple string matching
            return self._fuzzy_match(text1, text2)
        
        try:
            # Compute embeddings
            emb1 = self.model.encode([text1], convert_to_numpy=True)[0]
            emb2 = self.model.encode([text2], convert_to_numpy=True)[0]
            
            # Cosine similarity
            import numpy as np
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            
            return float(max(0.0, min(1.0, similarity)))
        except Exception as e:
            print(f"⚠️  Similarity computation error: {e}")
            return self._fuzzy_match(text1, text2)
    
    def _fuzzy_match(self, text1: str, text2: str) -> float:
        """Simple fuzzy string matching fallback."""
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # Exact match
        if text1 == text2:
            return 1.0
        
        # Substring match
        if text1 in text2 or text2 in text1:
            return 0.85
        
        # Levenshtein-like simple check
        common_chars = set(text1) & set(text2)
        if len(common_chars) > 0:
            ratio = len(common_chars) / max(len(set(text1)), len(set(text2)))
            return ratio * 0.7
        
        return 0.0
    
    def match_to_canonical(
        self,
        user_text: str,
        canonical_labels: Dict[str, List[str]],
        language: Language
    ) -> Tuple[Optional[str], float]:
        """
        Match user text to canonical labels using semantic similarity.
        
        Args:
            user_text: User's input text
            canonical_labels: Dict of {canonical_label: [synonyms]}
            language: User's language
            
        Returns:
            Tuple of (best_label, confidence_score)
        """
        user_text = user_text.lower().strip()
        
        best_label = None
        best_score = 0.0
        
        for canonical, synonyms in canonical_labels.items():
            for synonym in synonyms:
                score = self.compute_similarity(user_text, synonym)
                if score > best_score:
                    best_score = score
                    best_label = canonical
        
        return best_label, best_score


# Global semantic validator instance
_semantic_validator = None


def get_semantic_validator() -> SemanticValidator:
    """Get or create global semantic validator instance."""
    global _semantic_validator
    if _semantic_validator is None:
        _semantic_validator = SemanticValidator(use_embeddings=True)
    return _semantic_validator


# Enhanced validation functions with confidence scoring

def validate_color_enhanced(text: str, language: Language) -> ValidationResult:
    """Enhanced color validation with semantic matching."""
    validator = get_semantic_validator()
    
    # Check for help request
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    # Build canonical labels with all synonyms
    canonical_labels = {
        "black": ["black", "kali", "काली", "काला", "dark", "गहरा", "kala"],
        "red": ["red", "lal", "लाल", "reddish", "laal"],
        "brown": ["brown", "bhura", "भूरा", "भूरी", "bhoora"],
        "yellow": ["yellow", "peela", "पीला", "पीली", "peeli"],
        "grey": ["grey", "gray", "surahi", "सुराही", "ग्रे", "gray"],
    }
    
    # Semantic matching
    best_label, confidence = validator.match_to_canonical(text, canonical_labels, language)
    
    # Be more lenient - accept lower confidence for colors
    if best_label and confidence >= 0.60:
        return ValidationResult(value=best_label, is_confident=True)
    elif best_label and confidence >= 0.40:
        # Medium confidence - still accept it
        return ValidationResult(value=best_label, is_confident=True)
    else:
        return ValidationResult(value=None, is_confident=False)


def validate_moisture_enhanced(text: str, language: Language) -> ValidationResult:
    """Enhanced moisture validation."""
    validator = get_semantic_validator()
    
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    canonical_labels = {
        "dry": ["dry", "sukhi", "सूखी", "सूखा", "arid"],
        "wet": ["wet", "geeli", "गीली", "गीला", "moist", "damp"],
        "moist": ["moist", "nam", "नम", "humid"],
        "very_dry": ["very dry", "bahut sukhi", "बहुत सूखी"],
    }
    
    best_label, confidence = validator.match_to_canonical(text, canonical_labels, language)
    
    if best_label and confidence >= 0.60:
        return ValidationResult(value=best_label, is_confident=True)
    elif best_label and confidence >= 0.40:
        return ValidationResult(value=best_label, is_confident=True)
    else:
        return ValidationResult(value=None, is_confident=False)


def validate_smell_enhanced(text: str, language: Language) -> ValidationResult:
    """Enhanced smell validation."""
    validator = get_semantic_validator()
    
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    canonical_labels = {
        "sweet": ["sweet", "meethi", "मीठी", "मीठा", "good"],
        "earthy": ["earthy", "mitti", "मिट्टी", "soil-like"],
        "sour": ["sour", "khatti", "खट्टी", "खट्टा", "acidic"],
        "rotten": ["rotten", "sadhi", "सड़ी", "bad", "foul"],
        "no_smell": ["no smell", "koi gandh nahi", "कोई गंध नहीं", "odorless"],
    }
    
    best_label, confidence = validator.match_to_canonical(text, canonical_labels, language)
    
    if best_label and confidence >= 0.60:
        return ValidationResult(value=best_label, is_confident=True)
    elif best_label and confidence >= 0.40:
        return ValidationResult(value=best_label, is_confident=True)
    else:
        return ValidationResult(value=None, is_confident=False)


def validate_ph_enhanced(text: str, language: Language) -> ValidationResult:
    """Enhanced pH validation with numeric extraction."""
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    normalized = text.lower().strip()
    
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
    
    # Semantic matching for categories
    validator = get_semantic_validator()
    canonical_labels = {
        "acidic": ["acidic", "acid", "अम्लीय", "khatta"],
        "neutral": ["neutral", "तटस्थ", "balanced"],
        "alkaline": ["alkaline", "basic", "क्षारीय"],
    }
    
    best_label, confidence = validator.match_to_canonical(text, canonical_labels, language)
    
    if best_label and confidence >= 0.60:
        return ValidationResult(value=best_label, is_confident=True)
    elif best_label and confidence >= 0.40:
        return ValidationResult(value=best_label, is_confident=True)
    else:
        return ValidationResult(value=None, is_confident=False)


def validate_soil_type_enhanced(text: str, language: Language) -> ValidationResult:
    """Enhanced soil type validation."""
    validator = get_semantic_validator()
    
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    canonical_labels = {
        "clay": ["clay", "chikni", "चिकनी", "sticky"],
        "sandy": ["sandy", "retili", "रेतिली", "sand"],
        "loamy": ["loamy", "dumat", "दोमट", "मिट्टी", "balanced"],
        "silt": ["silt", "silty"],
    }
    
    best_label, confidence = validator.match_to_canonical(text, canonical_labels, language)
    
    if best_label and confidence >= 0.60:
        return ValidationResult(value=best_label, is_confident=True)
    elif best_label and confidence >= 0.40:
        return ValidationResult(value=best_label, is_confident=True)
    else:
        return ValidationResult(value=None, is_confident=False)


def validate_earthworms_enhanced(text: str, language: Language) -> ValidationResult:
    """Enhanced earthworms validation."""
    validator = get_semantic_validator()
    
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    canonical_labels = {
        "yes": ["yes", "haan", "हाँ", "हैं", "present"],
        "no": ["no", "nahi", "नहीं", "absent"],
        "many": ["many", "bahut", "बहुत", "lots"],
        "few": ["few", "kam", "कम", "some"],
    }
    
    best_label, confidence = validator.match_to_canonical(text, canonical_labels, language)
    
    if best_label and confidence >= 0.60:
        return ValidationResult(value=best_label, is_confident=True)
    elif best_label and confidence >= 0.40:
        return ValidationResult(value=best_label, is_confident=True)
    else:
        return ValidationResult(value=None, is_confident=False)


def validate_location_enhanced(text: str, language: Language) -> ValidationResult:
    """Enhanced location validation (accepts free text)."""
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    normalized = text.lower().strip()
    if len(normalized) > 2:  # At least 3 characters
        return ValidationResult(value=normalized, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)


def validate_fertilizer_used_enhanced(text: str, language: Language) -> ValidationResult:
    """Enhanced fertilizer validation."""
    validator = get_semantic_validator()
    
    if _check_help_request(text, language):
        return ValidationResult(value=None, is_confident=False)
    
    normalized = text.lower().strip()
    
    # Check for yes/no first
    yes_no_labels = {
        "yes": ["yes", "haan", "हाँ", "used"],
        "no": ["no", "nahi", "नहीं", "none"],
    }
    
    best_label, confidence = validator.match_to_canonical(text, yes_no_labels, language)
    
    if best_label and confidence >= 0.60:
        return ValidationResult(value=best_label, is_confident=True)
    
    # If not yes/no, accept as fertilizer name (if reasonable length)
    if len(normalized) > 2:
        return ValidationResult(value=normalized, is_confident=True)
    
    return ValidationResult(value=None, is_confident=False)


# Helper functions

def _check_help_request(text: str, language: Language) -> bool:
    """Check if user is asking for help."""
    normalized = text.lower().strip()
    indicators = HELP_INDICATORS.get(language, [])
    return any(indicator in normalized for indicator in indicators)


# Export enhanced validators
ENHANCED_VALIDATORS = {
    "color": validate_color_enhanced,
    "moisture": validate_moisture_enhanced,
    "smell": validate_smell_enhanced,
    "ph": validate_ph_enhanced,
    "soil_type": validate_soil_type_enhanced,
    "earthworms": validate_earthworms_enhanced,
    "location": validate_location_enhanced,
    "fertilizer_used": validate_fertilizer_used_enhanced,
}
