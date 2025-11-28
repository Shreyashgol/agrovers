"""
LangChain-based Report Orchestrator
Uses 3 specialized LLM agents to generate comprehensive soil reports
"""
import asyncio
import json
import logging
import re
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from ..config import settings

logger = logging.getLogger(__name__)


class ReportOrchestrator:
    """
    Orchestrates 3 specialized agents to generate soil reports:
    1. Soil Analysis Agent (Gemini Flash)
    2. Crop Recommendation Agent (Gemini Flash)  
    3. Fertilizer Recommendation Agent (Groq)
    """
    
    def __init__(self):
        """Initialize the three specialized agents - all using Groq for speed and reliability"""
        
        # All agents use Groq for fast, reliable generation
        # Agent 1: Soil Analysis
        self.soil_analysis_agent = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.groq_llm_api_key,  # Use existing Groq key
            temperature=0.3,
            max_tokens=2000
        )
        
        # Agent 2: Crop Recommendations
        self.crop_agent = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.groq_llm_api_key,
            temperature=0.4,
            max_tokens=2000
        )
        
        # Agent 3: Fertilizer Recommendations
        self.fertilizer_agent = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=settings.groq_report_api_key if settings.groq_report_api_key else settings.groq_llm_api_key,
            temperature=0.4,
            max_tokens=2000
        )
        
        logger.info("✓ Initialized Report Orchestrator with 3 Groq agents (fast & reliable)")
    
    def _clean_json_response(self, text: str) -> str:
        """Clean LLM response to extract valid JSON"""
        text = text.strip()
        
        # Remove markdown code blocks
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        
        # Remove common prefixes
        for prefix in ['Output:', 'Answer:', 'Result:', 'JSON:', 'Here is', 'Here\'s']:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
        
        # Find JSON object or array
        obj_match = re.search(r'\{.*\}', text, re.DOTALL)
        arr_match = re.search(r'\[.*\]', text, re.DOTALL)
        
        if obj_match and (not arr_match or obj_match.start() < arr_match.start()):
            return obj_match.group(0)
        elif arr_match:
            return arr_match.group(0)
        
        return text.strip()
    
    async def generate_soil_analysis(self, soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent 1: Soil Science Expert
        Generates in the specified language (Hindi or English)
        """
        language = soil_data.get('language', 'en')
        is_hindi = language == 'hi'
        
        if is_hindi:
            system_prompt = """आप एक मिट्टी विज्ञान विशेषज्ञ हैं जो भारतीय कृषि में विशेषज्ञता रखते हैं।

कार्य: मिट्टी के डेटा का विश्लेषण करें और प्रदान करें:
1) assessment: मिट्टी के स्वास्थ्य का विस्तृत विश्लेषण (3-4 वाक्य) जिसमें रंग, नमी, गंध, pH, मिट्टी का प्रकार, जैविक गतिविधि और स्थान का उल्लेख हो
2) pros: 4-5 सकारात्मक विशेषताएं (छोटे, किसान-अनुकूल बिंदु)
3) cons: 3-4 सीमाएं या चिंताएं
4) rating: इनमें से एक [Excellent, Good, Fair, Poor]

JSON format में return करें:
{"assessment":"...","pros":["..."],"cons":["..."],"rating":"..."}

कोई markdown नहीं, कोई अतिरिक्त keys नहीं। किसानों के लिए सरल भाषा का उपयोग करें।"""

            user_prompt = f"""इस मिट्टी के डेटा का विश्लेषण करें:

मिट्टी का रंग: {soil_data.get('soilColor', 'अज्ञात')}
नमी का स्तर: {soil_data.get('moistureLevel', 'अज्ञात')}
मिट्टी की गंध: {soil_data.get('soilSmell', 'अज्ञात')}
pH स्तर: {soil_data.get('phLevel', 'अज्ञात')}
मिट्टी का प्रकार: {soil_data.get('soilType', 'अज्ञात')}
केंचुए/जैविक गतिविधि: {soil_data.get('earthworms', 'अज्ञात')}
स्थान: {soil_data.get('location', 'अज्ञात')}
पिछली खाद: {soil_data.get('previousFertilizers', 'कोई नहीं')}

