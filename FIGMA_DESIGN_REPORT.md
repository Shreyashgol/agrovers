# AGROVERS SOIL ASSISTANT - COMPLETE DESIGN SPECIFICATION
## Frontend & Backend Architecture Report for Figma Design

---

## 📋 TABLE OF CONTENTS
1. System Overview
2. User Flow & State Machine
3. Frontend Architecture
4. Backend Architecture
5. UI Components Specification
6. Color System & Typography
7. Data Models & API Contracts
8. Voice Features (STT/TTS)

---

## 1. SYSTEM OVERVIEW

### Purpose
An 8-step wizard that collects soil parameters from farmers through:
- Text input
- Voice recording (STT)
- Quick option buttons
- AI-powered helper mode with RAG (Retrieval Augmented Generation)

### Core Principles
- **Deterministic**: No hallucination, only KB-based responses
- **Sequential**: One parameter at a time, no skipping
- **Bilingual**: Full Hindi + English support
- **Accessible**: Voice input/output for low-literacy users
- **Offline-capable**: Local LLM support (Ollama)

---

## 2. USER FLOW & STATE MACHINE

### The 8 Steps (Fixed Order)

1. **Color** - Soil color identification
2. **Moisture** - Moisture level assessment
3. **Smell** - Odor characteristics
4. **pH** - Acidity/alkalinity (numeric or category)
5. **Soil Type** - Clay/Sandy/Loamy/Silty
6. **Earthworms** - Presence/absence
7. **Location** - Farm location (free text)
8. **Fertilizer Used** - Recent fertilizer application

### State Machine Logic

```
START SESSION
    ↓
[WAITING_FOR_ANSWER]
    ↓
User Input → Backend Validation
    ↓
    ├─→ VALID (confidence ≥ 60%) → Move to Next Step
    ├─→ INVALID (confidence < 60%) → [HELPER_MODE]
    └─→ HELP REQUEST ("I don't know") → [HELPER_MODE]

[HELPER_MODE]
    ↓
Show RAG-based guidance (yellow panel)
Stay on SAME step
Continue accepting input
    ↓
User provides valid answer → Move to Next Step

AFTER STEP 8
    ↓
[SUMMARY_PAGE]
    ↓
Show complete report + Download PDF
```

### Critical State Rules
- **NEVER skip steps** - Must collect all 8 parameters
- **NEVER guess** - If unclear, enter helper mode
- **NEVER show duplicate questions** - Only render on step change
- **Progress requests** ("next", "completed") → Re-ask same question

---

## 3. FRONTEND ARCHITECTURE

### Tech Stack

- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Build**: Vite
- **HTTP Client**: Axios
- **PDF Generation**: jsPDF
- **Audio**: Web Audio API + MediaRecorder

### File Structure
```
frontend/src/
├── pages/
│   └── SoilWizard.tsx          # Main wizard container
├── components/
│   ├── ChatInterface.tsx       # Chat UI with messages
│   ├── Stepper.tsx             # Progress sidebar
│   └── SummaryPage.tsx         # Final report
├── api/
│   └── client.ts               # API calls
├── config/
│   └── labels.ts               # Questions & options
└── types/
    └── index.ts                # TypeScript types
```

### Key Components

#### 3.1 SoilWizard (Main Container)
**Location**: `frontend/src/pages/SoilWizard.tsx`

**State Management**:
```typescript
const [sessionId, setSessionId] = useState<string | null>(null);
const [currentParameter, setCurrentParameter] = useState<string>("");
const [currentQuestion, setCurrentQuestion] = useState<string>("");
const [stepNumber, setStepNumber] = useState(1);
const [helperText, setHelperText] = useState<string | undefined>();
const [audioUrl, setAudioUrl] = useState<string | undefined>();
const [answers, setAnswers] = useState<SoilTestResult>({});
const [isComplete, setIsComplete] = useState(false);
```

**Lifecycle**:
1. `useEffect` on mount → Call `/api/v1/session/start`
2. Receive first question + session_id
3. User submits answer → Call `/api/v1/session/next`
4. Update state based on response
5. Repeat until `is_complete = true`
6. Show SummaryPage



#### 3.2 ChatInterface Component
**Location**: `frontend/src/components/ChatInterface.tsx`

**Props**:
```typescript
interface ChatInterfaceProps {
  parameter: string;           // Current parameter (e.g., "moisture")
  question: string;            // Question text
  language: Language;          // "hi" | "en"
  helperText?: string;         // RAG guidance (if helper mode)
  audioUrl?: string;           // TTS audio URL
  onSubmit: (message?: string, audioBlob?: Blob) => void;
  onHelpRequest: () => void;
  isSubmitting?: boolean;
}
```

