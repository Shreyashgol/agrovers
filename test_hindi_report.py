#!/usr/bin/env python3
"""
Test Hindi report generation
"""
import requests
import time
import json

BASE_URL = "http://localhost:8001"

print("🇮🇳 Testing Hindi Report Generation\n")

# Start Hindi session
print("1️⃣ Starting Hindi session...")
response = requests.post(f"{BASE_URL}/api/v1/session/start", json={"language": "hi"})
data = response.json()
session_id = data["session_id"]
print(f"✅ Session: {session_id}")
print(f"   First question: {data['question']}\n")

# Answer in Hindi
hindi_answers = [
    "मितुल",
    "काली",
    "नम",
    "मिट्टी जैसी",
    "अम्लीय",
    "चिकनी",
    "हाँ",
    "सोनीपत, हरियाणा",
    "यूरिया"
]

for i, answer in enumerate(hindi_answers, 1):
    print(f"2️⃣.{i} जवाब: {answer}")
    response = requests.post(
        f"{BASE_URL}/api/v1/session/next",
        data={"session_id": session_id, "user_text": answer}
    )
    data = response.json()
    if data.get("is_complete"):
        print("✅ सभी प्रश्न पूर्ण!\n")
        break

# Generate report
print("3️⃣ रिपोर्ट तैयार की जा रही है...")
response = requests.post(
    f"{BASE_URL}/api/reports/generate",
    json={"session_id": session_id}
)
print("✅ रिपोर्ट जनरेशन शुरू\n")

# Wait for completion
print("4️⃣ रिपोर्ट का इंतजार...")
for i in range(90):
    response = requests.get(f"{BASE_URL}/api/reports/status/{session_id}")
    status_data = response.json()
    
    print(f"   प्रगति: {status_data['progress']}% - {status_data['message']}")
    
    if status_data["status"] == "completed":
        print("\n✅ रिपोर्ट पूर्ण!\n")
        
        report = status_data.get("report", {})
        
        # Check Hindi report
        if "hindi" in report:
            hindi_report = report['hindi']
            print("📊 हिंदी रिपोर्ट:")
            
            if 'soilAnalysis' in hindi_report:
                assessment = hindi_report['soilAnalysis'].get('assessment', '')
                print(f"\n   मिट्टी विश्लेषण (पहले 150 अक्षर):")
                print(f"   {assessment[:150]}...")
                
                # Check if it's actually in Hindi
                hindi_chars = sum(1 for c in assessment if '\u0900' <= c <= '\u097F')
                total_chars = len(assessment)
                hindi_percentage = (hindi_chars / total_chars * 100) if total_chars > 0 else 0
                
                if hindi_percentage > 30:
                    print(f"\n   ✅ रिपोर्ट हिंदी में है! ({hindi_percentage:.1f}% देवनागरी)")
                else:
                    print(f"\n   ❌ रिपोर्ट अंग्रेजी में है! ({hindi_percentage:.1f}% देवनागरी)")
            
            if 'cropRecommendations' in hindi_report:
                crops = hindi_report['cropRecommendations']
                print(f"\n   फसल सिफारिशें: {len(crops)} फसलें")
                if crops:
                    print(f"   पहली फसल: {crops[0].get('crop', 'N/A')}")
        
        # Save for inspection
        with open("test_hindi_report.json", "w", encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("\n💾 पूर्ण रिपोर्ट सहेजी गई: test_hindi_report.json")
        
        break
    elif status_data["status"] == "failed":
        print(f"\n❌ विफल: {status_data['message']}")
        break
    
    time.sleep(1)
