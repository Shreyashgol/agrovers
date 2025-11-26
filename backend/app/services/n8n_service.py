"""
n8n Integration Service
Handles communication with n8n workflow for soil report generation
"""
import httpx
import json
import logging
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger(__name__)

class N8NService:
    def __init__(self):
        self.n8n_webhook_url = settings.n8n_webhook_url
        self.timeout = 120.0  # 2 minutes timeout for report generation
        
    async def generate_soil_report(self, soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send soil test data to n8n and receive generated report
        
        Args:
            soil_data: Dictionary containing all soil test parameters
            
        Returns:
            Dictionary containing the parsed report data
        """
        try:
            logger.info(f"Sending data to n8n webhook: {self.n8n_webhook_url}")
            
            # Prepare payload for n8n - exact format as specified
            payload = {
                "id": soil_data.get("id", ""),
                "name": soil_data.get("name", ""),
                "soilColor": soil_data.get("soilColor", ""),
                "moistureLevel": soil_data.get("moistureLevel", ""),
                "soilSmell": soil_data.get("soilSmell", ""),
                "phLevel": soil_data.get("phLevel", ""),
                "soilType": soil_data.get("soilType", ""),
                "earthworms": soil_data.get("earthworms", ""),
                "location": soil_data.get("location", ""),
                "previousFertilizers": soil_data.get("previousFertilizers", ""),
                "preferredLanguage": soil_data.get("preferredLanguage", "English")
            }
            
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.n8n_webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                response.raise_for_status()
                
                # Parse response
                report_data = response.json()
                logger.info("Successfully received report from n8n")
                
                return {
                    "success": True,
                    "report": report_data
                }
                
        except httpx.TimeoutException:
            logger.error("Timeout while waiting for n8n response")
            return {
                "success": False,
                "error": "Report generation timed out. Please try again."
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from n8n: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"Failed to generate report: {e.response.status_code}"
            }
        except Exception as e:
            logger.error(f"Error communicating with n8n: {str(e)}")
            return {
                "success": False,
                "error": f"An error occurred: {str(e)}"
            }
    
    def parse_report_text(self, report_text: str) -> Dict[str, Any]:
        """
        Parse text report into structured JSON format
        Handles various report formats from n8n
        """
        try:
            # If already JSON, parse it
            if report_text.strip().startswith('{'):
                return json.loads(report_text)
            
            # Otherwise, structure the text report
            return {
                "type": "text_report",
                "content": report_text,
                "sections": self._extract_sections(report_text)
            }
        except json.JSONDecodeError:
            # Fallback to text format
            return {
                "type": "text_report",
                "content": report_text,
                "sections": self._extract_sections(report_text)
            }
    
    def _extract_sections(self, text: str) -> list:
        """Extract sections from text report"""
        sections = []
        current_section = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a heading (all caps or ends with :)
            if line.isupper() or line.endswith(':'):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "title": line.rstrip(':'),
                    "content": []
                }
            elif current_section:
                current_section["content"].append(line)
        
        if current_section:
            sections.append(current_section)
        
        return sections

# Singleton instance
n8n_service = N8NService()