**Features**:
- Message history (AI + User bubbles)
- Quick option buttons (from labels.ts)
- Text input with Enter key support
- Voice recording (MediaRecorder API)
- Audio playback (auto-play TTS responses)
- Help button ("I don't know")

**Current Bug** (to fix in Figma):
- Shows duplicate questions due to `useEffect` triggering on every prop change
- **Fix**: Only add message when `stepNumber` increases

#### 3.3 Stepper Component
**Location**: `frontend/src/components/Stepper.tsx`

**Visual Structure**:
```
┌─────────────────────────┐
│  Questions              │
│  ─────────────────────  │
│  ✓  1. Color            │ ← Completed (green)
│  ✓  2. Moisture         │ ← Completed (green)
│  →  3. Smell            │ ← Current (highlighted)
│  ○  4. pH               │ ← Pending (gray)
│  ○  5. Soil Type        │
│  ○  6. Earthworms       │
│  ○  7. Location         │
│  ○  8. Fertilizer       │
│                         │
│  Progress: 37%          │
│  ▓▓▓▓▓▓▓░░░░░░░░░░░     │
└─────────────────────────┘
```

**Props**:
```typescript
interface StepperProps {
  currentStep: number;
  totalSteps: number;
  currentParameter: string;
  language: Language;
  allParameters: string[];
  completedSteps: number;
}
```



#### 3.4 SummaryPage Component
**Location**: `frontend/src/components/SummaryPage.tsx`

**Display Format**:
```
┌─────────────────────────────────────┐
│         Soil Report Summary         │
│─────────────────────────────────────│
│ Color:           Black               │
│ Moisture:        Moist               │
│ Smell:           Earthy              │
│ pH Category:     Neutral             │
│ pH Value:        6.8                 │
│ Soil Type:       Loamy               │
│ Earthworms:      Many                │
│ Location:        Village, District   │
│ Fertilizer Used: Urea + DAP          │
│─────────────────────────────────────│
│                                      │
│  [Download PDF]  [Start New Test]   │
└─────────────────────────────────────┘
```

**Features**:
- Displays all collected parameters
- PDF export (jsPDF)
- Reset button to start new test

**Missing** (to add):
- Crop recommendations
- Fertilizer plan
- Water management advice
- Soil health score (0-100)

---

## 4. BACKEND ARCHITECTURE

### Tech Stack
- **Framework**: FastAPI (Python 3.11+)
- **LLM**: Ollama (local) or Gemini API
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector DB**: FAISS
- **STT**: Groq Whisper API
- **TTS**: gTTS (Google Text-to-Speech)
- **Webhook**: n8n integration

### File Structure
```
backend/app/
├── main.py                     # FastAPI app entry
├── config.py                   # Settings & env vars
├── models.py                   # Pydantic models
├── routes/
│   └── sessions.py             # API endpoints
└── services/
    ├── session_manager.py      # In-memory session store
    ├── orchestrator_enhanced.py # Main logic + confidence
    ├── validators_enhanced.py   # Semantic validation
    ├── answer_extractor.py      # LLM-based extraction
    ├── rag_engine.py            # FAISS retrieval
    ├── llm_adapter.py           # Ollama/Gemini wrapper
    ├── stt_service.py           # Speech-to-text
    ├── tts_service.py           # Text-to-speech
    └── n8n_client.py            # Webhook sender
```



### Core Services

#### 4.1 Orchestrator Enhanced
**Location**: `backend/app/services/orchestrator_enhanced.py`

**Confidence Fusion Algorithm**:
```python
combined_confidence = (
    0.20 * asr_confidence +      # Speech recognition quality
    0.60 * validator_confidence + # Semantic matching
    0.20 * llm_confidence         # Answer extraction
)

if combined_confidence >= 0.60:
    auto_fill_answer()
else:
    enter_helper_mode()
```

**Decision Flow**:
1. Check if "progress request" ("next", "completed") → Re-ask question
2. Check if "help request" ("I don't know", "help") → Helper mode
3. Try LLM answer extraction (confidence ≥ 0.80) → Accept
4. Try semantic validator → Accept if confident
5. If all fail → Helper mode with RAG

#### 4.2 Validators Enhanced
**Location**: `backend/app/services/validators_enhanced.py`

**Semantic Matching**:
- Uses sentence-transformers embeddings
- Computes cosine similarity between user input and canonical labels
- Accepts if similarity ≥ 0.60 (high) or ≥ 0.40 (medium)

**Example**:
```python
User: "मेरी मिट्टी काली है"
Canonical: ["black", "kali", "काली", "काला"]
Similarity: 0.92 → Accept as "black"
```

