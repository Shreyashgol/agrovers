"""
Speech-to-Text (STT) Service

Provides ASR (Automatic Speech Recognition) with multiple provider support:
- Groq Whisper API (fast, cloud-based)
- Local Whisper (free, CPU-based)
- OpenAI Whisper API (fallback)

Returns ASRResult with text, confidence, and detected language.
"""

import os
import tempfile
from typing import Optional, Literal
from pydantic import BaseModel
from ..config import settings


class ASRResult(BaseModel):
    """Result from speech-to-text conversion."""
    text: str
    asr_confidence: float  # 0.0 to 1.0
    detected_language: Optional[str] = None  # 'hi', 'en', etc.
    provider: str  # which ASR was used


class STTService:
    """Speech-to-Text service with multiple provider support."""
    
    def __init__(self, provider: str = "groq"):
        """
        Initialize STT service.
        
        Args:
            provider: 'groq', 'local_whisper', or 'openai'
        """
        self.provider = provider
        self._init_provider()
    
    def _init_provider(self):
        """Initialize the selected ASR provider."""
        if self.provider == "groq":
            try:
                from groq import Groq
                api_key = getattr(settings, 'groq_api_key', None)
                if not api_key:
                    print("⚠️  Groq API key not found, falling back to local Whisper")
                    self.provider = "local_whisper"
                    self._init_provider()
                    return
                self.client = Groq(api_key=api_key)
                print(f"✓ Initialized Groq STT")
            except Exception as e:
                print(f"⚠️  Groq initialization failed: {e}, falling back to local Whisper")
                self.provider = "local_whisper"
                self._init_provider()
        
        elif self.provider == "local_whisper":
            try:
                import whisper
                # Load tiny model for speed on CPU
                self.model = whisper.load_model("tiny")
                print(f"✓ Initialized local Whisper (tiny model)")
            except ImportError:
                print("⚠️  Whisper not installed. Install with: pip install openai-whisper")
                raise
        
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = getattr(settings, 'openai_api_key', None)
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                self.client = OpenAI(api_key=api_key)
                print(f"✓ Initialized OpenAI STT")
            except Exception as e:
                print(f"✗ OpenAI initialization failed: {e}")
                raise
    
    def transcribe(
        self,
        audio_bytes: bytes,
        language: Optional[Literal["hi", "en"]] = None
    ) -> ASRResult:
        """
        Transcribe audio to text.
        
        Args:
            audio_bytes: Audio file bytes (wav, mp3, etc.)
            language: Expected language ('hi' or 'en'), helps improve accuracy
            
        Returns:
            ASRResult with transcription and confidence
        """
        if self.provider == "groq":
            return self._transcribe_groq(audio_bytes, language)
        elif self.provider == "local_whisper":
            return self._transcribe_local(audio_bytes, language)
        elif self.provider == "openai":
            return self._transcribe_openai(audio_bytes, language)
        else:
            raise ValueError(f"Unknown ASR provider: {self.provider}")
    
    def _transcribe_groq(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None
    ) -> ASRResult:
        """Transcribe using Groq Whisper API."""
        try:
            # Save to temp file (Groq requires file)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name
            
            try:
                # Call Groq Whisper
                with open(temp_path, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-large-v3",
                        language=self._map_language(language) if language else None,
                        response_format="verbose_json"
                    )
                
                # Extract confidence from segments if available
                confidence = self._estimate_confidence_groq(transcription)
                
                return ASRResult(
                    text=transcription.text.strip(),
                    asr_confidence=confidence,
                    detected_language=language or transcription.language if hasattr(transcription, 'language') else None,
                    provider="groq"
                )
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        except Exception as e:
            print(f"✗ Groq transcription error: {e}")
            # Return low confidence result
            return ASRResult(
                text="",
                asr_confidence=0.0,
                detected_language=language,
                provider="groq_error"
            )
    
    def _transcribe_local(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None
    ) -> ASRResult:
        """Transcribe using local Whisper model."""
        try:
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name
            
            try:
                # Transcribe with Whisper
                result = self.model.transcribe(
                    temp_path,
                    language=self._map_language(language) if language else None,
                    fp16=False  # CPU mode
                )
                
                # Calculate confidence from log probabilities
                confidence = self._estimate_confidence_local(result)
                
                return ASRResult(
                    text=result["text"].strip(),
                    asr_confidence=confidence,
                    detected_language=result.get("language", language),
                    provider="local_whisper"
                )
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        except Exception as e:
            print(f"✗ Local Whisper error: {e}")
            return ASRResult(
                text="",
                asr_confidence=0.0,
                detected_language=language,
                provider="local_whisper_error"
            )
    
    def _transcribe_openai(
        self,
        audio_bytes: bytes,
        language: Optional[str] = None
    ) -> ASRResult:
        """Transcribe using OpenAI Whisper API."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio_bytes)
                temp_path = temp_audio.name
            
            try:
                with open(temp_path, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-1",
                        language=self._map_language(language) if language else None
                    )
                
                # OpenAI doesn't provide confidence, estimate as high
                return ASRResult(
                    text=transcription.text.strip(),
                    asr_confidence=0.85,  # Assume high confidence for OpenAI
                    detected_language=language,
                    provider="openai"
                )
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        
        except Exception as e:
            print(f"✗ OpenAI transcription error: {e}")
            return ASRResult(
                text="",
                asr_confidence=0.0,
                detected_language=language,
                provider="openai_error"
            )
    
    def _map_language(self, lang: Optional[str]) -> Optional[str]:
        """Map our language codes to Whisper language codes."""
        if not lang:
            return None
        # Groq uses ISO 639-1 codes (hi, en), not full names
        mapping = {
            "hi": "hi",
            "en": "en"
        }
        return mapping.get(lang, lang)
    
    def _estimate_confidence_groq(self, transcription) -> float:
        """Estimate confidence from Groq response."""
        # Groq verbose_json includes segments with confidence-like metrics
        try:
            if hasattr(transcription, 'segments') and transcription.segments:
                # Average no_speech_prob across segments (lower is better)
                avg_no_speech = sum(
                    seg.get('no_speech_prob', 0.5) 
                    for seg in transcription.segments
                ) / len(transcription.segments)
                confidence = 1.0 - avg_no_speech
                return max(0.0, min(1.0, confidence))
        except:
            pass
        
        # Default: if text is non-empty, assume decent confidence
        if hasattr(transcription, 'text') and transcription.text.strip():
            return 0.75
        return 0.5
    
    def _estimate_confidence_local(self, result: dict) -> float:
        """Estimate confidence from local Whisper result."""
        try:
            # Use average log probability from segments
            if "segments" in result and result["segments"]:
                avg_logprob = sum(
                    seg.get("avg_logprob", -1.0) 
                    for seg in result["segments"]
                ) / len(result["segments"])
                
                # Convert log prob to confidence (rough heuristic)
                # avg_logprob typically ranges from -1.0 (good) to -3.0 (poor)
                confidence = max(0.0, min(1.0, (avg_logprob + 3.0) / 2.0))
                return confidence
        except:
            pass
        
        # Default confidence based on text length
        text_len = len(result.get("text", "").strip())
        if text_len > 10:
            return 0.75
        elif text_len > 3:
            return 0.60
        return 0.40


# Factory function
def create_stt_service(provider: Optional[str] = None) -> STTService:
    """
    Create STT service with specified provider.
    
    Args:
        provider: 'groq', 'local_whisper', or 'openai'. 
                  If None, uses ASR_PROVIDER from settings.
    """
    if provider is None:
        provider = getattr(settings, 'asr_provider', 'groq')
    
    return STTService(provider=provider)
