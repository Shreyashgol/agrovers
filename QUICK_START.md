# 🚀 Quick Start - n8n Integration

## ✅ System Status

All services are **RUNNING** and **READY**:

```
✅ Backend:     http://localhost:8001
✅ Frontend:    http://localhost:5174
✅ Mock n8n:    http://localhost:5678
```

---

## 🎯 Test It NOW!

### 1. Open Browser
```
http://localhost:5174
```

### 2. Complete Wizard
Answer these 9 questions:
1. **Name**: Ramesh Kumar
2. **Soil Color**: dark brown
3. **Moisture**: moist
4. **Smell**: earthy
5. **pH Level**: 6.5
6. **Soil Type**: loamy
7. **Earthworms**: yes
8. **Location**: Maharashtra, India
9. **Previous Fertilizers**: NPK 10-10-10

### 3. Watch the Magic! ✨
- Loading screen appears
- Progress bar animates (10% → 30% → 50% → 100%)
- Beautiful report displays with:
  - Soil health score
  - Strengths & weaknesses
  - 6 crop recommendations
  - 6 fertilizer recommendations

---

## 🧪 Quick Tests

### Test n8n Webhook
```bash
curl -X POST http://localhost:5678/webhook/soil-report \
  -H "Content-Type: application/json" \
  -d '{"id":"test","name":"Test","soilColor":"dark brown","moistureLevel":"moist","soilSmell":"earthy","phLevel":"6.5","soilType":"loamy","earthworms":"yes","location":"Maharashtra","previousFertilizers":"NPK","preferredLanguage":"English"}'
```

### Test Backend Integration
```bash
cd backend && source .venv/bin/activate && python test_n8n_integration.py
```

---

## 📁 Key Files

### Backend
- `backend/app/services/n8n_service.py` - n8n integration
- `backend/app/routes/reports.py` - Report API
- `backend/mock_n8n_server.py` - Mock server

### Frontend
- `frontend/src/components/ui/ComprehensiveSoilReport.tsx` - Report UI
- `frontend/src/components/ui/ReportLoadingScreen.tsx` - Loading UI
- `frontend/src/pages/NewSoilWizard.tsx` - Main wizard

---

## 🔧 For Production

### 1. Update n8n URL
Edit `backend/.env`:
```bash
N8N_WEBHOOK_URL=https://algoshera.app.n8n.cloud/webhook-test/soil-analysis-v5
```

### 2. Activate n8n Workflow
- Open n8n
- Click "Activate" button
- Test with sample data

### 3. Stop Mock Server
```bash
# Find and stop the mock server process
ps aux | grep mock_n8n_server
kill <PID>
```

### 4. Restart Backend
```bash
# Backend will now use real n8n
bash start_backend.sh
```

---

## 🎨 What You'll See

### Loading Screen
```
┌────────────────────────────────┐
│ 🌱 Generating Your Soil Report │
│                                │
│ ████████████░░░░░░░░  50%     │
│ Generating recommendations...  │
│                                │
│ ✓ Preparing soil data          │
│ ✓ Analyzing parameters         │
│ ⟳ Generating recommendations   │
│ ○ Report ready                 │
└────────────────────────────────┘
```

### Report Sections
1. **Soil Analysis** - Score, assessment, pros/cons
2. **Crop Recommendations** - 6 crops with seasons
3. **Fertilizer Recommendations** - 6 fertilizers with details

---

## 🐛 Troubleshooting

### Services Not Running?
```bash
# Check processes
ps aux | grep -E "uvicorn|vite|python"

# Restart if needed
bash start_backend.sh
bash start_frontend.sh
cd backend && source .venv/bin/activate && python mock_n8n_server.py
```

### Port Already in Use?
```bash
# Kill processes on ports
lsof -ti:8001 | xargs kill  # Backend
lsof -ti:5174 | xargs kill  # Frontend
lsof -ti:5678 | xargs kill  # Mock n8n
```

### Report Not Showing?
- Open browser console (F12)
- Check for errors
- Verify all services are running

---

## 📚 Full Documentation

- **FINAL_SUMMARY.md** - Complete overview
- **TESTING_GUIDE.md** - Detailed testing instructions
- **N8N_INTEGRATION_GUIDE.md** - Technical documentation

---

## ✨ That's It!

Your n8n integration is **COMPLETE** and **WORKING**!

Open **http://localhost:5174** and test it now! 🎉