JSON format में व्यापक मिट्टी विश्लेषण प्रदान करें।"""
        else:
            system_prompt = """You are a soil science expert specializing in Indian agriculture.

Task: Analyze the soil data and provide:
1) assessment: detailed soil-health analysis (3-4 sentences) referencing color, moisture, smell, pH, soil_type, biological_activity, and location
2) pros: list 4-5 positive characteristics (short, farmer-friendly bullets)
3) cons: list 3-4 limitations or concerns
4) rating: one of [Excellent, Good, Fair, Poor]

Return as JSON object exactly:
{"assessment":"...","pros":["..."],"cons":["..."],"rating":"..."}

No markdown, no additional keys. Use simple language for farmers."""

            user_prompt = f"""Analyze this soil data:

Soil Color: {soil_data.get('soilColor', 'unknown')}
Moisture Level: {soil_data.get('moistureLevel', 'unknown')}
Soil Smell: {soil_data.get('soilSmell', 'unknown')}
pH Level: {soil_data.get('phLevel', 'unknown')}
Soil Type: {soil_data.get('soilType', 'unknown')}
Earthworms/Biological Activity: {soil_data.get('earthworms', 'unknown')}
Location: {soil_data.get('location', 'unknown')}
Previous Fertilizers: {soil_data.get('previousFertilizers', 'none')}

