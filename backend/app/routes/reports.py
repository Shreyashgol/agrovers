"""
Report Generation Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
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
    """Background task for report generation using AI agents"""
    try:
        from ..services.report_orchestrator import report_orchestrator
        from ..services.report_translator import report_translator
        
        # Update progress
        report_status_store[session_id] = {
            "status": "processing",
            "progress": 20,
            "message": "Analyzing soil parameters..."
        }
        
        # Prepare soil data (always in English for LLM)
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
        }
        
        # Update progress
        report_status_store[session_id]["progress"] = 40
        report_status_store[session_id]["message"] = "Generating crop recommendations..."
        
        # Generate report in English using LangChain orchestrator
        report_english = await report_orchestrator.generate_complete_report(soil_data)
        
        # Update progress
        report_status_store[session_id]["progress"] = 70
        report_status_store[session_id]["message"] = "Translating to Hindi..."
        
        # Translate to Hindi (with fallback to English if translation fails)
        try:
            report_hindi = await report_translator.translate_complete_report(report_english)
        except Exception as e:
            logger.error(f"Translation failed, using English as fallback: {e}")
            report_hindi = report_english  # Fallback to English
        
        # Update progress
        report_status_store[session_id]["progress"] = 90
        report_status_store[session_id]["message"] = "Finalizing report..."
        
        # Store completed report with both languages
        report_status_store[session_id] = {
            "status": "completed",
            "progress": 100,
            "message": "Report generated successfully!",
            "report": {
                "english": report_english,
                "hindi": report_hindi,
                "metadata": {
                    "sessionId": session_id,
                    "generatedAt": str(__import__('datetime').datetime.now()),
                    "location": soil_data.get("location", ""),
                    "soilType": soil_data.get("soilType", "")
                }
            }
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
    Download the generated report as JSON
    """
    status_data = report_status_store.get(session_id)
    
    if not status_data or status_data["status"] != "completed":
        raise HTTPException(status_code=404, detail="Report not ready")
    
    return {
        "success": True,
        "report": status_data["report"]
    }


@router.get("/download/{session_id}/pdf")
async def download_report_pdf(session_id: str, language: str = "english"):
    """
    Download the generated report as PDF
    
    Args:
        session_id: Session ID
        language: "english" or "hindi"
    """
    from fastapi.responses import StreamingResponse
    from ..services.pdf_generator import pdf_generator
    
    status_data = report_status_store.get(session_id)
    
    if not status_data or status_data["status"] != "completed":
        raise HTTPException(status_code=404, detail="Report not ready")
    
    try:
        # Generate PDF
        pdf_buffer = pdf_generator.generate_pdf(status_data["report"], language)
        
        # Return as downloadable file
        filename = f"soil_report_{session_id}_{language}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
