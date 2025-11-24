"""
Test script for voice-enabled features.

Tests:
1. Text-only flow (existing)
2. Audio input with STT
3. TTS response generation
4. Confidence scoring
5. Enhanced validators
"""

import requests
import json
from gtts import gTTS
import tempfile
import os


API_BASE = "http://localhost:8000/api/v1"


def test_text_flow():
    """Test 1: Basic text flow (should work as before)."""
    print("\n" + "="*60)
    print("TEST 1: Text-only flow")
    print("="*60)
    
    # Start session
    response = requests.post(
        f"{API_BASE}/session/start",
        json={"language": "en"}
    )
    data = response.json()
    session_id = data["session_id"]
    print(f"✓ Session started: {session_id[:20]}...")
    print(f"  Question: {data['question']}")
    
    # Submit answer
    response = requests.post(
        f"{API_BASE}/session/next",
        data={
            "session_id": session_id,
            "user_text": "black"
        }
    )
    data = response.json()
    print(f"✓ Answer submitted")
    print(f"  Next parameter: {data['parameter']}")
    print(f"  Audit: {data.get('audit', {})}")
    
    return session_id


def test_audio_input():
    """Test 2: Audio input with STT."""
    print("\n" + "="*60)
    print("TEST 2: Audio input with STT")
    print("="*60)
    
    # Start session
    response = requests.post(
        f"{API_BASE}/session/start",
        json={"language": "hi"}
    )
    data = response.json()
    session_id = data["session_id"]
    print(f"✓ Session started (Hindi)")
    
    # Create test audio
    print("  Creating test audio...")
    tts = gTTS(text="काली मिट्टी", lang="hi")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        audio_path = f.name
        tts.save(audio_path)
    
    # Submit audio
    print("  Submitting audio...")
    with open(audio_path, "rb") as audio_file:
        response = requests.post(
            f"{API_BASE}/session/next",
            data={"session_id": session_id},
            files={"audio_file": audio_file}
        )
    
    data = response.json()
    audit = data.get('audit') or {}
    print(f"✓ Audio processed")
    print(f"  ASR confidence: {audit.get('asr_conf', 'N/A')}")
    print(f"  Validator confidence: {audit.get('validator_conf', 'N/A')}")
    print(f"  Combined confidence: {audit.get('combined_conf', 'N/A')}")
    print(f"  Next parameter: {data['parameter']}")
    
    # Cleanup
    os.unlink(audio_path)
    
    return session_id


def test_helper_mode():
    """Test 3: Helper mode with TTS response."""
    print("\n" + "="*60)
    print("TEST 3: Helper mode with TTS")
    print("="*60)
    
    # Start session
    response = requests.post(
        f"{API_BASE}/session/start",
        json={"language": "en"}
    )
    data = response.json()
    session_id = data["session_id"]
    
    # Trigger helper mode
    response = requests.post(
        f"{API_BASE}/session/next",
        data={
            "session_id": session_id,
            "user_text": "I don't know"
        }
    )
    data = response.json()
    print(f"✓ Helper mode triggered")
    print(f"  Helper mode: {data['helper_mode']}")
    print(f"  Helper text preview: {data.get('helper_text', '')[:100]}...")
    print(f"  Audio URL: {data.get('audio_url', 'None')}")
    print(f"  Audit: {data.get('audit', {})}")
    
    return session_id


def test_semantic_matching():
    """Test 4: Semantic matching with synonyms."""
    print("\n" + "="*60)
    print("TEST 4: Semantic matching")
    print("="*60)
    
    # Start session
    response = requests.post(
        f"{API_BASE}/session/start",
        json={"language": "en"}
    )
    data = response.json()
    session_id = data["session_id"]
    
    # Test with synonym
    test_inputs = [
        ("dark", "color"),
        ("गहरा", "color (Hindi)"),
        ("damp", "moisture"),
    ]
    
    for user_input, description in test_inputs:
        response = requests.post(
            f"{API_BASE}/session/start",
            json={"language": "en"}
        )
        sid = response.json()["session_id"]
        
        response = requests.post(
            f"{API_BASE}/session/next",
            data={
                "session_id": sid,
                "user_text": user_input
            }
        )
        data = response.json()
        audit = data.get('audit', {})
        
        print(f"  Input: '{user_input}' ({description})")
        print(f"    Validator conf: {audit.get('validator_conf', 'N/A')}")
        print(f"    Accepted: {not data['helper_mode']}")


def test_confidence_fusion():
    """Test 5: Confidence fusion with audio + text."""
    print("\n" + "="*60)
    print("TEST 5: Confidence fusion")
    print("="*60)
    
    # Start session
    response = requests.post(
        f"{API_BASE}/session/start",
        json={"language": "en"}
    )
    data = response.json()
    session_id = data["session_id"]
    
    # Create ambiguous audio
    print("  Creating ambiguous audio...")
    tts = gTTS(text="hmm maybe black", lang="en")
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        audio_path = f.name
        tts.save(audio_path)
    
    # Submit audio
    with open(audio_path, "rb") as audio_file:
        response = requests.post(
            f"{API_BASE}/session/next",
            data={"session_id": session_id},
            files={"audio_file": audio_file}
        )
    
    data = response.json()
    audit = data.get('audit', {})
    
    print(f"✓ Confidence fusion test")
    print(f"  ASR conf: {audit.get('asr_conf', 'N/A')}")
    print(f"  Validator conf: {audit.get('validator_conf', 'N/A')}")
    print(f"  LLM conf: {audit.get('llm_conf', 'N/A')}")
    print(f"  Combined: {audit.get('combined_conf', 'N/A')}")
    print(f"  Auto-filled: {not data['helper_mode']}")
    
    os.unlink(audio_path)


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("VOICE-ENABLED FEATURES TEST SUITE")
    print("="*60)
    
    try:
        test_text_flow()
        test_audio_input()
        test_helper_mode()
        test_semantic_matching()
        test_confidence_fusion()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
