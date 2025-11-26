"""
Report Generation Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from ..services.n8n_service import n8n_service
from ..services.session_manager import session_manager

logger = logging.getLogger(__name__)
router = APIRouter()

class ReportRequest(BaseModel):
    session_id: str

class ReportStatusResponse(BaseModel):
    status: str  # "pending", "processing", "completed", "failed"
    progress: int  # 0-100
    message: str
    report: Optional[Dict[str, Any]] = None

# In-memory storage for report status (use Redis in production)
report_status_store: Dict[str, Dict[str, Any]] = {}

@router.post("/generate")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """
    Trigger report generation for a completed session
    """
    try:
        session_id = request.session_id
        
        # Get session data
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if all questions are answered
        if not session.is_complete():
            raise HTTPException(
                status_code=400, 
                detail="Cannot generate report. Please answer all questions first."
            )
        
        # Initialize report status
        report_status_store[session_id] = {
            "status": "processing",
            "progress": 10,
            "message": "Preparing soil data..."
        }
        
        # Trigger background report generation
        background_tasks.add_task(generate_report_background, session_id, session)
        
        return {
            "success": True,
            "message": "Report generation started",
            "session_id": session_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting report generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def generate_report_background(session_id: str, session):
    """Background task for report generation"""
    try:
        # Update progress
        report_status_store[session_id] = {
            "status": "processing",
            "progress": 30,
            "message": "Analyzing soil parameters..."
        }
        
        # Prepare soil data - map from session.answers to n8n format
        # session.answers has: name, color, moisture, smell, ph_category, ph_value, soil_type, earthworms, location, fertilizer_used
        soil_data = {
            "id": session_id,
            "name": session.answers.name or "",
            "soilColor": session.answers.color or "",
            "moistureLevel": session.answers.moisture or "",
            "soilSmell": session.answers.smell or "",
            "phLevel": str(session.answers.ph_value) if session.answers.ph_value else (session.answers.ph_category or ""),
            "soilType": session.answers.soil_type or "",
            "earthworms": session.answers.earthworms or "",
            "location": session.answers.location or "",
            "previousFertilizers": session.answers.fertilizer_used or "",
            "preferredLanguage": session.language
        }
        
        # Update progress
        report_status_store[session_id]["progress"] = 50
        report_status_store[session_id]["message"] = "Generating personalized recommendations..."
        
        # Call n8n service
        result = await n8n_service.generate_soil_report(soil_data)
        
        if result["success"]:
            # Parse report if needed
            report_data = result["report"]
            if isinstance(report_data, str):
                report_data = n8n_service.parse_report_text(report_data)
            
            report_status_store[session_id] = {
                "status": "completed",
                "progress": 100,
                "message": "Report generated successfully!",
                "report": report_data
            }
        else:
            report_status_store[session_id] = {
                "status": "failed",
                "progress": 0,
                "message": result.get("error", "Failed to generate report")
            }
            
    except Exception as e:
        logger.error(f"Error in background report generation: {str(e)}")
        report_status_store[session_id] = {
            "status": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}"
        }

@router.get("/status/{session_id}")
async def get_report_status(session_id: str) -> ReportStatusResponse:
    """
    Get the current status of report generation
    """
    status_data = report_status_store.get(session_id)
    
    if not status_data:
        return ReportStatusResponse(
            status="pending",
            progress=0,
            message="Report generation not started"
        )
    
    return ReportStatusResponse(**status_data)

@router.get("/download/{session_id}")
async def download_report(session_id: str):
    """
    Download the generated report
    """
    status_data = report_status_store.get(session_id)
    
    if not status_data or status_data["status"] != "completed":
        raise HTTPException(status_code=404, detail="Report not ready")
    
    return {
        "success": True,
        "report": status_data["report"]
    }
