"""
n8n webhook client for sending final soil test results.

Sends completed soil test data to n8n webhook URL configured in settings.

To modify:
- Change webhook URL: Update N8N_WEBHOOK_URL in .env
- Change payload format: Modify send_to_n8n() function
"""

import requests
from typing import Optional
from ..config import settings
from ..models import SoilTestResult


def send_to_n8n(result: SoilTestResult) -> tuple[bool, Optional[str]]:
    """
    Send soil test result to n8n webhook.
    
    Args:
        result: Complete SoilTestResult with all parameters filled
        
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    if not settings.n8n_webhook_url:
        return False, "N8N_WEBHOOK_URL not configured"
    
    try:
        # Convert to dict and send
        payload = result.model_dump(exclude_none=True)
        
        response = requests.post(
            settings.n8n_webhook_url,
            json=payload,
            timeout=10
        )
        
        if response.ok:
            return True, None
        else:
            return False, f"n8n returned status {response.status_code}: {response.text}"
    
    except requests.exceptions.RequestException as e:
        return False, f"Error sending to n8n: {str(e)}"

