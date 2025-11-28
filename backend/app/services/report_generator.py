"""
AI-Powered Soil Report Generator
Generates comprehensive reports using LLM agents (no n8n needed)
"""
import asyncio
import json
import logging
from typing import Dict, Any, List
from ..config import settings
from .llm_adapter import create_llm_adapter

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates soil reports using three specialized LLM agents"""
    
    def __init__(self):
        self.llm = create_llm_adapter()
    
    async def generate_soil_analysis(self, soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent 1: Soil Analysis Expert
        Analyzes soil health and provides assessment
        """
        prompt = f"""You are a soil science expert specializing in agricultural soil analysis.

Analyze this soil data and provide a comprehensive assessment:

Soil Data:
- Color: {soil_data.get('soilColor', 'unknown')}
- Moisture: {soil_data.get('moistureLevel', 'unknown')}
- Smell: {soil_data.get('soilSmell', 'unknown')}
- pH Level: {soil_data.get('phLevel', 'unknown')}
- Soil Type: {soil_data.get('soilType', 'unknown')}
- Earthworms: {soil_data.get('earthworms', 'unknown')}
- Location: {soil_data.get('location', 'unknown')}
- Previous Fertilizers: {soil_data.get('previousFertilizers', 'none')}

Provide your analysis in this EXACT JSON format (no markdown, no extra text):
{{
  "assessment": "Detailed 3-4 sentence assessment of soil health, referencing the specific parameters above",
  "pros": ["Strength 1", "Strength 2", "Strength 3", "Strength 4", "Strength 5"],
  "cons": ["Concern 1", "Concern 2", "Concern 3"],
  "rating": "Excellent|Good|Fair|Poor"
}}

Return ONLY the JSON, nothing else."""

        try:
            response = await self.llm.generate_async(prompt, temperature=0.3)
            # Clean response
            cleaned = self._clean_json_response(response)
            result = json.loads(cleaned)
            
            # Validate
            if not all(k in result for k in ['assessment', 'pros', 'cons', 'rating']):
                raise ValueError("Missing required fields")
            
            return result
        except Exception as e:
            logger.error(f"Soil analysis error: {e}")
            # Fallback
            return {
                "assessment": f"Analysis of {soil_data.get('soilType', 'unknown')} soil with {soil_data.get('moistureLevel', 'unknown')} moisture and pH {soil_data.get('phLevel', 'unknown')}.",
                "pros": ["Soil data collected", "Ready for analysis"],
                "cons": ["Detailed analysis unavailable"],
                "rating": "Fair"
            }
    
    async def generate_crop_recommendations(self, soil_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Agent 2: Crop Recommendation Expert
        Recommends suitable crops based on soil
        """
        location = soil_data.get('location', 'India')
        soil_type = soil_data.get('soilType', 'unknown')
        ph = soil_data.get('phLevel', 'unknown')
        
        prompt = f"""You are an agricultural crop specialist with expertise in Indian farming.

Based on this soil data, recommend 6 suitable crops:

Soil Data:
- Type: {soil_type}
- pH: {ph}
- Moisture: {soil_data.get('moistureLevel', 'unknown')}
- Location: {location}
- Earthworms: {soil_data.get('earthworms', 'unknown')}

Provide recommendations in this EXACT JSON format (no markdown):
[
  {{
    "crop": "Crop Name",
    "reason": "One sentence explaining why this crop suits the soil conditions",
    "season": "Planting season (e.g., Kharif Jun-Jul, Rabi Oct-Nov)"
  }}
]

Recommend 6 crops that are:
1. Suitable for the soil type and pH
2. Appropriate for the location/climate
3. Commonly grown in India
4. Include mix of cereals, pulses, vegetables

Return ONLY the JSON array, nothing else."""

        try:
            response = await self.llm.generate_async(prompt, temperature=0.4)
            cleaned = self._clean_json_response(response)
            result = json.loads(cleaned)
            
            # Validate
            if not isinstance(result, list) or len(result) < 3:
                raise ValueError("Invalid crop recommendations")
            
            return result[:6]  # Limit to 6
        except Exception as e:
            logger.error(f"Crop recommendation error: {e}")
            # Fallback
            return [
                {"crop": "Rice", "reason": "Versatile crop suitable for various soil types", "season": "Kharif (Jun-Jul)"},
                {"crop": "Wheat", "reason": "Grows well in moderate conditions", "season": "Rabi (Oct-Nov)"},
                {"crop": "Pulses", "reason": "Nitrogen-fixing legumes improve soil", "season": "Rabi (Oct-Nov)"}
            ]
    
    async def generate_fertilizer_recommendations(
        self, 
        soil_data: Dict[str, Any],
        crops: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Agent 3: Fertilizer Expert
        Recommends fertilizers based on soil and crops
        """
        crop_names = ", ".join([c['crop'] for c in crops[:3]])
        
        prompt = f"""You are a fertilizer and soil nutrition expert.

Based on this soil data and recommended crops, provide 6 fertilizer recommendations:

Soil Data:
- Type: {soil_data.get('soilType', 'unknown')}
- pH: {soil_data.get('phLevel', 'unknown')}
- Previous Fertilizers: {soil_data.get('previousFertilizers', 'none')}
- Earthworms: {soil_data.get('earthworms', 'unknown')}

Recommended Crops: {crop_names}

Provide recommendations in this EXACT JSON format (no markdown):
[
  {{
    "fertilizer": "Fertilizer Name",
    "type": "Organic|Chemical",
    "application": "Application rate with units (e.g., 5-10 tonnes per acre)",
    "timing": "When to apply (e.g., 2-3 weeks before sowing)",
    "purpose": "Why this fertilizer is recommended for these conditions"
  }}
]

Include:
- 2-3 organic options (FYM, compost, bio-fertilizers)
- 3-4 chemical options (NPK, urea, DAP, micronutrients)
- Specific application rates
- Clear timing instructions

Return ONLY the JSON array, nothing else."""

        try:
            response = await self.llm.generate_async(prompt, temperature=0.4)
            cleaned = self._clean_json_response(response)
            result = json.loads(cleaned)
            
            # Validate
            if not isinstance(result, list) or len(result) < 3:
                raise ValueError("Invalid fertilizer recommendations")
            
            return result[:6]  # Limit to 6
        except Exception as e:
            logger.error(f"Fertilizer recommendation error: {e}")
            # Fallback
            return [
                {
                    "fertilizer": "Farmyard Manure (FYM)",
                    "type": "Organic",
                    "application": "5-10 tonnes per acre",
                    "timing": "2-3 weeks before sowing",
                    "purpose": "Improves soil structure and provides slow-release nutrients"
                },
                {
                    "fertilizer": "NPK 10-10-10",
                    "type": "Chemical",
                    "application": "50-100 kg per acre",
                    "timing": "At sowing and top-dressing",
                    "purpose": "Provides balanced primary nutrients"
                }
            ]
    
    def _clean_json_response(self, text: str) -> str:
        """Clean LLM response to extract valid JSON"""
        # Remove markdown code blocks
        text = text.strip()
        if text.startswith('```'):
            # Remove ```json or ``` at start
            text = text.split('\n', 1)[1] if '\n' in text else text[3:]
        if text.endswith('```'):
            text = text.rsplit('\n', 1)[0] if '\n' in text else text[:-3]
        
        # Remove common prefixes
        for prefix in ['Output:', 'Answer:', 'Result:', 'JSON:']:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Find JSON object or array
        start_obj = text.find('{')
        start_arr = text.find('[')
        
        if start_obj == -1 and start_arr == -1:
            return text
        
        if start_obj != -1 and (start_arr == -1 or start_obj < start_arr):
            # Object
            end = text.rfind('}')
            if end != -1:
                return text[start_obj:end+1]
        else:
            # Array
            end = text.rfind(']')
            if end != -1:
                return text[start_arr:end+1]
        
        return text.strip()
    
    async def generate_complete_report(self, soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete report by running all three agents in parallel
        """
        logger.info(f"Generating report for session: {soil_data.get('id')}")
        
        try:
            # Run all three agents in parallel
            soil_analysis_task = self.generate_soil_analysis(soil_data)
            crop_recommendations_task = self.generate_crop_recommendations(soil_data)
            
            # Wait for soil and crops first
            soil_analysis, crop_recommendations = await asyncio.gather(
                soil_analysis_task,
                crop_recommendations_task
            )
            
            # Then generate fertilizer recommendations based on crops
            fertilizer_recommendations = await self.generate_fertilizer_recommendations(
                soil_data,
                crop_recommendations
            )
            
            # Compile final report
            report = {
                "soilAnalysis": soil_analysis,
                "cropRecommendations": crop_recommendations,
                "fertilizerRecommendations": fertilizer_recommendations
            }
            
            logger.info("Report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise


# Singleton instance
report_generator = ReportGenerator()
