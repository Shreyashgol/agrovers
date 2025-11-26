# Intent Classifier Test Cases

## ✅ Should Detect as ANSWER (and move to next step)

### Color Parameter
- ✅ "Black" → answer
- ✅ "काली" → answer
- ✅ "My soil is red" → answer
- ✅ "It's brown" → answer
- ✅ "dark" → answer
- ✅ "भूरा है" → answer

### Moisture Parameter
- ✅ "Dry" → answer
- ✅ "सूखी" → answer
- ✅ "It's wet" → answer
- ✅ "Moist" → answer
- ✅ "Very dry" → answer
- ✅ "थोड़ी नम" → answer

### Smell Parameter
- ✅ "Sweet" → answer
- ✅ "मीठी" → answer
- ✅ "Earthy" → answer
- ✅ "No smell" → answer
- ✅ "Sour" → answer
- ✅ "खट्टी है" → answer

### pH Parameter
- ✅ "Acidic" → answer
- ✅ "अम्लीय" → answer
- ✅ "Neutral" → answer
- ✅ "तटस्थ" → answer
- ✅ "Alkaline" → answer
- ✅ "7.0" → answer
- ✅ "6.5" → answer
- ✅ "pH is 7" → answer

### Soil Type Parameter
- ✅ "Clay" → answer
- ✅ "चिकनी" → answer
- ✅ "Sandy" → answer
- ✅ "Loamy" → answer
- ✅ "दोमट" → answer

### Earthworms Parameter
- ✅ "Yes" → answer
- ✅ "हाँ" → answer
- ✅ "No" → answer
- ✅ "Many" → answer
- ✅ "Few" → answer
- ✅ "बहुत" → answer

### Location Parameter
- ✅ "Village, District, State" → answer
- ✅ "गाँव, जिला" → answer
- ✅ "Mumbai" → answer

### Fertilizer Parameter
- ✅ "Urea" → answer
- ✅ "यूरिया" → answer
- ✅ "DAP" → answer
- ✅ "None" → answer
- ✅ "कुछ नहीं" → answer

---

## ❌ Should Detect as HELP_REQUEST (stay on same step, show guidance)

### All Parameters
- ❌ "I don't know" → help
- ❌ "नहीं पता" → help
- ❌ "Help" → help
- ❌ "मदद" → help
- ❌ "How to check?" → help
- ❌ "कैसे जांचें?" → help
- ❌ "Explain" → help
- ❌ "समझाओ" → help
- ❌ "Guide me" → help
- ❌ "मुझे बताओ" → help
- ❌ "What should I do?" → help
- ❌ "Show me steps" → help
- ❌ "Need all the steps" → help

---

## 🎯 Current Implementation Logic

1. **First Check**: Does message contain any valid answer keyword for this parameter?
   - YES → Return "answer" (confidence: 0.95)
   
2. **Second Check**: Does message contain help phrases?
   - YES → Return "help_request" (confidence: 0.95)
   
3. **Third Check**: Is message very short (1-2 words)?
   - YES → Return "answer" (confidence: 0.85)
   
4. **Final Check**: Use LLM classification for ambiguous cases
   - Returns "answer" or "help_request" with confidence

---

## 📊 Expected Behavior

### Scenario 1: User provides clear answer
```
User: "Acidic"
Intent: answer (0.95)
Action: Extract → Validate → Move to next step
```

### Scenario 2: User asks for help
```
User: "I don't know how to check"
Intent: help_request (0.95)
Action: Show RAG guidance → Stay on same step
```

### Scenario 3: User provides answer in sentence
```
User: "My soil color is red"
Intent: answer (0.95) [contains "red"]
Action: Extract "red" → Validate → Move to next step
```

### Scenario 4: Ambiguous case
```
User: "Can you tell me what this means?"
Intent: help_request (LLM classification)
Action: Show guidance
```

---

## ✅ Test Results

All test cases should pass with the updated intent classifier that includes:
- 100+ valid answer keywords across all parameters
- Both English and Hindi support
- Transliterated variations (kali, lal, etc.)
- Numeric pH values
- Common phrases and variations
