"""
Test script for n8n integration
"""
import asyncio
import json
from app.services.n8n_service import n8n_service

async def test_n8n():
    """Test n8n webhook integration"""
    
    # Sample soil data
    test_data = {
        "id": "test-session-123",
        "name": "Ramesh Kumar",
        "soil_color": "dark brown",
        "moisture_level": "moist",
        "soil_smell": "earthy",
        "ph_level": "6.5",
        "soil_type": "loamy",
        "earthworms": "yes",
        "location": "Maharashtra, India",
        "previous_fertilizers": "NPK 10-10-10",
        "preferred_language": "English"
    }
    
    print("Testing n8n integration...")
    print(f"Webhook URL: {n8n_service.n8n_webhook_url}")
    print(f"\nSending data:")
    print(json.dumps(test_data, indent=2))
    print("\n" + "="*50)
    
    result = await n8n_service.generate_soil_report(test_data)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))
    
    if result["success"]:
        print("\n✅ n8n integration test PASSED!")
        print("\nReport data:")
        print(json.dumps(result["report"], indent=2))
    else:
        print("\n❌ n8n integration test FAILED!")
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_n8n())
