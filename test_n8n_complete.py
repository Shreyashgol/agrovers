#!/usr/bin/env python3
"""
Complete end-to-end test of n8n integration
"""
import requests
import time
import json

BASE_URL = "http://localhost:8001"

def test_complete_flow():
    print("="*60)
    print("🧪 Testing Complete n8n Integration Flow")
    print("="*60)
    
    # Step 1: Create session
    print("\n📝 Step 1: Creating session...")
    response = requests.post(f"{BASE_URL}/api/v1/session/start", json={"language": "en"})
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"✓ Session created: {session_id}")
    print(f"  Total steps: {session_data['total_steps']}")
    
    # Step 2: Answer all questions
    print("\n📝 Step 2: Answering all questions...")
    answers = [
        "Ramesh Kumar",
        "dark brown",
        "moist",
        "earthy",
        "6.5",
        "loamy",
        "yes",
        "Maharashtra, India",
        "NPK 10-10-10"
    ]
    
    for i, answer in enumerate(answers, 1):
        print(f"  Q{i}: {answer}")
        response = requests.post(
            f"{BASE_URL}/api/v1/session/next",
            data={"session_id": session_id, "user_text": answer}
        )
        data = response.json()
        
        if data.get("is_complete"):
            print(f"✓ Session complete after {i} questions!")
            break
        
        time.sleep(0.2)
    
    # Step 2.5: Check session data
    print("\n📝 Step 2.5: Checking session data...")
    response = requests.get(f"{BASE_URL}/api/v1/session/state/{session_id}")
    print(f"  Status code: {response.status_code}")
    if response.status_code == 200:
        session_state = response.json()
        print(f"  Current parameter: {session_state.get('current_parameter')}")
        print(f"  Is complete: {session_state.get('is_complete')}")
        answers = session_state.get('answers', {})
        filled = sum(1 for v in answers.values() if v is not None)
        print(f"  Answers filled: {filled}/{len(answers)}")
        print(f"  Answers: {json.dumps(answers, indent=4)}")
    else:
        print(f"  Error: {response.json()}")
    
    # Step 3: Generate report
    print("\n📝 Step 3: Generating report...")
    response = requests.post(
        f"{BASE_URL}/api/reports/generate",
        json={"session_id": session_id}
    )
    
    if response.status_code != 200:
        print(f"❌ Error: {response.json()}")
        return False
    
    report_response = response.json()
    print(f"✓ Report generation started")
    print(f"  Message: {report_response.get('message')}")
    
    # Step 4: Poll for status
    print("\n📝 Step 4: Polling for report status...")
    for i in range(15):
        time.sleep(1)
        response = requests.get(f"{BASE_URL}/api/reports/status/{session_id}")
        status_data = response.json()
        
        status = status_data["status"]
        progress = status_data["progress"]
        message = status_data["message"]
        
        print(f"  [{i+1}] {status.upper()} - {progress}% - {message}")
        
        if status == "completed":
            print("\n✅ Report Generated Successfully!")
            print("\n📊 Report Data:")
            report = status_data["report"]
            
            # Print summary
            if "soilAnalysis" in report:
                print(f"\n  Soil Rating: {report['soilAnalysis']['rating']}")
                print(f"  Crops: {len(report['cropRecommendations'])} recommendations")
                print(f"  Fertilizers: {len(report['fertilizerRecommendations'])} recommendations")
                
                print("\n  Sample Crop Recommendations:")
                for crop in report['cropRecommendations'][:3]:
                    print(f"    - {crop['crop']}: {crop['season']}")
            
            return True
        
        elif status == "failed":
            print(f"\n❌ Report generation failed: {message}")
            return False
    
    print("\n⏱️ Timeout waiting for report")
    return False

if __name__ == "__main__":
    success = test_complete_flow()
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ TESTS FAILED")
    print("="*60)
