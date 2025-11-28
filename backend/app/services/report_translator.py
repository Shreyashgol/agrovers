"""
Report Translation Service
Translates English reports to Hindi using LLM
"""
import logging
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from ..config import settings

logger = logging.getLogger(__name__)


class ReportTranslator:
    """Translates soil reports from English to Hindi"""
    
    def __init__(self):
        """Initialize translation agent"""
        self.translator = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.groq_llm_api_key,
            temperature=0.2,  # Low temperature for consistent translation
            max_tokens=3000
        )
        logger.info("✓ Initialized Report Translator")
    
    async def translate_soil_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Translate soil analysis section to Hindi"""
        
        system_prompt = """You are a professional translator specializing in agricultural content.
Translate the following soil analysis from English to Hindi.

IMPORTANT:
- Maintain the exact JSON structure
- Translate all text content to natural, farmer-friendly Hindi
- Keep technical terms understandable
- Preserve the meaning and tone
- Return ONLY the translated JSON, no markdown or explanations"""

        user_prompt = f"""Translate this soil analysis to Hindi:

{analysis}

Return the translated JSON with same structure."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.translator.ainvoke(messages)
            
            # Parse response - try to extract JSON
            import json
            import re
            
            content = response.content.strip()
            # Remove markdown code blocks
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            
            # Find JSON object
            obj_match = re.search(r'\{.*\}', content, re.DOTALL)
            if obj_match:
                content = obj_match.group(0)
            
            translated = json.loads(content)
            logger.info("✓ Translated soil analysis to Hindi")
            return translated
            
        except Exception as e:
            logger.error(f"Translation error (soil analysis): {e}")
            logger.error(f"Response content: {response.content if 'response' in locals() else 'No response'}")
            # Return original if translation fails
            return analysis
    
    async def translate_crop_recommendations(self, crops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Translate crop recommendations to Hindi"""
        
        system_prompt = """You are a professional translator specializing in agricultural content.
Translate the following crop recommendations from English to Hindi.

IMPORTANT:
- Maintain the exact JSON array structure
- Translate crop names, reasons, and seasons to Hindi
- Use common Hindi names for crops (e.g., Rice → धान, Wheat → गेहूं)
- Keep seasons in Hindi format (e.g., Kharif → खरीफ, Rabi → रबी)
- Return ONLY the translated JSON array, no markdown or explanations"""

        user_prompt = f"""Translate these crop recommendations to Hindi:

{crops}

Return the translated JSON array with same structure."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.translator.ainvoke(messages)
            
            import json
            import re
            
            content = response.content.strip()
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            
            # Find JSON array
            arr_match = re.search(r'\[.*\]', content, re.DOTALL)
            if arr_match:
                content = arr_match.group(0)
            
            translated = json.loads(content)
            logger.info(f"✓ Translated {len(translated)} crop recommendations to Hindi")
            return translated
            
        except Exception as e:
            logger.error(f"Translation error (crops): {e}")
            return crops
    
    async def translate_fertilizer_recommendations(self, fertilizers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Translate fertilizer recommendations to Hindi"""
        
        system_prompt = """You are a professional translator specializing in agricultural content.
Translate the following fertilizer recommendations from English to Hindi.

IMPORTANT:
- Maintain the exact JSON array structure
- Translate fertilizer names, applications, timing, and purpose to Hindi
- Use common Hindi terms (e.g., Compost → कंपोस्ट, FYM → गोबर की खाद)
- Keep units clear (e.g., kg/acre → किग्रा/एकड़, tons/acre → टन/एकड़)
- Return ONLY the translated JSON array, no markdown or explanations"""

        user_prompt = f"""Translate these fertilizer recommendations to Hindi:

{fertilizers}

Return the translated JSON array with same structure."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.translator.ainvoke(messages)
            
            import json
            import re
            
            content = response.content.strip()
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            
            # Find JSON array
            arr_match = re.search(r'\[.*\]', content, re.DOTALL)
            if arr_match:
                content = arr_match.group(0)
            
            translated = json.loads(content)
            logger.info(f"✓ Translated {len(translated)} fertilizer recommendations to Hindi")
            return translated
            
        except Exception as e:
            logger.error(f"Translation error (fertilizers): {e}")
            return fertilizers
    
    async def translate_complete_report(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Translate entire report to Hindi"""
        
        logger.info("🌐 Translating report to Hindi...")
        
        try:
            import asyncio
            
            # Translate all sections in parallel
            soil_task = self.translate_soil_analysis(report.get('soilAnalysis', {}))
            crop_task = self.translate_crop_recommendations(report.get('cropRecommendations', []))
            fert_task = self.translate_fertilizer_recommendations(report.get('fertilizerRecommendations', []))
            
            soil_hi, crops_hi, fert_hi = await asyncio.gather(
                soil_task,
                crop_task,
                fert_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(soil_hi, Exception):
                logger.error(f"Soil translation failed: {soil_hi}")
                soil_hi = report.get('soilAnalysis', {})
            if isinstance(crops_hi, Exception):
                logger.error(f"Crop translation failed: {crops_hi}")
                crops_hi = report.get('cropRecommendations', [])
            if isinstance(fert_hi, Exception):
                logger.error(f"Fertilizer translation failed: {fert_hi}")
                fert_hi = report.get('fertilizerRecommendations', [])
            
            translated_report = {
                "soilAnalysis": soil_hi,
                "cropRecommendations": crops_hi,
                "fertilizerRecommendations": fert_hi
            }
            
            logger.info("✅ Report translated to Hindi successfully")
            return translated_report
            
        except Exception as e:
            logger.error(f"❌ Error translating report: {e}")
            # Return original report if translation fails
            return report


# Singleton instance
report_translator = ReportTranslator()
