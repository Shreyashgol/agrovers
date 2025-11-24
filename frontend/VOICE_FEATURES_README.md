# Voice Features - Frontend Integration

## ✅ What's Been Added

### New Components

1. **VoiceInput** (`src/components/VoiceInput.tsx`)
   - Microphone button with recording animation
   - Audio preview before sending
   - Send/Cancel actions
   - Bilingual labels (Hindi/English)

2. **AudioPlayer** (`src/components/AudioPlayer.tsx`)
   - Plays TTS responses from backend
   - Auto-play support
   - Audio controls
   - Error handling

3. **useAudioRecorder** (`src/hooks/useAudioRecorder.ts`)
   - Custom React hook for audio recording
   - MediaRecorder API integration
   - Recording state management
   - Error handling

### Updated Components

1. **ParameterStep** (`src/components/ParameterStep.tsx`)
   - Added input mode toggle (Type/Speak)
   - Integrated VoiceInput component
   - Integrated AudioPlayer for responses
   - Updated to handle audio blobs

2. **SoilWizard** (`src/pages/SoilWizard.tsx`)
   - Updated to handle audio submissions
   - Added audio URL state
   - Logs confidence scores to console

3. **API Client** (`src/api/client.ts`)
   - Updated `sendNext()` to support multipart form data
   - Added audio_url and audit fields to response type
   - Handles both text and audio input

## 🎯 Features

### Voice Input
- 🎤 **Record Audio:** Tap microphone button to start recording
- 🔴 **Recording Animation:** Visual feedback while recording
- ✅ **Preview:** Review audio before sending
- 🗑️ **Cancel:** Discard recording if needed
- 📤 **Send:** Submit audio to backend for STT

### Voice Output
- 🔊 **Auto-play:** TTS responses play automatically
- ⏯️ **Controls:** Standard audio controls (play/pause/seek)
- 🎵 **Caching:** Backend caches TTS files for reuse

### Input Modes
- ⌨️ **Type Mode:** Traditional text input (default)
- 🎤 **Speak Mode:** Voice input with recording
- 🔄 **Easy Toggle:** Switch between modes anytime

## 🚀 How to Use

### For Users

1. **Start the wizard** and select language
2. **Choose input mode:**
   - Click "Type" for text input
   - Click "Speak" for voice input
3. **Voice input:**
   - Tap "Tap to speak" button
   - Speak your answer
   - Tap again to stop recording
   - Review and click "Send"
4. **Listen to responses:**
   - Audio responses play automatically
   - Use controls to replay if needed

### For Developers

#### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: http://localhost:5173

#### Testing Voice Features

1. **Ensure backend is running** on http://localhost:8000
2. **Open browser** and navigate to frontend
3. **Allow microphone access** when prompted
4. **Test recording:**
   - Click "Speak" mode
   - Record a short message
   - Check browser console for confidence scores

#### Browser Requirements

- **Chrome/Edge:** Full support ✅
- **Firefox:** Full support ✅
- **Safari:** Partial support (may need HTTPS) ⚠️
- **Mobile browsers:** Varies by device

**Note:** Microphone access requires:
- HTTPS (in production)
- User permission
- Secure context

## 📊 Confidence Scores

The frontend logs confidence scores to the browser console:

```javascript
{
  asr_conf: 0.85,        // Speech recognition confidence
  validator_conf: 0.95,  // Validation confidence
  llm_conf: 0.80,        // LLM helper confidence
  combined_conf: 0.87,   // Combined score
  asr_text: "black soil" // Transcribed text
}
```

**Thresholds:**
- `>= 0.80`: Auto-advance to next question
- `< 0.80`: Show helper mode

## 🎨 UI/UX Features

### Recording State
- **Idle:** Blue microphone button
- **Recording:** Red pulsing button with waveform animation
- **Recorded:** Green preview with Send/Cancel buttons

### Audio Playback
- **Playing:** Shows "🔊 Playing..." indicator
- **Controls:** Standard HTML5 audio controls
- **Error:** Shows warning if playback fails

