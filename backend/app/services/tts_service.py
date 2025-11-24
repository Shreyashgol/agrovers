"""
Text-to-Speech (TTS) Service

Provides TTS with multiple provider support:
- gTTS (Google Text-to-Speech, free, cloud-based)
- Coqui TTS (local, high quality)
- OpenAI TTS (premium quality)

Returns audio file path for playback.
"""

import os
import hashlib
from pathlib import Path
from typing import Literal, Optional
from gtts import gTTS
from ..config import settings


class TTSService:
    """Text-to-Speech service with multiple provider support."""
    
    def __init__(self, provider: str = "gtts"):
        """
        Initialize TTS service.
        
        Args:
            provider: 'gtts', 'coqui', or 'openai'
        """
        self.provider = provider
        self.audio_dir = self._setup_audio_dir()
        self._init_provider()
    
    def _setup_audio_dir(self) -> Path:
        """Create directory for audio files."""
        # Store in backend/app/data/audio/
        backend_dir = Path(__file__).parent.parent.parent
        audio_dir = backend_dir / "app" / "data" / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)
        return audio_dir
    
    def _init_provider(self):
        """Initialize the selected TTS provider."""
        if self.provider == "gtts":
            # gTTS doesn't need initialization
            print(f"✓ Initialized gTTS")
        
        elif self.provider == "coqui":
            try:
                from TTS.api import TTS
                # Load a fast model for CPU
                self.model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
                print(f"✓ Initialized Coqui TTS")
            except ImportError:
                print("⚠️  Coqui TTS not installed. Install with: pip install TTS")
                print("   Falling back to gTTS")
                self.provider = "gtts"
        
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = getattr(settings, 'openai_api_key', None)
                if not api_key:
                    raise ValueError("OpenAI API key not found")
                self.client = OpenAI(api_key=api_key)
                print(f"✓ Initialized OpenAI TTS")
            except Exception as e:
                print(f"⚠️  OpenAI TTS initialization failed: {e}")
                print("   Falling back to gTTS")
                self.provider = "gtts"
    
    def synthesize(
        self,
        text: str,
        language: Literal["hi", "en"] = "en",
        slow: bool = False
    ) -> str:
        """
        Convert text to speech and return audio file path.
        
        Args:
            text: Text to synthesize
            language: Language code ('hi' or 'en')
            slow: Speak slowly (for gTTS)
            
        Returns:
            Relative path to audio file (e.g., 'audio/tts_abc123.mp3')
        """
        if self.provider == "gtts":
            return self._synthesize_gtts(text, language, slow)
        elif self.provider == "coqui":
            return self._synthesize_coqui(text, language)
        elif self.provider == "openai":
            return self._synthesize_openai(text, language)
        else:
            raise ValueError(f"Unknown TTS provider: {self.provider}")
    
    def _synthesize_gtts(
        self,
        text: str,
        language: str,
        slow: bool = False
    ) -> str:
        """Synthesize using gTTS."""
        try:
            # Generate unique filename based on text hash
            text_hash = hashlib.md5(f"{text}_{language}_{slow}".encode()).hexdigest()[:12]
            filename = f"tts_{text_hash}.mp3"
            filepath = self.audio_dir / filename
            
            # Check if already exists (cache)
            if filepath.exists():
                return f"audio/{filename}"
            
            # Map language codes
            lang_map = {"hi": "hi", "en": "en"}
            gtts_lang = lang_map.get(language, "en")
            
            # Generate speech
            tts = gTTS(text=text, lang=gtts_lang, slow=slow)
            tts.save(str(filepath))
            
            return f"audio/{filename}"
        
        except Exception as e:
            print(f"✗ gTTS error: {e}")
            # Return empty path on error
            return ""
    
    def _synthesize_coqui(
        self,
        text: str,
        language: str
    ) -> str:
        """Synthesize using Coqui TTS."""
        try:
            text_hash = hashlib.md5(f"{text}_{language}".encode()).hexdigest()[:12]
            filename = f"tts_{text_hash}.wav"
            filepath = self.audio_dir / filename
            
            if filepath.exists():
                return f"audio/{filename}"
            
            # Coqui TTS
            self.model.tts_to_file(text=text, file_path=str(filepath))
            
            return f"audio/{filename}"
        
        except Exception as e:
            print(f"✗ Coqui TTS error: {e}")
            return ""
    
    def _synthesize_openai(
        self,
        text: str,
        language: str
    ) -> str:
        """Synthesize using OpenAI TTS."""
        try:
            text_hash = hashlib.md5(f"{text}_{language}".encode()).hexdigest()[:12]
            filename = f"tts_{text_hash}.mp3"
            filepath = self.audio_dir / filename
            
            if filepath.exists():
                return f"audio/{filename}"
            
            # OpenAI TTS
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",  # Can be customized
                input=text
            )
            
            response.stream_to_file(str(filepath))
            
            return f"audio/{filename}"
        
        except Exception as e:
            print(f"✗ OpenAI TTS error: {e}")
            return ""
    
    def get_audio_url(self, relative_path: str, base_url: str = "http://localhost:8000") -> str:
        """
        Convert relative path to full URL.
        
        Args:
            relative_path: e.g., 'audio/tts_abc123.mp3'
            base_url: Base URL of the API
            
        Returns:
            Full URL: 'http://localhost:8000/audio/tts_abc123.mp3'
        """
        if not relative_path:
            return ""
        return f"{base_url}/{relative_path}"


# Factory function
def create_tts_service(provider: Optional[str] = None) -> TTSService:
    """
    Create TTS service with specified provider.
    
    Args:
        provider: 'gtts', 'coqui', or 'openai'. 
                  If None, uses TTS_PROVIDER from settings.
    """
    if provider is None:
        provider = getattr(settings, 'tts_provider', 'gtts')
    
    return TTSService(provider=provider)