#### 4.3 RAG Engine
**Location**: `backend/app/services/rag_engine.py`

**Architecture**:
```
Knowledge Base (Markdown files)
    ↓
Chunking (500 chars, 50 overlap)
    ↓
Embedding (all-MiniLM-L6-v2)
    ↓
FAISS Index (484 chunks)
    ↓
Retrieval (top-k=8 chunks)
    ↓
LLM Context
```

**Query Templates**:
- Color: "How to identify soil color at home step by step"
- Moisture: "How to test soil moisture level at home step by step"
- pH: "How to test soil pH at home step by step"
- etc.



#### 4.4 LLM Adapter
**Location**: `backend/app/services/llm_adapter.py`

**Supported Providers**:
1. **Ollama** (Local) - gemma2:9b, llama3.2, phi3
2. **Gemini API** - gemini-2.5-flash, gemini-2.5-pro

**System Prompt** (Anti-Hallucination):
```
CRITICAL RULES:
1. Use ONLY and EXCLUSIVELY the provided context
2. Do NOT invent ANY information - this is strictly forbidden
3. If context is limited, provide guidance based on what's available
4. Speak in simple [Hindi/English]
5. Explain in 2-3 simple steps
```

**Temperature Settings**:
- Answer extraction: 0.1 (very deterministic)
- Helper mode: 0.3 (balanced)

---

## 5. UI COMPONENTS SPECIFICATION

### Layout Structure

```
┌──────────────────────────────────────────────────────────────┐
│  MAIN CONTAINER (max-w-6xl, h-[90vh])                        │
│  ┌────────────────┬──────────────────────────────────────┐  │
│  │  LEFT PANEL    │  RIGHT PANEL                         │  │
│  │  (w-64)        │  (flex-1)                            │  │
│  │                │                                       │  │
│  │  [STEPPER]     │  ┌─────────────────────────────────┐ │  │
│  │                │  │  HEADER                         │ │  │
│  │  Step 1 ✓      │  │  Soil Test Assistant            │ │  │
│  │  Step 2 ✓      │  │  Step 3 of 8                    │ │  │
│  │  Step 3 →      │  └─────────────────────────────────┘ │  │
│  │  Step 4 ○      │                                       │  │
│  │  Step 5 ○      │  ┌─────────────────────────────────┐ │  │
│  │  Step 6 ○      │  │  CHAT MESSAGES (scrollable)     │ │  │
│  │  Step 7 ○      │  │                                  │ │  │
│  │  Step 8 ○      │  │  [AI Bubble]                    │ │  │
│  │                │  │  What does your soil smell like?│ │  │
│  │  Progress: 37% │  │                                  │ │  │
│  │  ▓▓▓▓░░░░░░    │  │  [User Bubble]                  │ │  │
│  │                │  │  Earthy                          │ │  │
│  └────────────────┘  │                                  │ │  │
│                      │  [Helper Panel - Yellow]         │ │  │
│                      │  To test smell, take a handful...│ │  │
│                      └─────────────────────────────────┘ │  │
│                                                           │  │
│                      ┌─────────────────────────────────┐ │  │
│                      │  QUICK OPTIONS                  │ │  │
│                      │  [Earthy] [Sweet] [Sour]        │ │  │
│                      └─────────────────────────────────┘ │  │
│                                                           │  │
│                      ┌─────────────────────────────────┐ │  │
│                      │  INPUT BAR (sticky bottom)      │ │  │
│                      │  [Text Input] [🎤] [?]          │ │  │
│                      └─────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```



### Component Dimensions

| Component | Width | Height | Padding | Border Radius |
|-----------|-------|--------|---------|---------------|
| Main Container | max-w-6xl | 90vh | - | rounded-2xl |
| Left Panel | 256px (w-64) | 100% | p-6 | - |
| Right Panel | flex-1 | 100% | - | - |
| Header | 100% | auto | px-6 py-4 | - |
| Chat Area | 100% | flex-1 | p-6 | - |
| AI Bubble | max-w-[80%] | auto | px-4 py-3 | rounded-2xl |
| User Bubble | max-w-[80%] | auto | px-4 py-3 | rounded-2xl |
| Helper Panel | 100% | auto | p-3 | rounded-xl |
| Quick Option Button | auto | auto | px-4 py-2 | rounded-full |
| Input Bar | 100% | auto | p-4 | - |
| Text Input | flex-1 | 48px | px-4 py-3 | rounded-full |
| Mic Button | 48px | 48px | p-4 | rounded-full |
| Help Button | 40px | 40px | p-3 | rounded-full |

---

## 6. COLOR SYSTEM & TYPOGRAPHY

