# Browser Testing Guide

## Services Status
✅ Backend running on: http://localhost:8001
✅ Frontend running on: http://localhost:5174

## Testing Steps

### 1. Open the Application
Navigate to: http://localhost:5174

### 2. Start a New Session
- Click on "New Soil Analysis" or similar button
- The wizard should start

### 3. Answer Questions
Answer the questions that appear. Example answers:
- Location: "Pune, Maharashtra"
- Soil type: "Black soil"
- Crop history: "Cotton last season"
- Water availability: "Moderate"
- etc.

### 4. Complete Questions
- After answering all questions, you should see a loading screen
- The loading screen should show real-time progress:
  - "Analyzing soil data..." (33%)
  - "Generating crop recommendations..." (66%)
  - "Preparing fertilizer suggestions..." (90%)

### 5. View Report
- After loading completes, you should see the comprehensive soil report
- Report should contain:
  - Soil Analysis section
  - Crop Recommendations section
  - Fertilizer Recommendations section
- All content should be AI-generated (no mock data)

## What to Check

### ✅ Expected Behavior
- [ ] Questions load properly
- [ ] Can answer questions via text or voice
- [ ] Loading screen appears after last question
- [ ] Progress updates show real-time status
- [ ] Report generates successfully
- [ ] Report contains real AI-generated content
- [ ] No errors in browser console
- [ ] Language selection works (Hindi/English)

### ❌ Issues to Watch For
- Mock/fallback data appearing in report
- Loading stuck at certain percentage
- Errors in browser console
- API errors (check Network tab)
- Missing sections in report

## Debugging

If issues occur:

1. **Check Browser Console** (F12 → Console tab)
   - Look for JavaScript errors
   - Check for failed API calls

2. **Check Network Tab** (F12 → Network tab)
   - Look for failed requests to `/api/reports/generate`
   - Check response status codes

3. **Check Backend Logs**
   - Backend terminal should show report generation progress
   - Look for errors or exceptions

4. **Check API Keys**
   - Ensure GROQ_API_KEY is set in backend/.env
   - Verify API key has sufficient quota

## Quick API Test

You can also test the API directly:

```bash
# Test report generation endpoint
curl -X POST http://localhost:8001/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-123",
    "language": "english"
  }'
```

This should return a task_id that you can use to check status.
