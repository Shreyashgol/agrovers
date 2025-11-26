"""
LLM-Based Answer Extractor

Uses LLM to intelligently extract answers from natural conversation.
This allows farmers to speak naturally instead of giving exact keywords.

Examples:
- "मेरी मिट्टी काली है" → extracts "black"
- "I don't know how to check the color" → extracts None (help needed)
- "It looks dark, almost black" → extracts "black"
"""

from typing import Optional, Tuple
from ..models import Language
from ..config import settings
import re


class AnswerExtractor:
    """Extracts structured answers from natural language using LLM."""
    
    def __init__(self, llm_provider: str = "ollama"):
        """Initialize answer extractor with LLM."""
        self.llm_provider = llm_provider
        
        if llm_provider == "ollama":
            self.base_url = "http://localhost:11434"
            self.model_name = getattr(settings, 'ollama_model_name', 'llama3.2')
            print(f"✓ Answer extractor initialized with Ollama ({self.model_name})")
        elif llm_provider == "gemini":
            self.api_key = settings.gemini_api_key
            self.model_name = settings.gemini_model_name
            print(f"✓ Answer extractor initialized with Gemini ({self.model_name})")
    
    def extract_answer(
        self,
        user_message: str,
        parameter: str,
        language: Language,
        expected_values: list[str]
    ) -> Tuple[Optional[str], float]:
        """
        Extract answer from natural language message.
        
        Args:
            user_message: What the farmer said
            parameter: Current parameter (color, moisture, etc.)
            language: Language code
            expected_values: List of valid values (e.g., ["black", "red", "brown"])
            
        Returns:
            Tuple of (extracted_value, confidence)
            - extracted_value: One of expected_values or None
            - confidence: 0.0-1.0 confidence score
        """
        # Build extraction prompt
        prompt = self._build_extraction_prompt(
            user_message, parameter, language, expected_values
        )
        
        # Call LLM
        if self.llm_provider == "ollama":
            return self._extract_with_ollama(prompt, expected_values)
        elif self.llm_provider == "gemini":
            return self._extract_with_gemini(prompt, expected_values)
        else:
            return None, 0.0
    
    def _build_extraction_prompt(
        self,
        user_message: str,
        parameter: str,
        language: Language,
        expected_values: list[str]
    ) -> str:
        """Build prompt for answer extraction."""
        values_str = ", ".join(expected_values)
        
        if language == "hi":
            prompt = f"""किसान ने कहा: "{user_message}"

प्रश्न: मिट्टी का {parameter} क्या है?
संभावित उत्तर: {values_str}

निर्देश: किसान के संदेश से सही उत्तर निकालें। केवल एक शब्द में जवाब दें।
यदि किसान को नहीं पता या मदद चाहिए, तो "HELP" लिखें।
यदि कोई उत्तर नहीं मिला, तो "NONE" लिखें।

उत्तर:"""
        else:
            prompt = f"""Farmer said: "{user_message}"

Question: What is the soil {parameter}?
Possible answers: {values_str}

Instructions: Extract the correct answer from the farmer's message. Reply with ONLY ONE WORD.
If the farmer doesn't know or needs help, write "HELP".
If no answer found, write "NONE".

Answer:"""
        
        return prompt
    
    def _extract_with_ollama(
        self,
        prompt: str,
        expected_values: list[str]
    ) -> Tuple[Optional[str], float]:
        """Extract answer using Ollama."""
        import requests
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Very low for extraction
                        "num_predict": 10,  # Short response
                        "top_p": 0.9,
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result.get('response', '').strip().lower()
                
                # Parse response
                return self._parse_extraction(extracted_text, expected_values)
            else:
                print(f"✗ Ollama extraction error: {response.status_code}")
                return None, 0.0
        
        except Exception as e:
            print(f"✗ Ollama extraction error: {e}")
            return None, 0.0
    
    def _extract_with_gemini(
        self,
        prompt: str,
        expected_values: list[str]
    ) -> Tuple[Optional[str], float]:
        """Extract answer using Gemini."""
        try:
            # Try new API first
            try:
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=self.api_key)
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)],
                    )
                ]
                
                config = types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=20,
                )
                
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config,
                )
                
                # Extract text
                if hasattr(response, 'text'):
                    extracted_text = response.text.strip().lower()
                else:
                    # Try candidates
                    extracted_text = ""
                    if hasattr(response, 'candidates') and response.candidates:
                        for candidate in response.candidates:
                            if hasattr(candidate, 'content') and candidate.content:
                                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                    for part in candidate.content.parts:
                                        if hasattr(part, 'text'):
                                            extracted_text += str(part.text)
                    extracted_text = extracted_text.strip().lower()
                
                return self._parse_extraction(extracted_text, expected_values)
            
            except ImportError:
                # Fall back to old API
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(self.model_name)
                
                response = model.generate_content(prompt)
                extracted_text = response.text.strip().lower()
                
                return self._parse_extraction(extracted_text, expected_values)
        
        except Exception as e:
            print(f"✗ Gemini extraction error: {e}")
            return None, 0.0
    
    def _parse_extraction(
        self,
        extracted_text: str,
        expected_values: list[str]
    ) -> Tuple[Optional[str], float]:
        """Parse LLM extraction response."""
        # Remove quotes, punctuation
        extracted_text = re.sub(r'["\'\.,!?]', '', extracted_text).strip()
        
        # Check for help indicators
        if "help" in extracted_text or "none" in extracted_text:
            return None, 0.0
        
        # Try exact match first
        for value in expected_values:
            if value.lower() == extracted_text:
                return value, 0.95  # High confidence
        
        # Try partial match
        for value in expected_values:
            if value.lower() in extracted_text or extracted_text in value.lower():
                return value, 0.85  # Good confidence
        
        # No match found
        return None, 0.0


# Global instance
_answer_extractor: Optional[AnswerExtractor] = None


def get_answer_extractor() -> AnswerExtractor:
    """Get or create global answer extractor instance."""
    global _answer_extractor
    if _answer_extractor is None:
        llm_provider = getattr(settings, 'llm_provider', 'ollama')
        _answer_extractor = AnswerExtractor(llm_provider=llm_provider)
    return _answer_extractor