### Color Palette (Tailwind Classes)

#### Background Colors
```css
--bg-main: #0F172A          /* bg-slate-900 - Main app background */
--bg-panel: #1E293B         /* bg-slate-800 - Panels & cards */
--bg-sidebar: #334155       /* bg-slate-700 - Left sidebar */
--bg-input: #475569         /* bg-slate-600 - Input fields */
```

#### Message Bubbles
```css
--bubble-ai: #334155        /* bg-slate-700 - AI messages */
--bubble-user: #10B981      /* bg-emerald-600 - User messages */
--bubble-helper: #78350F    /* bg-yellow-900/40 - Helper mode */
```

#### Accent Colors
```css
--accent-primary: #10B981   /* bg-emerald-600 - Primary actions */
--accent-success: #22C55E   /* bg-green-500 - Success states */
--accent-warning: #EAB308   /* bg-yellow-500 - Helper mode */
--accent-error: #EF4444     /* bg-red-500 - Errors */
--accent-recording: #DC2626 /* bg-red-600 - Recording state */
```

#### Text Colors
```css
--text-primary: #F8FAFC     /* text-slate-50 - Primary text */
--text-secondary: #CBD5E1   /* text-slate-300 - Secondary text */
--text-muted: #94A3B8       /* text-slate-400 - Muted text */
--text-helper: #FDE047      /* text-yellow-200 - Helper text */
```

#### Border Colors
```css
--border-default: #475569   /* border-slate-600 */
--border-light: #334155     /* border-slate-700 */
--border-helper: #CA8A04    /* border-yellow-700 */
```



### Typography

#### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

#### Font Sizes
```css
--text-xs: 12px      /* text-xs - Timestamps, labels */
--text-sm: 14px      /* text-sm - Body text, buttons */
--text-base: 16px    /* text-base - Default text */
--text-lg: 18px      /* text-lg - Headings */
--text-xl: 20px      /* text-xl - Page titles */
--text-2xl: 24px     /* text-2xl - Main headings */
--text-3xl: 30px     /* text-3xl - Summary page title */
```

#### Font Weights
```css
--font-normal: 400   /* font-normal - Body text */
--font-medium: 500   /* font-medium - Buttons, labels */
--font-semibold: 600 /* font-semibold - Subheadings */
--font-bold: 700     /* font-bold - Main headings */
```

#### Line Heights
```css
--leading-tight: 1.25    /* leading-tight - Headings */
--leading-normal: 1.5    /* leading-normal - Body text */
--leading-relaxed: 1.625 /* leading-relaxed - Long text */
```

### Spacing System

```css
--space-1: 4px       /* gap-1, p-1 */
--space-2: 8px       /* gap-2, p-2 */
--space-3: 12px      /* gap-3, p-3 */
--space-4: 16px      /* gap-4, p-4 */
--space-6: 24px      /* gap-6, p-6 */
--space-8: 32px      /* gap-8, p-8 */
--space-12: 48px     /* gap-12, p-12 */
```

---

## 7. DATA MODELS & API CONTRACTS

### Frontend Types

```typescript
// Language selection
type Language = "hi" | "en";

// Soil test result (collected data)
interface SoilTestResult {
  color?: string;
  moisture?: string;
  smell?: string;
  ph_category?: string;
  ph_value?: number;
  soil_type?: string;
  earthworms?: string;
  location?: string;
  fertilizer_used?: string;
}

// API response for next step
interface NextMessageResponse {
  session_id: string;
  parameter: string;
  question?: string;           // Next question (if progressing)
  helper_text?: string;        // RAG guidance (if helper mode)
  answers: SoilTestResult;
  is_complete: boolean;
  step_number: number;
  total_steps: number;
  helper_mode: boolean;
  audio_url?: string;          // TTS audio URL
  audit?: {                    // Debug info
    asr_conf: number;
    validator_conf: number;
    llm_conf: number;
    combined_conf: number;
  };
}
```



### API Endpoints

#### 1. Start Session
```http
POST /api/v1/session/start
Content-Type: application/json

Request:
{
  "language": "hi" | "en"
}

Response:
{
  "session_id": "uuid-string",
  "parameter": "color",
  "question": "आपकी मिट्टी का रंग क्या है?",
  "step_number": 1,
  "total_steps": 8,
  "audio_url": "http://localhost:8001/audio/xyz.mp3"
}
```

