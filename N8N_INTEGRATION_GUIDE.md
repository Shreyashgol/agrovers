# n8n Integration Guide

## Overview
The Agrovers Soil Assistant now integrates with n8n to generate comprehensive soil health reports after all 9 questions are answered.

## Architecture

### Flow
1. User completes all 9 soil test questions
2. Frontend triggers report generation via `/api/reports/generate`
3. Backend sends soil data to n8n webhook
4. n8n processes data and generates detailed report
5. Frontend polls `/api/reports/status/{session_id}` for progress
6. When complete, beautiful report is displayed with animations

### Components Created

#### Backend
- **`backend/app/services/n8n_service.py`** - n8n webhook client
  - Sends POST request with soil data
  - Handles response parsing (JSON or text)
  - Extracts sections from text reports
  
- **`backend/app/routes/reports.py`** - Report API endpoints
  - `POST /api/reports/generate` - Trigger report generation
  - `GET /api/reports/status/{session_id}` - Poll report status
  - `GET /api/reports/download/{session_id}` - Download completed report
  - Background task for async report generation

#### Frontend
- **`frontend/src/api/reports.ts`** - Report API client
  - `generateReport()` - Start report generation
  - `getReportStatus()` - Poll for status updates
  - `downloadReport()` - Get completed report

- **`frontend/src/components/ui/ReportLoadingScreen.tsx`** - Loading UI
  - Animated progress bar (0-100%)
  - Step-by-step progress indicators
  - Beautiful dark-themed loading screen
  - Shows current processing stage

- **`frontend/src/components/ui/SoilReportDisplay.tsx`** - Report Display
  - Structured report with sections
  - Soil health score with animated progress bar
  - Analysis cards (color, moisture, pH, type)
  - Recommendations (fertilizers, practices, warnings)
  - Next steps checklist
  - Download and share buttons
  - Smooth fade-in animations

## Configuration

### Backend (.env)
```bash
N8N_WEBHOOK_URL=https://algoshera.app.n8n.cloud/webhook-test/soil-analysis-v5
```

### n8n Webhook Setup

#### Expected Input (POST request)
```json
{
  "id": "session-id",
  "name": "Farmer Name",
  "soilColor": "dark brown",
  "moistureLevel": "moist",
  "soilSmell": "earthy",
  "phLevel": "6.5",
  "soilType": "loamy",
  "earthworms": "yes",
  "location": "Maharashtra, India",
  "previousFertilizers": "NPK 10-10-10",
  "preferredLanguage": "English"
}
```

#### Expected Output (JSON)

**Option 1: Structured Report**
```json
{
  "soilHealth": {
    "score": 85,
    "status": "Good",
    "description": "Your soil is in good health with balanced nutrients."
  },
  "analysis": {
    "soilColor": "Dark Brown - Rich in organic matter",
    "moistureLevel": "Moist - Optimal for most crops",
    "phLevel": "6.5 - Slightly acidic, ideal for vegetables",
    "soilType": "Loamy - Best soil type for agriculture"
  },
  "recommendations": {
    "fertilizers": [
      "NPK 10-10-10 for balanced nutrition",
      "Organic compost to maintain soil health",
      "Vermicompost for earthworm activity"
    ],
    "practices": [
      "Maintain current moisture levels",
      "Add organic matter regularly",
      "Practice crop rotation"
    ],
    "warnings": [
      "Monitor pH levels monthly",
      "Avoid over-watering"
    ]
  },
  "nextSteps": [
    "Apply recommended fertilizers",
    "Test soil again in 3 months",
    "Consult local agricultural expert"
  ]
}
```

**Option 2: Text Report**
```json
{
  "type": "text_report",
  "content": "Full text report here...",
  "sections": [
    {
      "title": "Soil Analysis",
      "content": ["Line 1", "Line 2", "Line 3"]
    },
    {
      "title": "Recommendations",
      "content": ["Recommendation 1", "Recommendation 2"]
    }
  ]
}
```

## Testing

### 1. Test n8n Integration
```bash
cd backend
source .venv/bin/activate
python test_n8n_integration.py
```