Provide comprehensive soil analysis in JSON format."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.soil_analysis_agent.ainvoke(messages)
            cleaned = self._clean_json_response(response.content)
            result = json.loads(cleaned)
            
            # Validate required fields
            required = ['assessment', 'pros', 'cons', 'rating']
            if not all(k in result for k in required):
                raise ValueError(f"Missing required fields. Got: {result.keys()}")
            
            # Validate rating
            if result['rating'] not in ['Excellent', 'Good', 'Fair', 'Poor']:
                result['rating'] = 'Good'  # Default
            
            logger.info(f"✓ Soil analysis generated: {result['rating']}")
            return result
            
        except Exception as e:
            logger.error(f"Soil analysis error: {e}")
            # Return error - no fallback
            raise Exception(f"Failed to generate soil analysis: {str(e)}")
    
    async def generate_crop_recommendations(self, soil_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Agent 2: Crop Specialist
        Generates in the specified language (Hindi or English)
        """
        language = soil_data.get('language', 'en')
        is_hindi = language == 'hi'
        location = soil_data.get('location', 'India')
        soil_type = soil_data.get('soilType', 'unknown')
        ph = soil_data.get('phLevel', 'unknown')
        moisture = soil_data.get('moistureLevel', 'unknown')
        
        if is_hindi:
            system_prompt = """आप एक कृषि फसल विशेषज्ञ हैं जो भारतीय खेती में विशेषज्ञता रखते हैं।

कार्य: मिट्टी और स्थान के आधार पर 6 फसलों की सिफारिश करें। प्रत्येक फसल के लिए शामिल करें:
- crop: फसल का नाम (हिंदी में)
- reason: एक वाक्य में कारण (मिट्टी के मापदंडों से जुड़ा)
- season: स्थानीय बुवाई का मौसम

JSON array में return करें:
[{"crop":"धान","reason":"...","season":"खरीफ (जून-जुलाई)"}]

कोई markdown नहीं। किसानों के लिए सरल भाषा का उपयोग करें।"""

            user_prompt = f"""इन परिस्थितियों के लिए 6 उपयुक्त फसलों की सिफारिश करें:

मिट्टी का प्रकार: {soil_type}
pH स्तर: {ph}
नमी: {moisture}
स्थान: {location}
केंचुए: {soil_data.get('earthworms', 'अज्ञात')}

आवश्यकताएं:
- मिट्टी के प्रकार और pH के लिए उपयुक्त
- स्थान/जलवायु के लिए उपयुक्त
- भारत में आमतौर पर उगाई जाने वाली
- अनाज, दालें, सब्जियां, नकदी फसलों का मिश्रण

6 फसल सिफारिशों के साथ JSON array return करें।"""
        else:
            system_prompt = """You are an agricultural crop specialist with expertise in Indian farming.

Task: Based on soil and location, recommend 6 crops. For each crop include:
- crop: string (crop name in English)
- reason: single-sentence justification tied to soil parameters
- season: local growing season or seeding months

Return as JSON array of objects:
[{"crop":"Rice","reason":"tolerates waterlogged conditions","season":"Kharif (Jun-Jul)"}]

No markdown, no explanations. Use simple language for farmers."""

            user_prompt = f"""Recommend 6 suitable crops for:

Soil Type: {soil_type}
pH Level: {ph}
Moisture: {moisture}
Location: {location}
Earthworms: {soil_data.get('earthworms', 'unknown')}

Requirements:
- Suitable for the soil type and pH
- Appropriate for location/climate
- Commonly grown in India
- Mix of cereals, pulses, vegetables, cash crops

Return JSON array with 6 crop recommendations."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.crop_agent.ainvoke(messages)
            cleaned = self._clean_json_response(response.content)
            result = json.loads(cleaned)
            
            # Validate
            if not isinstance(result, list):
                raise ValueError("Expected array of crops")
            
            # Ensure each crop has required fields
            validated = []
            for crop in result[:6]:
                if isinstance(crop, dict) and 'crop' in crop:
                    validated.append({
                        'crop': crop.get('crop', 'Unknown'),
                        'reason': crop.get('reason', 'Suitable for local conditions'),
                        'season': crop.get('season', 'Season varies by region')
                    })
            
            if len(validated) < 3:
                raise ValueError("Too few valid crops")
            
            logger.info(f"✓ Generated {len(validated)} crop recommendations")
            return validated
            
        except Exception as e:
            logger.error(f"Crop recommendation error: {e}")
            # Return error - no fallback
            raise Exception(f"Failed to generate crop recommendations: {str(e)}")
    
    async def generate_fertilizer_recommendations(
        self,
        soil_data: Dict[str, Any],
        crops: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Agent 3: Fertilizer Expert
        Generates in the specified language (Hindi or English)
        """
        language = soil_data.get('language', 'en')
        is_hindi = language == 'hi'
        crop_names = ", ".join([c['crop'] for c in crops[:3]])
        
        if is_hindi:
            system_prompt = """आप एक उर्वरक और मिट्टी पोषण विशेषज्ञ हैं।

कार्य: 6 उर्वरक सिफारिशें प्रदान करें। प्रत्येक के लिए:
- fertilizer: नाम (जैविक या रासायनिक)
- type: "Organic" या "Chemical"
- application: मात्रा इकाइयों के साथ (जैसे "50 किग्रा/एकड़" या "5 टन/एकड़")
- timing: कब लगाएं (जैसे "बुवाई से पहले", "फूल आने पर")
- purpose: यह उर्वरक क्यों सिफारिश किया गया है

JSON array में return करें:
[{"fertilizer":"गोबर की खाद","type":"Organic","application":"5 टन/एकड़","timing":"बुवाई से पहले","purpose":"..."}]

कोई markdown नहीं। किसानों के लिए सरल भाषा का उपयोग करें।"""

            user_prompt = f"""इन परिस्थितियों के लिए 6 उर्वरकों की सिफारिश करें:

मिट्टी का प्रकार: {soil_data.get('soilType', 'अज्ञात')}
pH स्तर: {soil_data.get('phLevel', 'अज्ञात')}
पिछली खाद: {soil_data.get('previousFertilizers', 'कोई नहीं')}
केंचुए: {soil_data.get('earthworms', 'अज्ञात')}
सिफारिश की गई फसलें: {crop_names}

शामिल करें:
- 2-3 जैविक विकल्प (गोबर की खाद, कंपोस्ट, जैव-उर्वरक)
- 3-4 रासायनिक विकल्प (NPK, यूरिया, DAP, सूक्ष्म पोषक तत्व)
- विशिष्ट मात्रा
- स्पष्ट समय

6 उर्वरक सिफारिशों के साथ JSON array return करें।"""
        else:
            system_prompt = """You are a fertilizer and soil nutrition expert.

Task: Provide 6 fertilizer recommendations. For each:
- fertilizer: name (organic or chemical)
- type: "Organic" or "Chemical"
- application: rate with units (e.g., "50 kg/acre" or "5 tons/acre")
- timing: when to apply (e.g., "pre-planting", "at flowering")
- purpose: why this fertilizer is recommended

Return as JSON array:
[{"fertilizer":"Compost","type":"Organic","application":"5 tons/acre","timing":"Pre-planting","purpose":"..."}]

No markdown, no explanations. Use simple language for farmers."""

            user_prompt = f"""Recommend 6 fertilizers for:

Soil Type: {soil_data.get('soilType', 'unknown')}
pH Level: {soil_data.get('phLevel', 'unknown')}
Previous Fertilizers: {soil_data.get('previousFertilizers', 'none')}
Earthworms: {soil_data.get('earthworms', 'unknown')}
Recommended Crops: {crop_names}

Include:
- 2-3 organic options (FYM, compost, bio-fertilizers)
- 3-4 chemical options (NPK, urea, DAP, micronutrients)
- Specific application rates
- Clear timing

Return JSON array with 6 fertilizer recommendations."""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = await self.fertilizer_agent.ainvoke(messages)
            cleaned = self._clean_json_response(response.content)
            result = json.loads(cleaned)
            
            # Validate
            if not isinstance(result, list):
                raise ValueError("Expected array of fertilizers")
            
            validated = []
            for fert in result[:6]:
                if isinstance(fert, dict) and 'fertilizer' in fert:
                    validated.append({
                        'fertilizer': fert.get('fertilizer', 'Unknown'),
                        'type': fert.get('type', 'Chemical'),
                        'application': fert.get('application', 'As per soil test'),
                        'timing': fert.get('timing', 'As recommended'),
                        'purpose': fert.get('purpose', 'Nutrient supplementation')
                    })
            
            if len(validated) < 3:
                raise ValueError("Too few valid fertilizers")
            
            logger.info(f"✓ Generated {len(validated)} fertilizer recommendations")
            return validated
            
        except Exception as e:
            logger.error(f"Fertilizer recommendation error: {e}")
            # Return error - no fallback
            raise Exception(f"Failed to generate fertilizer recommendations: {str(e)}")
    
    async def generate_complete_report(self, soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate all three agents in parallel to generate complete report
        """
        logger.info(f"🚀 Starting report generation for: {soil_data.get('id')}")
        
        try:
            # Run soil analysis and crop recommendations in parallel
            soil_task = self.generate_soil_analysis(soil_data)
            crop_task = self.generate_crop_recommendations(soil_data)
            
            soil_analysis, crop_recommendations = await asyncio.gather(
                soil_task,
                crop_task,
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(soil_analysis, Exception):
                logger.error(f"Soil analysis failed: {soil_analysis}")
                raise soil_analysis
            if isinstance(crop_recommendations, Exception):
                logger.error(f"Crop recommendations failed: {crop_recommendations}")
                raise crop_recommendations
            
            # Generate fertilizer recommendations based on crops
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
            
            logger.info("✅ Report generated successfully with real AI data")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            raise


# Singleton instance
report_orchestrator = ReportOrchestrator()