#### 2. Submit Answer
```http
POST /api/v1/session/next
Content-Type: multipart/form-data

Request:
{
  "session_id": "uuid-string",
  "user_text": "काली" (optional),
  "audio_file": File (optional)
}

Response:
{
  "session_id": "uuid-string",
  "parameter": "moisture",
  "question": "आपकी मिट्टी में नमी कितनी है?",
  "helper_text": null,
  "answers": {
    "color": "black",
    "moisture": null,
    ...
  },
  "is_complete": false,
  "step_number": 2,
  "total_steps": 8,
  "helper_mode": false,
  "audio_url": "http://localhost:8001/audio/abc.mp3",
  "audit": {
    "asr_conf": 0.0,
    "validator_conf": 0.95,
    "llm_conf": 0.0,
    "combined_conf": 0.95
  }
}
```

#### 3. Get Session State
```http
GET /api/v1/session/state/{session_id}

Response:
{
  "session_id": "uuid-string",
  "language": "hi",
  "current_parameter": "moisture",
  "answers": { ... },
  "step_number": 2,
  "total_steps": 8,
  "is_complete": false
}
```

### Backend Models (Python)

```python
class SoilTestResult(BaseModel):
    color: Optional[str] = None
    moisture: Optional[str] = None
    smell: Optional[str] = None
    ph_category: Optional[str] = None
    ph_value: Optional[float] = None
    soil_type: Optional[str] = None
    earthworms: Optional[str] = None
    location: Optional[str] = None
    fertilizer_used: Optional[str] = None

class SessionState(BaseModel):
    session_id: str
    language: Language
    current_parameter: str
    answers: SoilTestResult
    helper_mode: bool = False
    created_at: float
    updated_at: float

class ValidationResult(BaseModel):
    value: Optional[str] = None
    ph_value: Optional[float] = None
    is_confident: bool
```



---

## 8. VOICE FEATURES (STT/TTS)

### Speech-to-Text (STT)

**Provider**: Groq Whisper API

**Flow**:
1. User clicks mic button → Start recording
2. MediaRecorder captures audio (webm format)
3. Stop recording → Create Blob
4. Send to `/api/v1/session/next` as `audio_file`
5. Backend transcribes via Groq API
6. Returns transcribed text + confidence score

**Audio Format**:
- Input: webm, mp3, wav
- Sample rate: 16kHz (recommended)
- Channels: Mono

**Confidence Scoring**:
```python
asr_confidence = groq_response.confidence  # 0.0 - 1.0
# Used in combined confidence calculation
```

### Text-to-Speech (TTS)

**Provider**: gTTS (Google Text-to-Speech)

**Flow**:
1. Backend generates response (question or helper text)
2. TTS service synthesizes audio
3. Saves to `backend/app/data/audio/{uuid}.mp3`
4. Returns URL: `http://localhost:8001/audio/{uuid}.mp3`
5. Frontend auto-plays audio

**Language Support**:
- Hindi: `lang='hi'`
- English: `lang='en'`

**Audio Storage**:
```
backend/app/data/audio/
├── 123e4567-e89b-12d3-a456-426614174000.mp3
├── 234e5678-e89b-12d3-a456-426614174001.mp3
└── ...
```

**Auto-play Logic** (Frontend):
```typescript
useEffect(() => {
  if (audioUrl && audioRef.current) {
    setIsAISpeaking(true);
    audioRef.current.src = audioUrl;
    audioRef.current.play();
  }
}, [audioUrl]);
```

---

## 9. HELPER MODE SPECIFICATION

### Visual Design

**Helper Panel** (Yellow Warning Style):
```
┌─────────────────────────────────────────────────────┐
│  ⚠️  How to Test Soil Moisture                      │
│─────────────────────────────────────────────────────│
│  किसान भाई, मिट्टी की नमी जांचने के लिए:          │
│                                                      │
│  1. मुट्ठी भर मिट्टी लें                            │
│  2. इसे हाथ में दबाएं                               │
│  3. अगर पानी निकले तो "गीली"                       │
│  4. अगर गोला बने तो "नम"                            │
│  5. अगर बिखर जाए तो "सूखी"                         │
└─────────────────────────────────────────────────────┘
```

**CSS Classes**:
```css
.helper-panel {
  background: rgba(120, 53, 15, 0.4);  /* bg-yellow-900/40 */
  border: 1px solid #CA8A04;           /* border-yellow-700 */
  color: #FDE047;                      /* text-yellow-200 */
  border-radius: 12px;                 /* rounded-xl */
  padding: 12px;                       /* p-3 */
}
```

### Trigger Conditions

Helper mode activates when:
1. User says "I don't know", "help", "मदद", "नहीं पता"
2. Validator confidence < 60%
3. No valid answer extracted by LLM

### Behavior Rules

