#!/usr/bin/env python3
"""
Test report generation and check structure
"""
import requests
import time
import json

BASE_URL = "http://localhost:8001"

# Start a session and answer questions quickly
print("1️⃣ Starting session...")
response = requests.post(f"{BASE_URL}/api/v1/session/start", json={"language": "en"})
data = response.json()
session_id = data["session_id"]
print(f"✅ Session: {session_id}\n")

# Answer all questions
answers = ["Test User", "Black", "Moist", "Earthy", "Acidic", "Clay", "Yes", "Pune Maharashtra", "Urea"]

for i, answer in enumerate(answers, 1):
    print(f"2️⃣.{i} Answering: {answer}")
    response = requests.post(
        f"{BASE_URL}/api/v1/session/next",
        data={"session_id": session_id, "user_text": answer}
    )
    data = response.json()
    if data.get("is_complete"):
        print("✅ All questions completed!\n")
        break

# Generate report
print("3️⃣ Generating report...")
response = requests.post(
    f"{BASE_URL}/api/reports/generate",
    json={"session_id": session_id}
)
print(f"✅ Report generation started\n")

# Wait for completion
print("4️⃣ Waiting for report...")
for i in range(60):
    response = requests.get(f"{BASE_URL}/api/reports/status/{session_id}")
    status_data = response.json()
    
    print(f"   Progress: {status_data['progress']}% - {status_data['message']}")
    
    if status_data["status"] == "completed":
        print("\n✅ Report completed!\n")
        
        # Print report structure
        report = status_data.get("report", {})
        print("📊 Report Structure:")
        print(f"   Keys: {list(report.keys())}")
        
        if "english" in report:
            print(f"\n   English Report Keys: {list(report['english'].keys())}")
            eng = report['english']
            if 'soilAnalysis' in eng:
                print(f"   - soilAnalysis: {list(eng['soilAnalysis'].keys())}")
            if 'cropRecommendations' in eng:
                print(f"   - cropRecommendations: {len(eng['cropRecommendations'])} items")
            if 'fertilizerRecommendations' in eng:
                print(f"   - fertilizerRecommendations: {len(eng['fertilizerRecommendations'])} items")
        
        if "hindi" in report:
            print(f"\n   Hindi Report Keys: {list(report['hindi'].keys())}")
        
        # Save to file for inspection
        with open("test_report_output.json", "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("\n💾 Full report saved to: test_report_output.json")
        
        break
    elif status_data["status"] == "failed":
        print(f"\n❌ Failed: {status_data['message']}")
        break
    
    time.sleep(1)
