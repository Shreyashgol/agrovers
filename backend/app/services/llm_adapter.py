"""
LLM Adapter for generating helper explanations.

Abstract interface allows swapping between:
- Gemini API (current)
- Local models like Llama3/Phi3 (future)

To swap LLM provider:
1. Implement new adapter class inheriting from LLMAdapter
2. Update config.py to set llm_provider
3. Update main.py to instantiate correct adapter
"""

from abc import ABC, abstractmethod
from typing import List
from ..models import Language
from ..config import settings


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters."""
    
    @abstractmethod
    def generate_helper(
        self,
        parameter: str,
        language: Language,
        user_message: str,
        retrieved_chunks: List[str],
    ) -> str:
        """
        Generate helper explanation using RAG context.
        
        Args:
            parameter: Current parameter being explained
            language: Language for response ("hi" or "en")
            user_message: Farmer's original message/question
            retrieved_chunks: Relevant chunks from RAG
            
        Returns:
            Helper text explaining how to measure the parameter
        """
        pass


class OllamaLLMAdapter(LLMAdapter):
    """
    Ollama local LLM adapter.
    
    Uses Ollama to run local models (Mistral, Llama, etc.) on your Mac.
    Much better for Hindi/English and fully offline.
    """
    
    def __init__(self, model_name: str = "mistral", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama adapter.
        
        Args:
            model_name: Model to use (e.g., "mistral", "llama2", "phi")
            base_url: Ollama API URL
        """
        self.model_name = model_name
        self.base_url = base_url
        
        # Test connection
        try:
            import requests
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                if model_name not in model_names and f"{model_name}:latest" not in model_names:
                    print(f"⚠️  Model '{model_name}' not found. Available: {model_names}")
                    print(f"   Run: ollama pull {model_name}")
                else:
                    print(f"✓ Initialized Ollama adapter with model: {model_name}")
            else:
                print(f"⚠️  Ollama not responding. Is it running?")
                print(f"   Run: ollama serve")
        except Exception as e:
            print(f"⚠️  Could not connect to Ollama: {e}")
            print(f"   Install: curl -fsSL https://ollama.com/install.sh | sh")
    
    def generate_helper(
        self,
        parameter: str,
        language: Language,
        user_message: str,
        retrieved_chunks: List[str],
    ) -> str:
        """Generate helper explanation using Ollama."""
        import requests
        
        # Build context from retrieved chunks
        context = "\n\n".join(retrieved_chunks[:3])  # Use top 3 chunks
        
        # Build structured prompt for step-by-step guidance
        param_names = {
            "color": {"hi": "रंग", "en": "color"},
            "moisture": {"hi": "नमी", "en": "moisture"},
            "smell": {"hi": "गंध", "en": "smell"},
            "ph": {"hi": "pH", "en": "pH"},
            "soil_type": {"hi": "मिट्टी का प्रकार", "en": "soil type"},
            "earthworms": {"hi": "केंचुए", "en": "earthworms"},
            "location": {"hi": "स्थान", "en": "location"},
            "fertilizer_used": {"hi": "खाद", "en": "fertilizer"},
        }
        
        param_display = param_names.get(parameter, {}).get(language, parameter)
        
        if language == "hi":
            full_prompt = f"""नीचे दिए गए संदर्भ से किसान भाई को {param_display} जांचने के 2-3 कदम बताओ:

संदर्भ:
{context}

किसान भाई, {param_display} जांचने के लिए:

कदम 1:"""
        else:
            full_prompt = f"""Using the context below, explain 2-3 steps to test {param_display}:

Context:
{context}

To test {param_display}:

Step 1:"""
        
        # Call Ollama API
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Balanced for structured output
                        "num_predict": 150,  # Allow full steps
                        "top_p": 0.85,
                        "stop": ["\n\n\n", "किसान भाई:", "Farmer:"],  # Stop at section breaks
                    }
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"✗ Ollama API error: {response.status_code}")
                return self._fallback_response(parameter, language)
        
        except Exception as e:
            print(f"✗ Ollama error: {e}")
            return self._fallback_response(parameter, language)
    
    def _fallback_response(self, parameter: str, language: Language) -> str:
        """Fallback response if Ollama fails."""
        if language == "hi":
            return f"किसान भाई, {parameter} की जांच के लिए कृपया विकल्पों में से चुनें या फिर से प्रयास करें।"
        else:
            return f"Please select from the options or try again to test {parameter}."