**Note:** You must click "Execute workflow" in n8n before running the test in test mode.

### 2. Test Full Flow
1. Start backend: `bash start_backend.sh`
2. Start frontend: `bash start_frontend.sh`
3. Complete all 9 questions
4. Watch the loading screen with progress
5. View the beautiful report display

## Progress Stages

The loading screen shows these stages:
1. **10%** - Preparing soil data
2. **30%** - Analyzing parameters
3. **50%** - Generating recommendations
4. **100%** - Report ready

## Report Display Features

### Visual Elements
- ✅ Gradient header with download/share buttons
- ✅ Animated soil health score (0-100)
- ✅ Analysis cards with icons
- ✅ Color-coded recommendation sections
- ✅ Numbered next steps checklist
- ✅ Smooth fade-in animations
- ✅ Dark theme with green accents

### Interactions
- Download report (TODO: PDF generation)
- Share report (TODO: Share functionality)
- Start new test button

## API Endpoints

### Generate Report
```http
POST /api/reports/generate
Content-Type: application/json

{
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Report generation started",
  "session_id": "abc123"
}
```

### Get Report Status
```http
GET /api/reports/status/{session_id}
```

**Response:**
```json
{
  "status": "processing",
  "progress": 50,
  "message": "Generating recommendations...",
  "report": null
}
```

**Status values:** `pending`, `processing`, `completed`, `failed`

### Download Report
```http
GET /api/reports/download/{session_id}
```

**Response:**
```json
{
  "success": true,
  "report": { /* report data */ }
}
```

## Error Handling

### Backend
- Timeout after 2 minutes
- HTTP error handling
- JSON parsing fallback to text
- Comprehensive logging

### Frontend
- Loading state management
- Error display with retry option
- Fallback to summary page if report fails
- Progress polling with cleanup

## Future Enhancements

1. **PDF Generation** - Export report as PDF
2. **Email Delivery** - Send report to farmer's email
3. **SMS Notifications** - Alert when report is ready
4. **Multi-language Reports** - Generate reports in Hindi
5. **Historical Reports** - View past reports
6. **Report Comparison** - Compare multiple test results
7. **Offline Support** - Cache reports for offline viewing
8. **Print Optimization** - Print-friendly report layout

## Troubleshooting

### n8n webhook returns 404
- Click "Execute workflow" in n8n (test mode)
- Or activate the workflow (production mode)
- Verify webhook URL in `.env`

### Report generation times out
- Check n8n workflow is running
- Increase timeout in `n8n_service.py`
- Check n8n logs for errors

### Report not displaying
- Check browser console for errors
- Verify report data structure matches expected format
- Check network tab for API responses

## Dependencies

### Backend
- `httpx==0.25.2` - HTTP client for n8n
- `fastapi` - API framework
- `pydantic` - Data validation

### Frontend
- `lucide-react` - Icons
- `tailwindcss` - Styling
- React hooks for state management

## File Structure

```
backend/
├── app/
│   ├── routes/
│   │   └── reports.py          # Report API endpoints
│   └── services/
│       └── n8n_service.py      # n8n integration
└── test_n8n_integration.py     # Test script

frontend/
├── src/
│   ├── api/
│   │   └── reports.ts          # Report API client
│   ├── components/
│   │   └── ui/
│   │       ├── ReportLoadingScreen.tsx
│   │       └── SoilReportDisplay.tsx
│   └── pages/
│       └── NewSoilWizard.tsx   # Updated with report flow
└── src/index.css               # Report animations
```

## Summary

The n8n integration is complete and ready for testing. Once you activate your n8n workflow, the system will:

1. ✅ Automatically trigger report generation after question 9
2. ✅ Show beautiful loading screen with progress
3. ✅ Poll for status every 2 seconds
4. ✅ Display stunning report with animations
5. ✅ Handle errors gracefully
6. ✅ Support both structured and text reports

**Next Steps:**
1. Activate your n8n workflow
2. Test the complete flow
3. Customize report format in n8n
4. Add PDF export functionality
5. Deploy to production
