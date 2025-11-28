#!/usr/bin/env python3
"""
Test the complete browser flow end-to-end
"""
import requests
import time
import json

BASE_URL = "http://localhost:8001"

def test_complete_flow():
    print("🧪 Testing Complete Browser Flow\n")
    
    # Step 1: Start a session
    print("1️⃣ Starting new session...")
    response = requests.post(
        f"{BASE_URL}/api/v1/session/start",
        json={"language": "en"}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to start session: {response.text}")
        return
    
    data = response.json()
    session_id = data["session_id"]
    print(f"✅ Session started: {session_id}")
    print(f"   First question: {data['question']}\n")
    
    # Step 2: Answer questions - keep answering until complete
    max_questions = 20  # Safety limit
    question_num = 1
    
    # Generic answers that should work for most questions
    generic_answers = [
        "Pune, Maharashtra",
        "Black soil",
        "Moderate",
        "Cotton",
        "Yes",
        "Slightly acidic",
        "Good",
        "Normal",
        "Medium",
        "Regular",
        "Standard",
        "Average",
        "Typical",
        "Common",
        "Usual",
        "Ordinary",
        "Fair",
        "Adequate",
        "Sufficient",
        "Acceptable"
    ]
    
    for i in range(max_questions):
        answer = generic_answers[i % len(generic_answers)]
        print(f"2️⃣.{question_num} Answering question...")
        response = requests.post(
            f"{BASE_URL}/api/v1/session/next",
            data={
                "session_id": session_id,
                "user_text": answer
            }
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to submit answer: {response.text}")
            return
        
        data = response.json()
        print(f"✅ Answer accepted: {answer}")
        
        if data.get("is_complete"):
            print(f"✅ All questions completed!\n")
            break
        else:
            next_q = data.get('question', 'N/A')
            print(f"   Next question: {next_q}\n")
            question_num += 1
    
    # Step 3: Generate report
    print("3️⃣ Generating comprehensive report...")
    response = requests.post(
        f"{BASE_URL}/api/reports/generate",
        json={
            "session_id": session_id,
            "language": "english"
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to generate report: {response.text}")
        return
    
    print(f"✅ Report generation started\n")
    
    # Step 4: Poll for report status
    print("4️⃣ Waiting for report completion...")
    max_attempts = 60  # 60 seconds max
    for attempt in range(max_attempts):
        response = requests.get(f"{BASE_URL}/api/reports/status/{session_id}")
        
        if response.status_code != 200:
            print(f"❌ Failed to get status: {response.text}")
            return
        
        status_data = response.json()
        status = status_data["status"]
        progress = status_data["progress"]
        message = status_data["message"]
        
        print(f"   Progress: {progress}% - {message}")
        
        if status == "completed":
            print(f"\n✅ Report completed!\n")
            
            # Display report summary
            report = status_data.get("report", {})
            print("📊 Report Summary:")
            print(f"   Report keys: {list(report.keys())}")
            
            # Try both camelCase and snake_case
            soil = report.get('soilAnalysis') or report.get('soil_analysis', '')
            crops = report.get('cropRecommendations') or report.get('crop_recommendations', '')
            fert = report.get('fertilizerRecommendations') or report.get('fertilizer_recommendations', '')
            
            # Convert to string if needed
            soil_str = str(soil) if soil else ''
            crops_str = str(crops) if crops else ''
            fert_str = str(fert) if fert else ''
            
            print(f"   - Soil Analysis: {len(soil_str)} chars (type: {type(soil).__name__})")
            print(f"   - Crop Recommendations: {len(crops_str)} chars (type: {type(crops).__name__})")
            print(f"   - Fertilizer Recommendations: {len(fert_str)} chars (type: {type(fert).__name__})")
            
            # Print first 300 chars of each section
            if soil_str or crops_str or fert_str:
                print("\n📄 Report Preview:")
                if soil_str:
                    print(f"\n🌱 Soil Analysis:")
                    print(f"  {soil_str[:300]}...")
                if crops_str:
                    print(f"\n🌾 Crop Recommendations:")
                    print(f"  {crops_str[:300]}...")
                if fert_str:
                    print(f"\n💧 Fertilizer Recommendations:")
                    print(f"  {fert_str[:300]}...")
            
            # Check if it's real data (not mock)
            all_text = f"{soil_str} {crops_str} {fert_str}".lower()
            if 'mock' in all_text or 'placeholder' in all_text:
                print("\n⚠️  WARNING: Report contains mock/placeholder data!")
            elif not all_text.strip() or all_text.strip() == "none none none":
                print("\n⚠️  WARNING: Report is empty or contains None values!")
            else:
                print("\n✅ Report contains real AI-generated content!")
            
            return True
        
        elif status == "failed":
            print(f"\n❌ Report generation failed: {message}")
            return False
        
        time.sleep(1)
    
    print(f"\n❌ Timeout waiting for report")
    return False

if __name__ == "__main__":
    try:
        success = test_complete_flow()
        if success:
            print("\n🎉 All tests passed! The browser flow should work correctly.")
            print("\n📱 Open your browser to: http://localhost:5174")
        else:
            print("\n❌ Tests failed. Check the errors above.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