class GeminiLLMAdapter(LLMAdapter):
    """
    Gemini API adapter for generating helper explanations.
    
    Uses Google's Gemini API to generate contextual explanations
    based on RAG-retrieved knowledge base chunks.
    
    Supports both old (google-generativeai) and new (google-genai) packages.
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Gemini adapter.
        
        Args:
            api_key: Gemini API key
            model_name: Model to use (e.g., "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-pro-preview")
        """
        self.api_key = api_key
        self.model_name = model_name
        self.use_new_api = False
        
        try:
            # Try new API first (google-genai package)
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key)
                self.use_new_api = True
                print(f"✓ Initialized Gemini adapter (new API) with model: {model_name}")
            except ImportError:
                # Fall back to old API (google-generativeai package)
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
                self.use_new_api = False
                print(f"✓ Initialized Gemini adapter (legacy API) with model: {model_name}")
        except Exception as e:
            print(f"✗ Error initializing Gemini: {e}")
            raise
    
    def generate_helper(
        self,
        parameter: str,
        language: Language,
        user_message: str,
        retrieved_chunks: List[str],
    ) -> str:
        """Generate helper explanation using Gemini API."""
        # Build context from retrieved chunks
        context = "\n\n".join(retrieved_chunks)
        
        # Build system prompt based on language
        if language == "hi":
            system_prompt = """आप एक मिट्टी परीक्षण सहायक हैं जो भारतीय किसानों की मदद करता है। 
सरल हिंदी में बात करें, उन्हें "किसान भाई" कहकर संबोधित करें, और चरणबद्ध तरीके से समझाएं कि 
मांगे गए पैरामीटर के लिए मिट्टी का परीक्षण कैसे करें। केवल प्रदान किए गए संदर्भ का उपयोग करें 
और जानकारी का आविष्कार न करें।"""
            
            user_prompt = f"""पैरामीटर: {parameter}
किसान का संदेश: "{user_message}"

ऊपर दिए गए संदर्भ का उपयोग करते हुए, समझाएं कि किसान को घर पर इस पैरामीटर को कैसे मापना चाहिए 
और संभावित श्रेणियों का क्या अर्थ है। इसे छोटा और व्यावहारिक रखें।"""
        else:
            system_prompt = """You are a soil testing assistant for Indian farmers. 
Speak in simple English, and explain step-by-step how to test the soil for the requested parameter. 
Use only the provided context and do not invent information."""
            
            user_prompt = f"""Parameter: {parameter}
Farmer message: "{user_message}"

Using the context above, explain how the farmer should measure this parameter at home and what 
the possible categories mean. Keep it short and actionable."""
        
        # Combine into full prompt
        full_prompt = f"""{system_prompt}

Context from knowledge base:
{context}

{user_prompt}"""
        
        try:
            if self.use_new_api:
                # Use new google-genai API
                from google.genai import types
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=full_prompt)],
                    )
                ]
                
                config = types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1000,  # Increased to avoid truncation
                )
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config,
                )
                # Handle response - new API returns different structure
                # Try to get text directly first
                try:
                    if hasattr(response, 'text'):
                        text = response.text
                        if text:
                            return text.strip()
                except Exception as e:
                    print(f"DEBUG: Could not get text directly: {e}")
                
                # Try to extract from candidates
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and candidate.content:
                            content = candidate.content
                            if hasattr(content, 'parts') and content.parts:
                                parts_text = []
                                for part in content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        parts_text.append(str(part.text))
                                if parts_text:
                                    return ' '.join(parts_text).strip()
                
                # If we can't extract text, raise an error to trigger fallback
                raise ValueError(f"Could not extract text from response")
            else:
                # Use legacy google-generativeai API
                response = self.model.generate_content(full_prompt)
                return response.text.strip()
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error calling Gemini API: {error_msg}")
            
            # Check for quota/rate limit errors
            if "429" in error_msg or "quota" in error_msg.lower():
                if language == "hi":
                    return f"किसान भाई, API की सीमा पूरी हो गई है। कृपया कुछ देर बाद पुनः प्रयास करें।"
                else:
                    return f"API quota exceeded. Please try again later."
            
            # Fallback message
            if language == "hi":
                return f"माफ करें, {parameter} के बारे में जानकारी प्राप्त करने में समस्या हुई। कृपया पुनः प्रयास करें।"
            else:
                return f"Sorry, there was an issue getting information about {parameter}. Please try again."


def create_llm_adapter() -> LLMAdapter:
    """
    Factory function to create appropriate LLM adapter based on config.
    
    Returns:
        LLMAdapter instance (Gemini, Ollama, or Local)
    """
    if settings.llm_provider == "ollama":
        # Use Ollama (local LLM)
        model_name = getattr(settings, 'ollama_model_name', 'mistral')
        return OllamaLLMAdapter(model_name=model_name)
    
    elif settings.llm_provider == "gemini":
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        return GeminiLLMAdapter(
            api_key=settings.gemini_api_key,
            model_name=settings.gemini_model_name
        )
    
    elif settings.llm_provider == "local":
        # Future: llama.cpp or other local implementations
        raise NotImplementedError("Local LLM adapter not yet implemented. Use 'ollama' instead.")
    
    else:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