When in helper mode:
- ✅ Show helper panel with RAG-based guidance
- ✅ Keep same step (don't progress)
- ✅ Keep quick option buttons visible
- ✅ Continue accepting input
- ✅ Generate TTS for helper text
- ❌ Don't show new question
- ❌ Don't increment step number

### Exit Helper Mode

User provides valid answer → Validator accepts → Progress to next step



---

## 10. PARAMETER DETAILS & OPTIONS

### Complete Parameter Specification

| Step | Parameter | Type | Options (EN) | Options (HI) | Validation |
|------|-----------|------|--------------|--------------|------------|
| 1 | color | Select | Black, Red, Brown, Yellow, Grey | काली, लाल, भूरी, पीली, स्लेटी | Semantic match |
| 2 | moisture | Select | Dry, Moist, Wet, Very Dry | सूखी, थोड़ी नम, बहुत गीली, बहुत सूखी | Semantic match |
| 3 | smell | Select | Earthy, Sweet, Sour, Rotten, No Smell | मिट्टी जैसी, थोड़ी मीठी, खट्टी, सड़ी हुई, कोई गंध नहीं | Semantic match |
| 4 | ph | Numeric/Select | Acidic, Neutral, Alkaline | अम्लीय, तटस्थ, क्षारीय | Numeric (0-14) or category |
| 5 | soil_type | Select | Clay, Sandy, Loamy, Silty | चिकनी, रेतिली, दोमट, गादयुक्त | Semantic match |
| 6 | earthworms | Select | Many, Few, None | बहुत, थोड़े, नहीं | Semantic match |
| 7 | location | Free Text | - | - | Min 3 chars |
| 8 | fertilizer_used | Free Text/Select | Urea, DAP, NPK, Organic, None | यूरिया, डीएपी, एनपीके, जैविक, कुछ नहीं | Free text or yes/no |

### Normalized Values (Backend)

All answers are normalized to English lowercase for consistency:

```python
NORMALIZED_VALUES = {
    "color": ["black", "red", "brown", "yellow", "grey"],
    "moisture": ["dry", "moist", "wet", "very_dry"],
    "smell": ["earthy", "sweet", "sour", "rotten", "no_smell"],
    "ph": ["very_acidic", "acidic", "neutral", "alkaline", "very_alkaline"],
    "soil_type": ["clay", "sandy", "loamy", "silt"],
    "earthworms": ["many", "few", "none", "yes", "no"],
    "location": "<free_text>",
    "fertilizer_used": "<free_text>"
}
```

---

## 11. RESPONSIVE DESIGN BREAKPOINTS

### Desktop (≥ 1024px)
- Two-column layout (sidebar + chat)
- Sidebar width: 256px
- Max container width: 1152px (max-w-6xl)
- Chat bubbles: max-w-[80%]

### Tablet (768px - 1023px)
- Sidebar collapses to top bar
- Full-width chat area
- Stepper shows as horizontal progress bar
- Chat bubbles: max-w-[85%]

### Mobile (< 768px)
- Single column layout
- Stepper as compact progress bar
- Full-width input
- Chat bubbles: max-w-[90%]
- Mic button larger (56px)

### Breakpoint Classes (Tailwind)
```css
sm: 640px   /* Small devices */
md: 768px   /* Medium devices */
lg: 1024px  /* Large devices */
xl: 1280px  /* Extra large devices */
```



---

## 12. INTERACTION STATES

### Button States

#### Primary Button (Quick Options)
```css
/* Default */
background: #10B981;  /* bg-emerald-600 */
color: #FFFFFF;
padding: 8px 16px;
border-radius: 9999px;

/* Hover */
background: #059669;  /* bg-emerald-700 */
transform: scale(1.02);

/* Active/Pressed */
background: #047857;  /* bg-emerald-800 */
transform: scale(0.98);

/* Disabled */
background: #6B7280;  /* bg-gray-500 */
opacity: 0.5;
cursor: not-allowed;
```

#### Mic Button States
```css
/* Default (Idle) */
background: #10B981;  /* bg-emerald-600 */
animation: none;

/* Recording */
background: #DC2626;  /* bg-red-600 */
animation: pulse 1.5s infinite;

/* AI Speaking */
background: #10B981;  /* bg-emerald-500 */
animation: pulse 2s infinite;
```

### Input States

```css
/* Default */
background: #475569;  /* bg-slate-600 */
border: 1px solid transparent;
outline: none;

/* Focus */
background: #475569;
border: 2px solid #10B981;  /* ring-emerald-500 */
outline: none;

/* Disabled */
background: #334155;  /* bg-slate-700 */
opacity: 0.6;
cursor: not-allowed;
```

### Loading States

#### Submitting Answer
```
┌─────────────────────────────────┐
│  [Spinner] Processing...        │
└─────────────────────────────────┘
```

#### AI Speaking
```
┌─────────────────────────────────┐
│  [Wave Animation] AI बोल रहा है │
└─────────────────────────────────┘
```

#### Recording
```
┌─────────────────────────────────┐
│  [Pulse Dot] रिकॉर्डिंग...      │
└─────────────────────────────────┘
```

---

## 13. ANIMATIONS & TRANSITIONS

### Message Appearance
```css
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-bubble {
  animation: slideIn 0.3s ease-out;
}
```

### Progress Bar
```css
.progress-bar {
  transition: width 0.5s ease-in-out;
}
```

### Button Hover
```css
.button {
  transition: all 0.2s ease;
}

.button:hover {
  transform: scale(1.05);
}
```

### Pulse Animation (Recording/Speaking)
```css
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.pulse {
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```



---

## 14. ACCESSIBILITY REQUIREMENTS

### Keyboard Navigation
- Tab order: Input → Send → Mic → Help → Options
- Enter key: Submit text input
- Escape key: Cancel recording
- Arrow keys: Navigate quick options

### Screen Reader Support
```html
<!-- Example ARIA labels -->
<button aria-label="Record voice message">🎤</button>
<button aria-label="Get help with this question">?</button>
<input aria-label="Enter your answer" />
<div role="status" aria-live="polite">AI is speaking...</div>
```

### Color Contrast
All text meets WCAG AA standards:
- Primary text on dark bg: 15:1 ratio
- Secondary text on dark bg: 7:1 ratio
- Button text on emerald bg: 4.5:1 ratio

### Focus Indicators
```css
*:focus-visible {
  outline: 2px solid #10B981;
  outline-offset: 2px;
}
```

---

## 15. ERROR HANDLING

### Error Types & Messages

#### Network Error
```
┌─────────────────────────────────────┐
│  ❌ Connection failed                │
│  Please check your internet         │
│  [Retry]                             │
└─────────────────────────────────────┘
```

#### Session Expired
```
┌─────────────────────────────────────┐
│  ⏱️ Session expired                  │
│  Please start a new test            │
│  [Start New Test]                   │
└─────────────────────────────────────┘
```

#### Microphone Access Denied
```
┌─────────────────────────────────────┐
│  🎤 Microphone access denied         │
│  Please enable in browser settings  │
│  [OK]                                │
└─────────────────────────────────────┘
```

#### Audio Playback Failed
```
┌─────────────────────────────────────┐
│  🔇 Audio playback failed            │
│  You can still read the text        │
│  [Dismiss]                           │
└─────────────────────────────────────┘
```

### Error State Styling
```css
.error-message {
  background: rgba(239, 68, 68, 0.1);  /* bg-red-500/10 */
  border: 1px solid #EF4444;           /* border-red-500 */
  color: #FCA5A5;                      /* text-red-300 */
  padding: 12px;
  border-radius: 8px;
}
```

---

## 16. PERFORMANCE CONSIDERATIONS

### Frontend Optimization
- Lazy load SummaryPage component
- Debounce text input (300ms)
- Virtualize message list (if > 50 messages)
- Compress audio before upload (webm codec)
- Cache audio files in browser

### Backend Optimization
- FAISS index loaded once at startup
- Session data in-memory (Redis for production)
- Audio files cleaned up after 1 hour
- LLM response streaming (future)
- Batch embedding generation

### Target Metrics
- Initial load: < 2s
- API response: < 1s (text), < 3s (audio)
- TTS generation: < 2s
- STT transcription: < 3s
- RAG retrieval: < 500ms



---

## 17. FUTURE ENHANCEMENTS (NOT YET IMPLEMENTED)

### Summary Page Additions
Currently missing, to be added:

#### Crop Recommendations
```
┌─────────────────────────────────────┐
│  🌾 Recommended Crops               │
│─────────────────────────────────────│
│  1. Cotton (कपास)                   │
│     - Best for black soil           │
│     - Requires moderate water       │
│                                      │
│  2. Soybean (सोयाबीन)               │
│     - Good for loamy soil           │
│     - Drought resistant             │
│                                      │
│  3. Okra (भिंडी)                    │
│     - Suitable for pH 6.5-7.5       │
│     - Short growing season          │
└─────────────────────────────────────┘
```

#### Fertilizer Plan
```
┌─────────────────────────────────────┐
│  🧪 Fertilizer Recommendations      │
│─────────────────────────────────────│
│  Base Application:                  │
│  • DAP: 50 kg/acre                  │
│  • Urea: 40 kg (split dose)         │
│                                      │
│  Top Dressing (after 30 days):      │
│  • Urea: 30 kg/acre                 │
│  • Potash: 20 kg/acre               │
└─────────────────────────────────────┘
```

#### Water Management
```
┌─────────────────────────────────────┐
│  💧 Water Management                │
│─────────────────────────────────────│
│  • Irrigate every 10-12 days        │
│  • Critical stages: Flowering       │
│  • Avoid waterlogging               │
│  • Mulching recommended             │
└─────────────────────────────────────┘
```

#### Soil Health Score
```
┌─────────────────────────────────────┐
│  📊 Soil Health Score               │
│─────────────────────────────────────│
│         ▓▓▓▓▓▓▓▓░░ 78/100           │
│                                      │
│  ✅ Good organic matter             │
│  ✅ Balanced pH                     │
│  ⚠️  Low nitrogen                   │
│  ✅ Good earthworm activity         │
└─────────────────────────────────────┘
```

### Additional Features
- **Multi-language support**: Add Marathi, Tamil, Telugu
- **Offline mode**: PWA with service workers
- **Photo upload**: Soil image analysis
- **Historical tracking**: Compare tests over time
- **Weather integration**: Local weather data
- **Market prices**: Crop price recommendations
- **Expert consultation**: Connect with agronomists

---

## 18. DEPLOYMENT CONFIGURATION

### Frontend (Vite)
```bash
# Development
npm run dev  # Port 5174

# Production build
npm run build
npm run preview
```

### Backend (FastAPI)
```bash
# Development
uvicorn app.main:app --reload --port 8001

# Production (with Gunicorn)
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Environment Variables

#### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8001
```

#### Backend (.env)
```bash
# LLM Configuration
LLM_PROVIDER=ollama
OLLAMA_MODEL_NAME=gemma2:9b
GEMINI_API_KEY=your-key-here

# STT/TTS
GROQ_API_KEY=your-key-here
ASR_PROVIDER=groq
TTS_PROVIDER=gtts

# Knowledge Base
KB_RAW_DIR=app/data/kb_raw
KB_PROCESSED_DIR=app/data/kb_processed
EMBEDDINGS_DIR=app/data/embeddings

# CORS
ALLOWED_ORIGINS=http://localhost:5174,http://localhost:5173
```

---

## 19. TESTING CHECKLIST

### Functional Testing
- [ ] Session creation works
- [ ] All 8 steps complete in order
- [ ] Quick options submit correctly
- [ ] Text input submits correctly
- [ ] Voice recording works
- [ ] Audio playback works
- [ ] Helper mode triggers correctly
- [ ] Helper mode exits correctly
- [ ] Summary page displays all data
- [ ] PDF download works
- [ ] Reset button works
- [ ] Language switching works

### Edge Cases
- [ ] Empty input handling
- [ ] Very long text input (> 500 chars)
- [ ] Special characters in input
- [ ] Network timeout handling
- [ ] Session expiry handling
- [ ] Microphone permission denied
- [ ] Audio playback failure
- [ ] Invalid session ID
- [ ] Concurrent requests

### Browser Compatibility
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

### Performance Testing
- [ ] Initial load < 2s
- [ ] API response < 1s
- [ ] Audio generation < 2s
- [ ] No memory leaks
- [ ] Smooth animations (60fps)

---

## 20. FIGMA DESIGN DELIVERABLES

### Required Screens
1. **Language Selection** (initial screen)
2. **Step 1-8 Screens** (one for each parameter)
3. **Helper Mode Variant** (with yellow panel)
4. **Summary Page** (with all sections)
5. **Error States** (network, session, mic)
6. **Loading States** (submitting, recording, speaking)

### Required Components
1. **Stepper** (sidebar + mobile variants)
2. **Message Bubble** (AI + User variants)
3. **Helper Panel** (yellow warning style)
4. **Quick Option Button** (all states)
5. **Input Bar** (with mic + help buttons)
6. **Progress Bar** (animated)
7. **Audio Indicator** (recording + speaking)

### Design System Export
- Color palette (all shades)
- Typography scale
- Spacing system
- Component library
- Icon set
- Animation specs

---

## SUMMARY

This report provides complete specifications for designing the Agrovers Soil Assistant in Figma. Key points:

- **8-step wizard** with strict sequential flow
- **Dark theme** with emerald accents
- **Bilingual** (Hindi + English)
- **Voice-enabled** (STT + TTS)
- **RAG-powered helper mode** (no hallucination)
- **Responsive design** (desktop, tablet, mobile)
- **Accessible** (WCAG AA compliant)

Use this document as the single source of truth for all design decisions.

---

**Document Version**: 1.0  
**Last Updated**: November 26, 2025  
**Author**: Agrovers Development Team
