# AGROVERS - QUICK DESIGN REFERENCE

## 🎨 COLOR PALETTE

### Backgrounds
- Main: `#0F172A` (slate-900)
- Panel: `#1E293B` (slate-800)
- Sidebar: `#334155` (slate-700)
- Input: `#475569` (slate-600)

### Accents
- Primary: `#10B981` (emerald-600)
- Success: `#22C55E` (green-500)
- Warning: `#EAB308` (yellow-500)
- Error: `#EF4444` (red-500)

### Text
- Primary: `#F8FAFC` (slate-50)
- Secondary: `#CBD5E1` (slate-300)
- Muted: `#94A3B8` (slate-400)

## 📐 LAYOUT

```
┌────────────────────────────────────────┐
│  Sidebar (256px)  │  Chat (flex-1)    │
│  ─────────────────┼───────────────────│
│  Step 1 ✓         │  Header           │
│  Step 2 ✓         │  ─────────────────│
│  Step 3 →         │  Messages         │
│  Step 4 ○         │  (scrollable)     │
│  Step 5 ○         │                   │
│  Step 6 ○         │  ─────────────────│
│  Step 7 ○         │  Quick Options    │
│  Step 8 ○         │  ─────────────────│
│                   │  Input Bar        │
└────────────────────────────────────────┘
```

## 🔤 TYPOGRAPHY

- Font: Inter
- Sizes: 12px, 14px, 16px, 18px, 20px, 24px, 30px
- Weights: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

## 📱 COMPONENTS

### Message Bubble
- Max width: 80%
- Padding: 16px
- Border radius: 16px
- AI: slate-700 background
- User: emerald-600 background

### Quick Option Button
- Padding: 8px 16px
- Border radius: 9999px (full)
- Background: emerald-600
- Hover: emerald-700

### Input Bar
- Height: 48px
- Padding: 16px
- Border radius: 9999px (full)
- Background: slate-600

### Helper Panel
- Background: yellow-900/40
- Border: yellow-700
- Text: yellow-200
- Border radius: 12px

## 🎯 KEY INTERACTIONS

1. **Text Input**: Type → Enter → Submit
2. **Voice Input**: Click mic → Record → Click again → Submit
3. **Quick Options**: Click button → Submit immediately
4. **Help**: Click ? → Show helper panel → Stay on same step
5. **Progress**: Complete answer → Auto-advance to next step

## 📊 THE 8 STEPS

1. Color (काली, लाल, भूरी, पीली, स्लेटी)
2. Moisture (सूखी, नम, गीली)
3. Smell (मिट्टी जैसी, मीठी, खट्टी)
4. pH (अम्लीय, तटस्थ, क्षारीय)
5. Soil Type (चिकनी, रेतिली, दोमट)
6. Earthworms (बहुत, थोड़े, नहीं)
7. Location (free text)
8. Fertilizer (यूरिया, डीएपी, एनपीके)

## 🔊 AUDIO STATES

- **Idle**: Emerald mic button
- **Recording**: Red pulsing mic
- **AI Speaking**: Emerald pulsing + wave animation
- **Playback**: Auto-play TTS responses

## ⚠️ HELPER MODE

Triggers when:
- User says "I don't know" / "मदद"
- Confidence < 60%
- Invalid answer

Shows:
- Yellow warning panel
- RAG-based guidance
- Stays on same step
- Keeps accepting input

## 📄 SUMMARY PAGE

Displays:
- All 8 collected parameters
- Download PDF button
- Start New Test button

To add (future):
- Crop recommendations
- Fertilizer plan
- Water management
- Soil health score

## 🌐 API ENDPOINTS

- `POST /api/v1/session/start` - Start session
- `POST /api/v1/session/next` - Submit answer
- `GET /api/v1/session/state/{id}` - Get state

## 🎬 ANIMATIONS

- Message appear: slideIn 0.3s
- Progress bar: width 0.5s
- Button hover: scale 1.05
- Pulse: 1.5s infinite (recording/speaking)
