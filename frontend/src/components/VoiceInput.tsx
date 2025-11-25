// src/components/VoiceInput.tsx
import React from "react";
import { useAudioRecorder } from "../hooks/useAudioRecorder";

interface VoiceInputProps {
  onAudioRecorded: (audioBlob: Blob) => void;
  disabled?: boolean;
  language: "hi" | "en";
}

export function VoiceInput({ onAudioRecorded, disabled, language }: VoiceInputProps) {
  const { isRecording, audioBlob, startRecording, stopRecording, error, clearAudio } = useAudioRecorder();

  const labels = {
    hi: { record: "रिकॉर्ड करें", recording: "रिकॉर्डिंग...", send: "भेजें", cancel: "रद्द करें", tap: "बोलने के लिए टैप करें" },
    en: { record: "Record", recording: "Recording...", send: "Send", cancel: "Cancel", tap: "Tap to speak" },
  }[language];

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <button
          onClick={() => (isRecording ? stopRecording() : startRecording())}
          disabled={disabled}
          className={`flex items-center gap-3 px-5 py-3 rounded-full font-semibold ${
            isRecording ? "bg-red-500 text-white animate-pulse" : "bg-emerald-600 text-white"
          }`}
        >
          {isRecording ? "⏺ " + labels.recording : "🎤 " + labels.tap}
        </button>

        {!isRecording && audioBlob && (
          <>
            <button onClick={() => onAudioRecorded(audioBlob)} className="px-4 py-2 bg-green-600 text-white rounded-lg">{labels.send}</button>
            <button onClick={() => clearAudio()} className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg">{labels.cancel}</button>
          </>
        )}
      </div>

      {isRecording && (
        <div className="flex gap-1">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="w-2 rounded" style={{ height: `${10 + Math.random() * 20}px`, background: "#34D399" }} />
          ))}
        </div>
      )}

      {error && <div className="text-sm text-red-600 bg-red-50 p-2 rounded">{error}</div>}
    </div>
  );
}
