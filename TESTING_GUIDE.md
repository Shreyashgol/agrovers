# Testing Guide - n8n Integration

## 🎯 Complete System is Running!

### Services Status
✅ **Backend API** - http://localhost:8001
✅ **Frontend** - http://localhost:5175
✅ **Mock n8n Server** - http://localhost:5678

---

## 🧪 How to Test the Complete Flow

### Step 1: Open the Application
```
Open your browser: http://localhost:5175
```

### Step 2: Complete the Wizard
1. Select language (English or Hindi)
2. Answer all 9 questions:
   - Name (e.g., "Ramesh Kumar")
   - Soil Color (e.g., "dark brown")
   - Moisture Level (e.g., "moist")
   - Soil Smell (e.g., "earthy")
   - pH Level (e.g., "6.5")
   - Soil Type (e.g., "loamy")
   - Earthworms (e.g., "yes")
   - Location (e.g., "Maharashtra, India")
   - Previous Fertilizers (e.g., "NPK 10-10-10")

### Step 3: Watch the Magic! ✨
After answering the last question, you'll see:

1. **Loading Screen** (2-5 seconds)
   - Animated progress bar
   - Progress stages:
     - 🌱 Preparing soil data (10%)
     - 🧪 Analyzing parameters (30%)
     - 📈 Generating recommendations (50%)
     - ✅ Report ready (100%)

2. **Comprehensive Report Display**
   - **Soil Analysis Section**
     - Health score with animated bar
     - Detailed assessment
     - Strengths (Pros) with green checkmarks
     - Areas to Watch (Cons) with yellow warnings
     - Rating badge (Excellent/Good/Fair)
   
   - **Crop Recommendations** (6 crops)
     - Sugarcane
     - Soybean
     - Cotton
     - Wheat
     - Onion
     - Chickpea
     - Each with reason and season info
   
   - **Fertilizer Recommendations** (6 fertilizers)
     - Organic (FYM, Bio-fertilizers)
     - Chemical (Urea, DAP+MOP, Sulphur, Micronutrients)
     - Each with:
       - Application rate
       - Timing
       - Purpose

---

## 🔍 Testing Individual Components

### Test 1: n8n Webhook Directly
```bash
curl -X POST http://localhost:5678/webhook/soil-report \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-123",
    "name": "Test Farmer",
    "soilColor": "dark brown",
    "moistureLevel": "moist",
    "soilSmell": "earthy",
    "phLevel": "6.5",
    "soilType": "loamy",
    "earthworms": "yes",
    "location": "Maharashtra",
    "previousFertilizers": "NPK",
    "preferredLanguage": "English"
  }'
```

**Expected:** JSON response with soilAnalysis, cropRecommendations, fertilizerRecommendations

### Test 2: Backend n8n Integration
```bash
cd backend
source .venv/bin/activate
python test_n8n_integration.py
```

**Expected:** ✅ n8n integration test PASSED!

### Test 3: Report API Endpoints

**Start Report Generation:**
```bash
# First, complete a session through the UI to get a session_id
# Then test the API:

curl -X POST http://localhost:8001/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID"}'
```

**Check Report Status:**
```bash
curl http://localhost:8001/api/reports/status/YOUR_SESSION_ID
```

**Download Report:**
```bash
curl http://localhost:8001/api/reports/download/YOUR_SESSION_ID
```

---

## 📊 What You Should See

### Loading Screen
```
┌─────────────────────────────────────┐
│  🌱 Generating Your Soil Report     │
│                                     │
│  ████████████░░░░░░░░░░░░  50%     │
│  Generating recommendations...      │
│                                     │
│  ✓ Preparing soil data              │
│  ✓ Analyzing parameters             │
│  ⟳ Generating recommendations       │
│  ○ Report ready                     │
└─────────────────────────────────────┘
```

