#!/usr/bin/env python3
"""
Test response speed
"""
import requests
import time

BASE_URL = "http://localhost:8001"

print("🚀 Testing Response Speed\n")

# Start session
print("1️⃣ Starting session...")
start = time.time()
response = requests.post(f"{BASE_URL}/api/v1/session/start", json={"language": "hi"})
data = response.json()
session_id = data["session_id"]
elapsed = time.time() - start
print(f"✅ Session started in {elapsed:.2f}s\n")

# Test name answer (should be fast now)
print("2️⃣ Testing name answer: 'मेरा नाम मितुल है'")
start = time.time()
response = requests.post(
    f"{BASE_URL}/api/v1/session/next",
    data={"session_id": session_id, "user_text": "मेरा नाम मितुल है"}
)
data = response.json()
elapsed = time.time() - start

print(f"   Response time: {elapsed:.2f}s")
print(f"   Helper mode: {data.get('helper_mode', False)}")
print(f"   Next question: {data.get('question', 'N/A')[:50]}...")

if data.get('helper_mode'):
    print("   ❌ PROBLEM: Entered helper mode for name!")
else:
    print("   ✅ Correctly accepted name and moved forward")

print(f"\n⏱️  Total time: {elapsed:.2f}s (should be < 2s)")
