"""
LLM-based Intent Classifier

Uses local LLM to intelligently detect user intent:
- Is the user asking for help/guidance?
- Is the user providing an answer?
- What's the confidence level?
"""

from typing import Tuple
from ..models import Language
from ..config import settings
import requests


class IntentClassifier:
    """Classifies user intent using local LLM."""
    
    def __init__(self, provider: str = "groq", model_name: str = "llama-3.3-70b-versatile", api_key: str = None):
        """Initialize intent classifier with Groq or Ollama."""
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key
        
        if provider == "groq":
            self.base_url = "https://api.groq.com/openai/v1/chat/completions"
            print(f"✓ Intent classifier initialized with Groq ({model_name})")
        else:
            self.base_url = "http://localhost:11434"
            print(f"✓ Intent classifier initialized with Ollama ({model_name})")
    
    def classify_intent(
        self,
        user_message: str,
        parameter: str,
        language: Language
    ) -> Tuple[str, float]:
        """
        Classify user intent.
        
        Args:
            user_message: What the user said
            parameter: Current parameter (color, moisture, etc.)
            language: Language code
            
        Returns:
            Tuple of (intent, confidence)
            - intent: "answer" or "help_request"
            - confidence: 0.0-1.0
        """
        # Quick check: If message is very short and looks like a valid value, it's likely an answer
        user_lower = user_message.lower().strip()
        
        # Special handling for "name" - almost always an answer unless explicitly asking for help
        if parameter == "name":
            explicit_help = ["help", "मदद", "don't know", "नहीं पता", "how", "कैसे"]
            if not any(phrase in user_lower for phrase in explicit_help):
                return "answer", 0.99
        
        # Comprehensive valid answers for each parameter (English + Hindi + variations)
        valid_answers = {
            "color": [
                # English
                "black", "red", "brown", "yellow", "grey", "gray", "dark", "light", "white",
                # Hindi
                "काली", "काला", "लाल", "भूरी", "भूरा", "पीली", "पीला", "स्लेटी", "सफेद",
                # Variations
                "kali", "lal", "bhura", "peela", "surahi"
            ],
            "moisture": [
                # English
                "dry", "wet", "moist", "damp", "very dry", "very wet", "slightly moist",
                # Hindi
                "सूखी", "सूखा", "गीली", "गीला", "नम", "थोड़ी नम", "बहुत सूखी", "बहुत गीली",
                # Variations
                "sukhi", "geeli", "nam"
            ],
            "smell": [
                # English
                "sweet", "earthy", "sour", "rotten", "no smell", "none", "good", "bad", "fresh",
                # Hindi
                "मीठी", "मीठा", "मिट्टी", "मिट्टी जैसी", "खट्टी", "खट्टा", "सड़ी", "सड़ा", "कोई गंध नहीं",
                # Variations
                "meethi", "mitti", "khatti", "sadhi"
            ],
            "ph": [
                # English
                "acidic", "neutral", "alkaline", "basic", "sour", "bitter", "balanced",
                # Hindi
                "अम्लीय", "तटस्थ", "क्षारीय", "खट्टा", "संतुलित",
                # Variations
                "amliya", "tatasth", "kshariya",
                # Numeric pH values
                "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14",
                "6.5", "7.0", "7.5", "ph"
            ],
            "soil_type": [
                # English
                "clay", "sandy", "loamy", "silt", "silty", "loam", "sand",
                # Hindi
                "चिकनी", "रेतिली", "दोमट", "गादयुक्त", "मिट्टी",
                # Variations
                "chikni", "retili", "domat"
            ],
            "earthworms": [
                # English
                "yes", "no", "many", "few", "none", "some", "lots", "present", "absent",
                # Hindi
                "हाँ", "नहीं", "बहुत", "थोड़े", "कम", "हैं", "नहीं हैं",
                # Variations
                "haan", "nahi", "bahut", "kam", "thode"
            ],
            "location": [
                # Any location-related words - be very permissive for location
                "village", "district", "state", "city", "town", "गाँव", "गाउं", "जिला", "राज्य",
                "में", "है", "से", "का", "की", "in", "at", "from", "near",
                # Common location indicators
                "नई", "पुरानी", "बड़ा", "छोटा", "नगर", "पुर", "आबाद", "गढ़"
            ],
            "fertilizer_used": [
                # English
                "urea", "dap", "npk", "organic", "compost", "manure", "none", "no", "yes",
                # Hindi
                "यूरिया", "डीएपी", "एनपीके", "जैविक", "खाद", "कुछ नहीं", "नहीं", "हाँ",
                # Variations
                "vermicompost", "cow dung", "gobar"
            ],
        }
        
        # Special handling for location - be VERY permissive
        if parameter == "location":
            # For location, unless it's explicitly "don't know" or "help", treat as answer
            explicit_help = ["don't know", "dont know", "नहीं पता", "मदद", "help", "कैसे बताऊं"]
            is_explicit_help = any(phrase in user_lower for phrase in explicit_help)
            
            if not is_explicit_help:
                # If message has more than 2 words, it's almost certainly a location
                if len(user_message.split()) > 2:
                    return "answer", 0.99
                
                # If it has location indicators, it's an answer
                location_indicators = ["में", "है", "से", "का", "की", "गाँव", "गाउं", "जिला", "in", "at", "from", "village", "district"]
                for indicator in location_indicators:
                    if indicator in user_lower:
                        return "answer", 0.98
                
                # If it's a proper noun (capitalized words), likely a location
                words = user_message.split()
                if any(word[0].isupper() for word in words if len(word) > 0):
                    return "answer", 0.97
                
                # For location, even short answers are likely valid (e.g., "Delhi", "Pune")
                if len(user_message.strip()) > 3:
                    return "answer", 0.95
        
        # Check if message contains any valid answer for this parameter
        if parameter in valid_answers:
            for valid_answer in valid_answers[parameter]:
                if valid_answer in user_lower:
                    # It's likely an answer
                    return "answer", 0.95
        
        # Check for obvious help requests (but not follow-up questions)
        help_phrases = [
            "don't know", "dont know", "not sure", "नहीं पता"
        ]
        
        # These are help requests ONLY if they're standalone, not follow-ups
        for phrase in help_phrases:
            if phrase in user_lower:
                return "help_request", 0.95
        
        # Check for follow-up questions (should stay in helper mode but not restart)
        follow_up_phrases = [
            "problem", "issue", "after step", "step", "what next", "then what",
            "समस्या", "कदम के बाद", "फिर क्या"
        ]
        
        for phrase in follow_up_phrases:
            if phrase in user_lower:
                # This is a follow-up question, not a new help request
                # Return as help_request but with lower confidence to indicate it's a follow-up
                return "help_request", 0.75
        
        # If message is very short (1-2 words) and doesn't contain help phrases, likely an answer
        if len(user_message.split()) <= 2:
            return "answer", 0.85
        
        # For longer messages, use LLM classification
        # Build classification prompt
        if language == "hi":
            # Special prompt for location
            if parameter == "location":
                prompt = f"""किसान का संदेश: "{user_message}"
प्रश्न: आपका खेत कहाँ है? (गाँव, जिला, राज्य)

क्या किसान:
A) स्थान बता रहा है (जैसे "सोनीपत में", "दिल्ली", "मेरा गाँव बालगड़ है")
B) मदद मांग रहा है (जैसे "नहीं पता", "कैसे बताऊं")

महत्वपूर्ण: अगर संदेश में कोई भी स्थान का नाम है, तो "ANSWER" चुनें।

केवल एक शब्द में जवाब दो: "ANSWER" या "HELP"

जवाब:"""
            else:
                prompt = f"""किसान का संदेश: "{user_message}"
प्रश्न: मिट्टी का {parameter} क्या है?

क्या किसान:
A) उत्तर दे रहा है (जैसे "काली", "लाल", "नम", "अम्लीय")
B) मदद मांग रहा है (जैसे "नहीं पता", "कैसे जांचें", "समझाओ")

महत्वपूर्ण: अगर संदेश में कोई भी मान्य उत्तर है (रंग, नमी, गंध, pH), तो "ANSWER" चुनें।

केवल एक शब्द में जवाब दो: "ANSWER" या "HELP"

जवाब:"""
        else:
            # Special prompt for location
            if parameter == "location":
                prompt = f"""User message: "{user_message}"
Question: Where is your farm located? (village, district, state)

Is the user:
A) Providing a location (like "Sonipat", "Delhi", "My village is Balgad")
B) Asking for help (like "don't know", "how to tell")

IMPORTANT: If the message contains ANY place name or location, choose "ANSWER".

Reply with ONLY ONE WORD: "ANSWER" or "HELP"

Reply:"""
            else:
                prompt = f"""User message: "{user_message}"
Question: What is the soil {parameter}?

Is the user:
A) Providing an answer (like "black", "red", "moist", "acidic")
B) Asking for help (like "don't know", "how to check", "explain")

IMPORTANT: If the message contains ANY valid answer value (color, moisture, smell, pH), choose "ANSWER".

Reply with ONLY ONE WORD: "ANSWER" or "HELP"

Reply:"""
        
        try:
            if self.provider == "groq":
                # Use Groq API
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.0,  # Deterministic for faster response
                        "max_tokens": 3,  # Just need "ANSWER" or "HELP"
                    },
                    timeout=3  # Shorter timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    classification = result["choices"][0]["message"]["content"].strip().upper()
                    
                    # Parse response
                    if "HELP" in classification:
                        return "help_request", 0.90
                    elif "ANSWER" in classification:
                        return "answer", 0.90
                    else:
                        return self._fallback_classification(user_message, language)
                else:
                    return self._fallback_classification(user_message, language)
            else:
                # Use Ollama API
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 5,
                            "top_p": 0.9,
                        }
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    classification = result.get('response', '').strip().upper()
                    
                    if "HELP" in classification:
                        return "help_request", 0.90
                    elif "ANSWER" in classification:
                        return "answer", 0.90
                    else:
                        return self._fallback_classification(user_message, language)
                else:
                    return self._fallback_classification(user_message, language)
        
        except Exception as e:
            print(f"✗ Intent classification error: {e}")
            return self._fallback_classification(user_message, language)
    
    def _fallback_classification(self, user_message: str, language: Language) -> Tuple[str, float]:
        """Fallback to keyword-based classification."""
        user_lower = user_message.lower()
        
        help_keywords_en = ["don't know", "help", "how", "explain", "guide", "steps", "not sure"]
        help_keywords_hi = ["नहीं पता", "मदद", "कैसे", "समझाओ", "बताओ"]
        
        if language == "hi":
            if any(kw in user_lower for kw in help_keywords_hi):
                return "help_request", 0.70
        else:
            if any(kw in user_lower for kw in help_keywords_en):
                return "help_request", 0.70
        
        return "answer", 0.60


# Global instance
_intent_classifier = None


def get_intent_classifier() -> IntentClassifier:
    """Get or create global intent classifier instance."""
    global _intent_classifier
    if _intent_classifier is None:
        provider = getattr(settings, 'llm_provider', 'ollama')
        if provider == "groq":
            api_key = getattr(settings, 'groq_llm_api_key', None)
            model_name = getattr(settings, 'groq_llm_model', 'llama-3.3-70b-versatile')
            _intent_classifier = IntentClassifier(provider="groq", model_name=model_name, api_key=api_key)
        else:
            model_name = getattr(settings, 'ollama_model_name', 'gemma2:9b')
            _intent_classifier = IntentClassifier(provider="ollama", model_name=model_name)
    return _intent_classifier
