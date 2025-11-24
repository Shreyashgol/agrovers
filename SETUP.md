# Quick Setup Guide

## Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add:
# GEMINI_API_KEY=your_gemini_api_key_here

# Preprocess knowledge base
python preprocess_kb.py

# Run server
uvicorn app.main:app --reload
```

Backend should be running at `http://localhost:8000`

## Step 2: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend should be running at `http://localhost:5173`

## Step 3: Test the Application

1. Open `http://localhost:5173` in browser
2. Select language (Hindi or English)
3. Go through the wizard steps
4. Try clicking "I don't know" to see helper mode

## Getting Gemini API Key

1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Add it to `backend/.env` as `GEMINI_API_KEY`

## Troubleshooting

### "RAG engine not initialized"
- Make sure you've run `python preprocess_kb.py`
- Check that markdown files are in `backend/app/data/kb_raw/`

### "LLM adapter initialization failed"
- Check `GEMINI_API_KEY` is set in `.env`
- Verify API key is valid

### CORS errors
- Ensure backend is running on port 8000
- Check `ALLOWED_ORIGINS` in `backend/app/config.py`

## Next Steps

1. Add your knowledge base markdown files
2. Run preprocessing
3. Test the full flow
4. Configure n8n webhook (when ready)

