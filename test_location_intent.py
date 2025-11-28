#!/usr/bin/env python3
"""
Test location intent classification
"""
import sys
sys.path.insert(0, 'backend')

from backend.app.services.intent_classifier import IntentClassifier
from backend.app.config import settings

# Initialize classifier
classifier = IntentClassifier(
    provider="groq",
    model_name="llama-3.3-70b-versatile",
    api_key=settings.groq_llm_api_key
)

# Test cases
test_cases = [
    ("नई दिल्ली गाओं में", "location", "hi"),
    ("मेरा गाउं सोनीपत बालगड में है", "location", "hi"),
    ("मेरा गाउं सोनीपत बालगड में स्थित है", "location", "hi"),
    ("Pune, Maharashtra", "location", "en"),
    ("My village is in Sonipat", "location", "en"),
    ("नहीं पता", "location", "hi"),
    ("don't know", "location", "en"),
]

print("🧪 Testing Location Intent Classification\n")

for message, parameter, language in test_cases:
    intent, confidence = classifier.classify_intent(message, parameter, language)
    status = "✅" if intent == "answer" else "❌"
    print(f"{status} '{message}'")
    print(f"   Intent: {intent}, Confidence: {confidence:.2f}")
    print()

print("\n✅ Expected: All location answers should be classified as 'answer'")
print("❌ Only 'नहीं पता' and 'don't know' should be 'help_request'")
