# 🚀 Quick Start Guide - Voice-Enabled Soil Assistant

## Prerequisites

- Python 3.11+
- Node.js 18+
- Modern browser (Chrome/Firefox/Edge)

## 1. Backend Setup (5 minutes)

```bash
# Navigate to backend
cd backend

# Activate virtual environment
source .venv/bin/activate  # Mac/Linux
# OR
.venv\Scripts\activate     # Windows

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload --port 8000
```

**✅ Backend running on:** http://localhost:8000

## 2. Frontend Setup (3 minutes)

```bash
# Open new terminal
cd frontend

# Install dependencies (if not already done)
npm install

# Start frontend
npm run dev
```

**✅ Frontend running on:** http://localhost:5173

## 3. Test It! (2 minutes)

1. **Open browser:** http://localhost:5173
2. **Select language:** Hindi or English
3. **Try text input:**
   - Click "Type" mode
   - Enter "black" for soil color
   - Click Submit
4. **Try voice input:**
   - Click "Speak" mode
   - Click "Tap to speak"
   - Say "black soil"
   - Click Send
5. **Listen to response:**
   - Audio plays automatically
   - Use controls to replay

## 4. Check It Works

### Backend Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "rag_ready": true
}
```

### API Documentation
Open: http://localhost:8000/docs

### Browser Console
Open DevTools (F12) → Console
Look for confidence scores:
```javascript
Confidence scores: {
  asr_conf: 0.85,
  validator_conf: 0.95,
  combined_conf: 0.87
}
```

## 5. Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9  # Mac/Linux
# OR
netstat -ano | findstr :8000   # Windows

# Restart backend
uvicorn app.main:app --reload --port 8000
```

### Frontend won't start
```bash
# Clear node modules
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Microphone not working
1. Check browser permissions (🔒 icon in address bar)
2. Allow microphone access
3. Refresh page
4. Try different browser

### Audio not playing
1. Check backend is running
2. Verify audio URL in Network tab
3. Check browser audio permissions
4. Try manual play button

## 6. Configuration

### Change API Keys

Edit `backend/.env`:
```env
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```

Restart backend after changes.

### Change Language

In frontend, select language at start.
Or modify default in `frontend/src/App.tsx`.

### Change Confidence Thresholds

Edit `backend/app/services/orchestrator_enhanced.py`:
```python
# Line ~15
AUTO_FILL_THRESHOLD = 0.80  # Change this

# Line ~10-12
W_ASR = 0.35        # ASR weight
W_VALIDATOR = 0.35  # Validator weight
W_LLM = 0.30        # LLM weight
```

## 7. Next Steps

### For Testing
- Test all 8 parameters
- Try both languages
- Test on mobile device
- Check confidence scores

### For Development
- Read `COMPLETE_IMPLEMENTATION_SUMMARY.md`
- Check `VOICE_FEATURES_IMPLEMENTATION.md`
- Review API docs at `/docs`

### For Deployment
- Set up HTTPS
- Configure production URLs
- Set up n8n webhook
- Add monitoring

## 8. Common Commands

### Backend
```bash
# Start
uvicorn app.main:app --reload

# Test
python test_voice_features.py

# Check logs
tail -f logs/app.log  # if logging configured
```

### Frontend
```bash
# Start dev
npm run dev

# Build production
npm run build

# Preview production
npm run preview
```

## 9. File Locations

### Configuration
- Backend: `backend/.env`
- Frontend: `frontend/src/api/client.ts` (API_BASE_URL)

### Logs
- Backend: Console output
- Frontend: Browser DevTools → Console

### Audio Files
- TTS cache: `backend/app/data/audio/`
- Recordings: Temporary (not saved)

## 10. Support

### Documentation
- `COMPLETE_IMPLEMENTATION_SUMMARY.md` - Full overview
- `VOICE_FEATURES_IMPLEMENTATION.md` - Backend details
- `frontend/VOICE_FEATURES_README.md` - Frontend details

### API Reference
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Debugging
- Backend logs: Terminal where uvicorn is running
- Frontend logs: Browser DevTools → Console
- Network: Browser DevTools → Network tab

---

## ✅ Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can select language
- [ ] Can type answers
- [ ] Can record audio
- [ ] Can hear TTS responses
- [ ] Confidence scores in console
- [ ] All 8 parameters work

**If all checked, you're ready to go!** 🎉

---

**Need help?** Check the documentation files or open an issue.
