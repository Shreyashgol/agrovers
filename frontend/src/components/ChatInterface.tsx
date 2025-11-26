// src/components/ChatInterface.tsx
import { useState, useEffect, useRef } from "react";
import { Language } from "../api/client";
import { LABELS } from "../config/labels";

interface Message {
  id: string;
  type: "ai" | "user";
  text: string;
  audioUrl?: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  parameter: string;
  question: string;
  language: Language;
  helperText?: string;
  audioUrl?: string;
  onSubmit: (message?: string, audioBlob?: Blob) => void;
  onHelpRequest: () => void;
  isSubmitting?: boolean;
}

export default function ChatInterface({
  parameter,
  question,
  language,
  helperText,
  audioUrl,
  onSubmit,
  onHelpRequest,
  isSubmitting = false,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const labels = LABELS[parameter]?.[language] || {
    question,
    options: [],
    placeholder: language === "hi" ? "उत्तर लिखें..." : "Type your answer...",
  };

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add AI message when question/helper changes
  useEffect(() => {
    const text = helperText || question;
    if (text) {
      // Check if this message already exists
      const messageExists = messages.some(m => m.text === text && m.type === "ai");
      
      if (!messageExists) {
        const newMessage: Message = {
          id: Date.now().toString(),
          type: "ai",
          text,
          audioUrl,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, newMessage]);
      }

      // Auto-play audio whenever audioUrl changes
      if (audioUrl && audioRef.current) {
        setIsAISpeaking(true);
        audioRef.current.src = audioUrl;
        audioRef.current.play().catch((err) => {
          console.error("Audio play failed:", err);
          setIsAISpeaking(false);
        });
      }
    }
  }, [question, helperText, audioUrl]);

  // Handle audio playback end
  const handleAudioEnd = () => {
    setIsAISpeaking(false);
  };

  // Handle option click
  const handleOptionClick = (option: string) => {
    if (isSubmitting) return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      text: option,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    
    onSubmit(option);
  };

  // Handle text submit
  const handleSubmitText = () => {
    if (!inputValue.trim() || isSubmitting) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      text: inputValue.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    
    onSubmit(inputValue.trim());
    setInputValue("");
  };

  // Handle voice recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: "audio/webm" });
        
        // Add user message (voice)
        const userMessage: Message = {
          id: Date.now().toString(),
          type: "user",
          text: language === "hi" ? "🎤 आवाज़ संदेश" : "🎤 Voice message",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMessage]);
        
        onSubmit(undefined, audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert(language === "hi" ? "माइक्रोफ़ोन एक्सेस नहीं मिला" : "Microphone access denied");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Hidden audio player */}
      <audio
        ref={audioRef}
        onEnded={handleAudioEnd}
        onPlay={() => setIsAISpeaking(true)}
        onPause={() => setIsAISpeaking(false)}
        className="hidden"
      />

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.type === "user"
                  ? "bg-emerald-600 text-white"
                  : "bg-gray-700 text-white"
              }`}
            >
              <p className="text-sm md:text-base whitespace-pre-wrap">{msg.text}</p>
              <span className="text-xs opacity-70 mt-1 block">
                {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick options */}
      {labels.options?.length > 0 && !isSubmitting && (
        <div className="px-6 pb-4">
          <div className="flex flex-wrap gap-2">
            {labels.options.map((opt) => (
              <button
                key={opt}
                onClick={() => handleOptionClick(opt)}
                className="px-4 py-2 rounded-full bg-emerald-700 text-white text-sm font-medium hover:bg-emerald-600 transition-colors"
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input area */}
      <div className="border-t border-gray-700 p-4 bg-gray-800">
        <div className="flex items-center gap-3">
          {/* Text input */}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSubmitText()}
            placeholder={labels.placeholder}
            disabled={isSubmitting || isRecording}
            className="flex-1 px-4 py-3 rounded-full bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />

          {/* Send button */}
          {inputValue.trim() && (
            <button
              onClick={handleSubmitText}
              disabled={isSubmitting}
              className="p-3 rounded-full bg-emerald-600 text-white hover:bg-emerald-500 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          )}

          {/* Mic button */}
          {!inputValue.trim() && (
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isSubmitting}
              className={`p-4 rounded-full transition-all ${
                isRecording
                  ? "bg-red-500 animate-pulse"
                  : isAISpeaking
                  ? "bg-emerald-500 animate-pulse"
                  : "bg-emerald-600 hover:bg-emerald-500"
              }`}
            >
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          )}

          {/* Help button */}
          <button
            onClick={onHelpRequest}
            disabled={isSubmitting}
            className="p-3 rounded-full bg-gray-700 text-white hover:bg-gray-600 transition-colors"
            title={language === "hi" ? "मदद चाहिए" : "Need help"}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
        </div>

        {/* Recording indicator */}
        {isRecording && (
          <div className="mt-3 flex items-center justify-center gap-2 text-red-400 text-sm">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            {language === "hi" ? "रिकॉर्डिंग..." : "Recording..."}
          </div>
        )}

        {/* AI speaking indicator */}
        {isAISpeaking && (
          <div className="mt-3 flex items-center justify-center gap-2 text-emerald-400 text-sm">
            <div className="flex gap-1">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="w-1 h-4 bg-emerald-500 rounded-full animate-pulse"
                  style={{ animationDelay: `${i * 0.15}s` }}
                ></div>
              ))}
            </div>
            {language === "hi" ? "AI बोल रहा है..." : "AI is speaking..."}
          </div>
        )}
      </div>
    </div>
  );
}
