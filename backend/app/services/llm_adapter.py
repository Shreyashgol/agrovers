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
    
    async def generate_async(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Generate text asynchronously (for report generation).
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Generated text
        """
        # Default implementation - subclasses should override for true async
        return self.generate_sync(prompt, temperature)
    
    def generate_sync(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Generate text synchronously.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Generated text
        """
        raise NotImplementedError("Subclass must implement generate_sync")


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
            # Check if this is a follow-up question
            if "step" in user_message.lower() or "कदम" in user_message.lower() or "problem" in user_message.lower():
                full_prompt = f"""किसान का सवाल: "{user_message}"

संदर्भ:
{context}

किसान को {param_display} के बारे में उनके सवाल का जवाब दो। अगर वे किसी खास कदम के बारे में पूछ रहे हैं, तो उस कदम को विस्तार से समझाओ।

जवाब:"""
            else:
                full_prompt = f"""नीचे दिए गए संदर्भ का उपयोग करके किसान भाई को {param_display} जांचने में मदद करो।

संदर्भ:
{context}

ऊपर दी गई जानकारी से किसान को {param_display} जांचने के लिए सभी कदम एक साथ बताओ। सभी कदमों को पूरा करो, बीच में मत रुको।

किसान भाई, {param_display} जांचने के लिए ये सभी कदम अपनाएं:

कदम 1:"""
        else:
            # Check if this is a follow-up question
            if "step" in user_message.lower() or "problem" in user_message.lower() or "after" in user_message.lower():
                full_prompt = f"""Farmer's question: "{user_message}"

Context:
{context}

Answer the farmer's specific question about {param_display}. If they're asking about a specific step, explain that step in more detail.

Answer:"""
            else:
                full_prompt = f"""Help the farmer test {param_display} using the context below.

Context:
{context}

Based on the information above, provide ALL steps together to test {param_display}. Complete all steps, don't stop in the middle.

To test {param_display}, follow ALL these steps:

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
                        "temperature": 0.4,  # Slightly higher for more helpful responses
                        "num_predict": 400,  # Allow more detailed steps (increased)
                        "top_p": 0.9,
                        "top_k": 40,
                        "repeat_penalty": 1.1,
                        "stop": ["Let me know", "let me know", "मुझे बताएं", "अगर आप", "if you'd like"],  # Stop at asking for more
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

महत्वपूर्ण नियम:
1. केवल और केवल प्रदान किए गए संदर्भ का उपयोग करें
2. कोई भी जानकारी का आविष्कार न करें - यह सख्त मना है
3. यदि संदर्भ सीमित है, तो उपलब्ध जानकारी से सरल मार्गदर्शन दें
4. सरल हिंदी में बात करें और "किसान भाई" कहकर संबोधित करें
5. विस्तृत कदम-दर-कदम निर्देश दें (3-5 कदम)
6. हर कदम को "कदम 1:", "कदम 2:" से शुरू करें"""
            
            user_prompt = f"""पैरामीटर: {parameter}
किसान का संदेश: "{user_message}"

केवल ऊपर दिए गए संदर्भ का उपयोग करते हुए, किसान को घर पर {parameter} कैसे जांचना है यह विस्तार से समझाएं। 
हर कदम को स्पष्ट रूप से बताएं। संदर्भ में न दी गई जानकारी न जोड़ें।

किसान भाई, {parameter} जांचने के लिए:"""
        else:
            system_prompt = """You are a soil testing assistant for Indian farmers. 

CRITICAL RULES:
1. Use ONLY and EXCLUSIVELY the provided context
2. Do NOT invent ANY information - this is strictly forbidden
3. If context is limited, provide simple guidance based on what's available
4. Speak in simple English
5. Provide detailed step-by-step instructions (3-5 steps)
6. Start each step with "Step 1:", "Step 2:", etc."""
            
            user_prompt = f"""Parameter: {parameter}
Farmer message: "{user_message}"

Using ONLY the context above, explain in detail how to test {parameter} at home. 
Provide clear, actionable steps. Do NOT add information not in the context.

To test {parameter}:"""
        
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
                    temperature=0.5,  # Lower for more consistent steps
                    max_output_tokens=1500,  # More tokens for detailed steps
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


class GroqLLMAdapter(LLMAdapter):
    """
    Groq API adapter for fast LLM inference.
    
    Uses Groq's ultra-fast inference for helper mode, intent classification, and answer extraction.
    Much faster than local models and suitable for production deployment.
    """
    
    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        """
        Initialize Groq adapter.
        
        Args:
            api_key: Groq API key
            model_name: Model to use (llama-3.3-70b-versatile, mixtral-8x7b-32768, etc.)
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        print(f"✓ Initialized Groq LLM adapter with model: {model_name}")
    
    def generate_helper(
        self,
        parameter: str,
        language: Language,
        user_message: str,
        retrieved_chunks: List[str],
    ) -> str:
        """Generate helper explanation using Groq API."""
        import requests
        
        # Build context from retrieved chunks
        context = "\n\n".join(retrieved_chunks[:5])  # Use top 5 chunks
        
        # Build system prompt
        if language == "hi":
            system_prompt = """आप एक मिट्टी परीक्षण सहायक हैं जो भारतीय किसानों की मदद करता है। 

महत्वपूर्ण नियम:
1. केवल और केवल प्रदान किए गए संदर्भ का उपयोग करें
2. कोई भी जानकारी का आविष्कार न करें - यह सख्त मना है
3. यदि संदर्भ सीमित है, तो उपलब्ध जानकारी से सरल मार्गदर्शन दें
4. सरल हिंदी में बात करें और "किसान भाई" कहकर संबोधित करें
5. विस्तृत कदम-दर-कदम निर्देश दें (3-5 कदम)
6. हर कदम को "कदम 1:", "कदम 2:" से शुरू करें"""
            
            # Check if this is a follow-up question
            if "step" in user_message.lower() or "कदम" in user_message.lower() or "problem" in user_message.lower():
                user_prompt = f"""किसान का सवाल: "{user_message}"

संदर्भ:
{context}

किसान को {parameter} के बारे में उनके सवाल का जवाब दो। अगर वे किसी खास कदम के बारे में पूछ रहे हैं, तो उस कदम को विस्तार से समझाओ।

जवाब:"""
            else:
                user_prompt = f"""पैरामीटर: {parameter}
किसान का संदेश: "{user_message}"

संदर्भ:
{context}

केवल ऊपर दिए गए संदर्भ का उपयोग करते हुए, किसान को घर पर {parameter} कैसे जांचना है यह विस्तार से समझाएं। 
हर कदम को स्पष्ट रूप से बताएं। संदर्भ में न दी गई जानकारी न जोड़ें।

किसान भाई, {parameter} जांचने के लिए:"""
        else:
            system_prompt = """You are a soil testing assistant for Indian farmers. 

CRITICAL RULES:
1. Use ONLY and EXCLUSIVELY the provided context
2. Do NOT invent ANY information - this is strictly forbidden
3. If context is limited, provide simple guidance based on what's available
4. Speak in simple English
5. Provide detailed step-by-step instructions (3-5 steps)
6. Start each step with "Step 1:", "Step 2:", etc."""
            
            # Check if this is a follow-up question
            if "step" in user_message.lower() or "problem" in user_message.lower() or "after" in user_message.lower():
                user_prompt = f"""Farmer's question: "{user_message}"

Context:
{context}

Answer the farmer's specific question about {parameter}. If they're asking about a specific step, explain that step in more detail.

Answer:"""
            else:
                user_prompt = f"""Parameter: {parameter}
Farmer message: "{user_message}"

Context:
{context}

Using ONLY the context above, explain in detail how to test {parameter} at home. 
Provide clear, actionable steps. Do NOT add information not in the context.

To test {parameter}:"""
        
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 1500,
                    "top_p": 0.9,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"✗ Groq API error: {response.status_code} - {response.text}")
                return self._fallback_response(parameter, language)
        
        except Exception as e:
            print(f"✗ Groq error: {e}")
            return self._fallback_response(parameter, language)
    
    def _fallback_response(self, parameter: str, language: Language) -> str:
        """Fallback response if Groq fails."""
        if language == "hi":
            return f"किसान भाई, {parameter} की जांच के लिए कृपया विकल्पों में से चुनें या फिर से प्रयास करें।"
        else:
            return f"Please select from the options or try again to test {parameter}."
    
    def generate_sync(self, prompt: str, temperature: float = 0.3) -> str:
        """Generate text synchronously using Groq API."""
        import requests
        
        try:
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
                    "temperature": temperature,
                    "max_tokens": 2000,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                raise Exception(f"Groq API error: {response.status_code}")
        
        except Exception as e:
            print(f"✗ Groq generation error: {e}")
            raise
    
    async def generate_async(self, prompt: str, temperature: float = 0.3) -> str:
        """Generate text asynchronously using Groq API."""
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
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
                        "temperature": temperature,
                        "max_tokens": 2000,
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    raise Exception(f"Groq API error: {response.status_code}")
        
        except Exception as e:
            print(f"✗ Groq async generation error: {e}")
            raise


def create_llm_adapter() -> LLMAdapter:
    """
    Factory function to create appropriate LLM adapter based on config.
    
    Returns:
        LLMAdapter instance (Groq, Gemini, Ollama, or Local)
    """
    if settings.llm_provider == "groq":
        # Use Groq (fast cloud LLM)
        if not settings.groq_llm_api_key:
            raise ValueError("GROQ_LLM_API_KEY not set in environment")
        return GroqLLMAdapter(
            api_key=settings.groq_llm_api_key,
            model_name=settings.groq_llm_model
        )
    
    elif settings.llm_provider == "ollama":
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

