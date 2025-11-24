/**
 * Voice Input Component
 * 
 * Provides microphone button for voice input
 * Shows recording state and waveform animation
 */

import { useAudioRecorder } from '../hooks/useAudioRecorder';

interface VoiceInputProps {
  onAudioRecorded: (audioBlob: Blob) => void;
  disabled?: boolean;
  language: 'hi' | 'en';
}

export function VoiceInput({ onAudioRecorded, disabled, language }: VoiceInputProps) {
  const {
    isRecording,
    audioBlob,
    startRecording,
    stopRecording,
    error,
    clearAudio,
  } = useAudioRecorder();

  const handleToggleRecording = async () => {
    if (isRecording) {
      stopRecording();
    } else {
      await startRecording();
    }
  };

  const handleSendAudio = () => {
    if (audioBlob) {
      onAudioRecorded(audioBlob);
      clearAudio();
    }
  };

  const handleCancel = () => {
    clearAudio();
  };

  const labels = {
    hi: {
      record: 'रिकॉर्ड करें',
      recording: 'रिकॉर्डिंग...',
      send: 'भेजें',
      cancel: 'रद्द करें',
      tapToRecord: 'बोलने के लिए टैप करें',
    },
    en: {
      record: 'Record',
      recording: 'Recording...',
      send: 'Send',
      cancel: 'Cancel',
      tapToRecord: 'Tap to speak',
    },
  };

  const label = labels[language];

  return (
    <div className="flex flex-col gap-2">
      {/* Recording Button */}
      <button
        type="button"
        onClick={handleToggleRecording}
        disabled={disabled || !!audioBlob}
        className={`
          flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium
          transition-all duration-200
          ${isRecording
            ? 'bg-red-500 text-white animate-pulse'
            : 'bg-blue-500 text-white hover:bg-blue-600'
          }
          ${(disabled || audioBlob) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        {isRecording ? (
          <>
            <span className="inline-block w-3 h-3 bg-white rounded-full animate-ping" />
            {label.recording}
          </>
        ) : (
          <>
            🎤 {label.tapToRecord}
          </>
        )}
      </button>

      {/* Recording Animation */}
      {isRecording && (
        <div className="flex items-center justify-center gap-1 py-2">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-red-500 rounded-full animate-pulse"
              style={{
                height: `${Math.random() * 20 + 10}px`,
                animationDelay: `${i * 0.1}s`,
              }}
            />
          ))}
        </div>
      )}

      {/* Audio Preview & Actions */}
      {audioBlob && !isRecording && (
        <div className="flex flex-col gap-2 p-3 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-600">
            ✓ Audio recorded ({(audioBlob.size / 1024).toFixed(1)} KB)
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleSendAudio}
              className="flex-1 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              {label.send}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="flex-1 px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              {label.cancel}
            </button>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="text-sm text-red-600 p-2 bg-red-50 rounded">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