### Report Display
```
┌─────────────────────────────────────────────────┐
│  🌱 Comprehensive Soil Health Report            │
│  📥 Download  📤 Share                          │
├─────────────────────────────────────────────────┤
│                                                 │
│  🧪 Soil Analysis                    ⭐ Excellent│
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  Soil Health Score: 95/100                      │
│                                                 │
│  Assessment: The soil sample demonstrates...    │
│                                                 │
│  ✅ Strengths          ⚠️ Areas to Watch        │
│  • Optimal pH          • Monitor micronutrients │
│  • Loamy soil type     • Avoid over-fertilizing │
│  • Rich organic matter • Test regularly         │
│                                                 │
│  🌾 Recommended Crops                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │Sugarcane │ │ Soybean  │ │  Cotton  │       │
│  │Kharif    │ │ Monsoon  │ │ Monsoon  │       │
│  └──────────┘ └──────────┘ └──────────┘       │
│                                                 │
│  🧪 Fertilizer Recommendations                  │
│  ┌─────────────────────────────────────────┐   │
│  │ Farmyard Manure (FYM)        [Organic]  │   │
│  │ 📍 5-10 tonnes per acre                 │   │
│  │ ⏰ 2-3 weeks before sowing              │   │
│  │ ✓ Enhances soil organic matter...      │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Issue: Loading screen stuck
**Solution:** Check backend logs for errors
```bash
# Check if backend is running
curl http://localhost:8001/health

# Check mock n8n server
curl http://localhost:5678/
```

### Issue: Report not displaying
**Solution:** Check browser console (F12)
- Look for API errors
- Check network tab for failed requests

### Issue: n8n webhook fails
**Solution:** Ensure mock server is running
```bash
# Check if port 5678 is in use
lsof -i :5678

# Restart mock server if needed
cd backend
source .venv/bin/activate
python mock_n8n_server.py
```

### Issue: Frontend not loading
**Solution:** Check if port is available
```bash
# Frontend should be on 5175
# If not, check start_frontend.sh output
```

---

## 🎨 UI Features to Test

### Animations
- [ ] Loading screen progress bar animates smoothly
- [ ] Report sections fade in sequentially
- [ ] Hover effects on crop cards
- [ ] Hover effects on fertilizer cards

### Responsiveness
- [ ] Works on desktop (1920x1080)
- [ ] Works on tablet (768x1024)
- [ ] Works on mobile (375x667)

### Interactions
- [ ] Download button (UI ready, functionality TODO)
- [ ] Share button (UI ready, functionality TODO)
- [ ] Start New Test button works
- [ ] Scroll behavior is smooth

---

## 📝 Sample Test Data

### Good Soil (Excellent Rating)
```json
{
  "soilColor": "dark brown",
  "moistureLevel": "moist",
  "soilSmell": "earthy",
  "phLevel": "6.5",
  "soilType": "loamy",
  "earthworms": "yes",
  "location": "Maharashtra, India",
  "previousFertilizers": "NPK 10-10-10"
}
```

### Average Soil (Good Rating)
```json
{
  "soilColor": "light brown",
  "moistureLevel": "slightly dry",
  "soilSmell": "mild",
  "phLevel": "7.0",
  "soilType": "sandy loam",
  "earthworms": "few",
  "location": "Maharashtra, India",
  "previousFertilizers": "None"
}
```

### Poor Soil (Fair Rating)
```json
{
  "soilColor": "gray",
  "moistureLevel": "dry",
  "soilSmell": "none",
  "phLevel": "8.0",
  "soilType": "sandy",
  "earthworms": "no",
  "location": "Maharashtra, India",
  "previousFertilizers": "None"
}
```

---

## ✅ Success Criteria

Your integration is working if:
- [x] All 3 services are running
- [x] You can complete the 9-question wizard
- [x] Loading screen appears after last question
- [x] Progress updates every 2 seconds
- [x] Report displays with all sections
- [x] Report shows 6 crop recommendations
- [x] Report shows 6 fertilizer recommendations
- [x] Animations are smooth
- [x] No console errors
- [x] Start New Test button works

---

## 🚀 Next Steps

### For Production
1. **Replace Mock Server** with real n8n
   - Update `backend/.env`:
     ```
     N8N_WEBHOOK_URL=https://algoshera.app.n8n.cloud/webhook-test/soil-analysis-v5
     ```
   - Activate your n8n workflow
   - Test with real webhook

2. **Add PDF Export**
   - Install `jspdf` or `react-pdf`
   - Implement download functionality
   - Style for print

3. **Add Share Functionality**
   - WhatsApp share
   - Email share
   - Copy link

4. **Deploy**
   - Backend to cloud (Railway, Render, etc.)
   - Frontend to Vercel/Netlify
   - n8n to n8n.cloud

---

## 📞 Support

If you encounter issues:
1. Check all services are running: `ps aux | grep -E "uvicorn|vite|python"`
2. Check logs in terminal windows
3. Check browser console (F12)
4. Verify ports: 8001 (backend), 5175 (frontend), 5678 (n8n)

**Happy Testing! 🎉**