### Responsive Design
- **Mobile-friendly:** Touch-optimized buttons
- **Tablet:** Optimized layout
- **Desktop:** Full-featured experience

## 🔧 Configuration

### Audio Settings

In `src/hooks/useAudioRecorder.ts`:

```typescript
const stream = await navigator.mediaDevices.getUserMedia({ 
  audio: {
    echoCancellation: true,    // Reduce echo
    noiseSuppression: true,    // Reduce background noise
    sampleRate: 16000,         // Good for speech
  } 
});
```

### Recording Format

Currently using `audio/webm` (widely supported). Can be changed in:

```typescript
const mediaRecorder = new MediaRecorder(stream, {
  mimeType: 'audio/webm', // or 'audio/mp4', 'audio/ogg'
});
```

## 🐛 Troubleshooting

### Microphone Not Working

**Issue:** "Could not access microphone"

**Solutions:**
1. Check browser permissions
2. Ensure HTTPS (or localhost)
3. Try different browser
4. Check system microphone settings

### Audio Not Playing

**Issue:** TTS audio doesn't play

**Solutions:**
1. Check backend is running
2. Verify audio URL in network tab
3. Check browser audio permissions
4. Try manual play button

### Recording Quality Poor

**Issue:** STT confidence low

**Solutions:**
1. Speak clearly and slowly
2. Reduce background noise
3. Use better microphone
4. Check audio settings in hook

## 📱 Mobile Support

### iOS Safari
- Requires user interaction to start recording
- May need HTTPS for microphone access
- Audio playback works well

### Android Chrome
- Full support for recording
- Good audio quality
- Auto-play may be blocked (user must tap)

### Progressive Web App (PWA)
- Can be installed as app
- Better microphone access
- Offline support (future)

## 🔐 Privacy & Security

### Microphone Access
- Requested only when needed
- User can deny/revoke anytime
- No recording without permission

### Audio Data
- Sent to backend via HTTPS
- Not stored on frontend
- Backend processes and discards

### TTS Audio
- Cached on backend for performance
- Served via static files
- No personal data in audio

## 🎯 Future Enhancements

### Planned Features
- [ ] Waveform visualization during recording
- [ ] Audio level meter
- [ ] Playback speed control
- [ ] Download audio responses
- [ ] Offline recording (PWA)
- [ ] Multiple language detection
- [ ] Real-time transcription preview

### Performance Optimizations
- [ ] Lazy load audio components
- [ ] Compress audio before upload
- [ ] Cache TTS responses locally
- [ ] Reduce bundle size

## 📚 API Reference

### VoiceInput Props

```typescript
interface VoiceInputProps {
  onAudioRecorded: (audioBlob: Blob) => void;
  disabled?: boolean;
  language: 'hi' | 'en';
}
```

### AudioPlayer Props

```typescript
interface AudioPlayerProps {
  audioUrl: string;
  autoPlay?: boolean;
  onEnded?: () => void;
}
```

### useAudioRecorder Return

```typescript
interface UseAudioRecorderReturn {
  isRecording: boolean;
  audioBlob: Blob | null;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  error: string | null;
  clearAudio: () => void;
}
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] Record audio in English
- [ ] Record audio in Hindi
- [ ] Test with clear speech
- [ ] Test with background noise
- [ ] Test cancel recording
- [ ] Test audio playback
- [ ] Test on mobile device
- [ ] Test with slow internet
- [ ] Test error handling
- [ ] Test mode switching

### Automated Testing (Future)

```bash
# Unit tests
npm run test

# E2E tests
npm run test:e2e
```

## 📖 Documentation

- **Backend API:** See `VOICE_FEATURES_IMPLEMENTATION.md`
- **Component Docs:** See inline JSDoc comments
- **API Client:** See `src/api/client.ts`

## 🎉 Summary

**Voice features are fully integrated!**

Users can now:
- ✅ Record voice input
- ✅ Listen to audio responses
- ✅ Switch between text and voice
- ✅ See confidence scores (console)
- ✅ Use in Hindi or English

**Ready for user testing!** 🚀
