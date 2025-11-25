// src/types/index.ts
export type Language = 'en' | 'hi';

export interface Message {
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export interface VoiceInputProps {
  onAudioRecorded: (audioBlob: Blob) => void;
  disabled?: boolean;
  language: Language;
  isRecording: boolean;
  onStartRecording: () => void;
  onStopRecording: () => void;
}