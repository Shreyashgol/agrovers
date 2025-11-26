"""
Mock n8n Server for Testing
Simulates n8n webhook responses
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

app = FastAPI(title="Mock n8n Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/webhook/soil-report")
async def soil_report_webhook(request: Request):
    """Mock n8n webhook that generates a sample soil report"""
    
    data = await request.json()
    print("\n" + "="*60)
    print("📥 Received soil data from Agrovers:")
    print(json.dumps(data, indent=2))
    print("="*60 + "\n")
    
    # Extract data
    name = data.get("name", "Farmer")
    soil_color = data.get("soilColor", "unknown")
    moisture = data.get("moistureLevel", "unknown")
    ph = data.get("phLevel", "unknown")
    soil_type = data.get("soilType", "unknown")
    earthworms = data.get("earthworms", "unknown")
    location = data.get("location", "unknown")
    
    # Calculate soil health score (simple logic)
    score = 70
    if soil_color.lower() in ["dark brown", "black"]:
        score += 10
    if moisture.lower() in ["moist", "slightly moist"]:
        score += 5
    if earthworms.lower() == "yes":
        score += 10
    if soil_type.lower() == "loamy":
        score += 5
    
    # Generate structured report matching your n8n format
    report = {
        "soilAnalysis": {
            "assessment": f"The soil sample '{data.get('id', 'unknown')}' from {location} demonstrates excellent health characteristics, indicative of highly fertile and productive agricultural land. The {soil_color} color, earthy smell, and {moisture} condition strongly suggest high organic matter content and robust microbial activity. The {soil_type} soil type provides an ideal balance of aeration, water retention, and drainage, crucial for robust root development. The pH of {ph} is nearly perfect for a wide range of crops, ensuring optimal nutrient availability. Furthermore, the presence of earthworms is a strong biological indicator of a thriving soil ecosystem, promoting soil structure and nutrient cycling.",
            "pros": [
                f"Optimal pH ({ph}) ensures high nutrient availability for most crops.",
                f"{soil_type.title()} soil type offers excellent water retention, drainage, and aeration.",
                f"{soil_color.title()} color and earthy smell signify rich organic matter and active microbial life.",
                "Presence of earthworms indicates healthy biological activity, improving soil structure and nutrient cycling." if earthworms.lower() == "yes" else "Good soil structure supports healthy root development.",
                f"{moisture.title()} condition suggests good water-holding capacity, reducing frequent irrigation needs."
            ],
            "cons": [
                "Potential for specific micronutrient deficiencies or imbalances if relying solely on generic fertilizers without targeted soil testing.",
                "While balanced fertilizers are good, they might not fully meet the specific high demands of certain crops for primary or secondary nutrients.",
                "Continuous application of the same fertilizer ratio could, over time, lead to an accumulation of certain nutrients while depleting others."
            ],
            "rating": "Excellent" if score >= 90 else "Good" if score >= 70 else "Fair"
        },
        "cropRecommendations": [
            {
                "crop": "Sugarcane",
                "reason": "Thrives in fertile, well-drained loamy soils with consistent moisture and pH 6.0-7.0. Maharashtra is a major sugarcane producer, and this soil is ideal for high yields.",
                "season": "Adsali (Jan-Feb) or Pre-seasonal (Oct-Nov) for 12-18 months cycle."
            },
            {
                "crop": "Soybean",
                "reason": "Well-suited to well-drained loamy soils with pH 6.0-7.0. It's a key pulse crop in Maharashtra, enriching the soil with nitrogen through symbiosis.",
                "season": "Kharif (Monsoon): Sown June-July, harvested Oct-Nov."
            },
            {
                "crop": "Cotton",
                "reason": "Prefers deep, well-drained loamy soils with a pH of 6.0-7.5. Maharashtra is a significant cotton-growing state, benefiting from good soil structure and moisture.",
                "season": "Kharif (Monsoon): Sown June-July, harvested Nov-Jan."
            },
            {
                "crop": "Wheat",
                "reason": "Grows best in fertile, well-drained loamy soils with pH 6.0-7.0. It is a staple Rabi crop, well-adapted to the region's winter conditions.",
                "season": "Rabi (Winter): Sown Oct-Nov, harvested Feb-Mar."
            },
            {
                "crop": "Onion",
                "reason": "Thrives in well-drained loamy soils with good organic matter and pH 6.0-7.5. Maharashtra is a top onion producer, and good moisture management in loamy soil is beneficial.",
                "season": "Kharif (June-July), Late Kharif (Aug-Sept), Rabi (Oct-Nov)."
            },
            {
                "crop": "Chickpea (Chana)",
                "reason": "Ideally suited for loamy soils with good drainage and pH 6.0-7.0. As a legume, it contributes to soil fertility and is a reliable Rabi crop in the region.",
                "season": "Rabi (Winter): Sown Oct-Nov, harvested Feb-Mar."
            }
        ],
        "fertilizerRecommendations": [
            {
                "fertilizer": "Farmyard Manure (FYM) / Quality Compost",
                "type": "Organic",
                "application": "5-10 tonnes per acre (adjust based on compost quality and soil tests).",
                "timing": "Incorporate thoroughly into the soil 2-3 weeks before sowing/planting.",
                "purpose": "Enhances soil organic matter, improves soil structure, water retention, and provides a slow release of macro and micronutrients, supporting overall soil health and microbial activity."
            },
            {
                "fertilizer": "Urea (46-0-0)",
                "type": "Chemical",
                "application": "Varies by crop: e.g., Sugarcane (80-120 kg/acre), Wheat (60-80 kg/acre), Cotton (50-70 kg/acre). Always split into 2-3 doses.",
                "timing": "First dose as top dressing 20-30 days after sowing/planting, subsequent doses during peak vegetative growth periods.",
                "purpose": "Provides readily available nitrogen crucial for robust vegetative growth, leaf development, and overall plant vigor, tailored to specific crop needs."
            },
            {
                "fertilizer": "DAP (Di-ammonium Phosphate 18-46-0) + MOP (Muriate of Potash 0-0-60)",
                "type": "Chemical",
                "application": "Varies by crop: e.g., Wheat/Cotton (100-120 kg DAP + 60-80 kg MOP/acre), Soybean (60-80 kg DAP + 40-50 kg MOP/acre).",
                "timing": "Basal application, incorporated into the soil at the time of sowing/planting.",
                "purpose": "Supplies concentrated phosphorus for strong root development and energy transfer, and potassium for flowering, fruiting, disease resistance, and water regulation."
            },
            {
                "fertilizer": "Sulphur Bentonite (90% S)",
                "type": "Chemical",
                "application": "10-20 kg per acre.",
                "timing": "Basal application, incorporated at sowing.",
                "purpose": "Provides essential sulfur, crucial for protein synthesis, oil content (especially for soybean), and enhances nutrient use efficiency."
            },
            {
                "fertilizer": "Chelated Multi-Micronutrient Mix (e.g., Zn, B, Fe, Mn)",
                "type": "Chemical",
                "application": "Foliar spray: 500g - 1 kg per acre mixed in 200 liters of water. Or soil application: 5-10 kg per acre.",
                "timing": "During critical growth stages (e.g., flowering, fruit set) or if specific deficiency symptoms are observed.",
                "purpose": "Corrects potential hidden deficiencies of essential trace elements vital for various metabolic functions, yield quality, and quantity."
            },
            {
                "fertilizer": "Bio-fertilizers (e.g., Rhizobium for legumes, PSB, KMB)",
                "type": "Organic",
                "application": "Seed treatment (200g/10-15 kg seed), soil application (2-4 kg/acre mixed with FYM/compost), or seedling dip.",
                "timing": "At sowing/planting.",
                "purpose": "Enhances nutrient availability by promoting natural processes like nitrogen fixation, phosphorus solubilization, and potassium mobilization, reducing reliance on chemical fertilizers."
            }
        ]
    }
    
    print("📤 Sending report back to Agrovers:")
    print(json.dumps(report, indent=2))
    print("\n" + "="*60 + "\n")
    
    return report

@app.get("/")
async def root():
    return {
        "message": "Mock n8n Server Running",
        "endpoints": {
            "soil_report": "POST /webhook/soil-report"
        }
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Mock n8n Server")
    print("="*60)
    print("📍 Webhook URL: http://localhost:5678/webhook/soil-report")
    print("💡 This simulates your n8n workflow for testing")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=5678, log_level="info")
