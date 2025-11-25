// src/components/ParameterStep.tsx
import React, { useState } from "react";
import { Language } from "../api/client";
import HelpPanel from "./HelpPanel";
import { VoiceInput } from "./VoiceInput";
import { AudioPlayer } from "./AudioPlayer";
import { LABELS } from "../config/labels";

interface ParameterStepProps {
  parameter: string;
  question: string;
  language: Language;
  helperText?: string;
  audioUrl?: string;
  onSubmit: (message?: string, audioBlob?: Blob) => void;
  onHelpRequest: () => void;
  isSubmitting?: boolean;
}

export default function ParameterStep({
  parameter,
  question,
  language,
  helperText,
  audioUrl,
  onSubmit,
  onHelpRequest,
  isSubmitting = false,
}: ParameterStepProps) {
  const [inputValue, setInputValue] = useState("");
  const [inputMode, setInputMode] = useState<"text" | "voice">("text");

  const labels = LABELS[parameter]?.[language] || {
    question,
    options: [],
    placeholder: language === "hi" ? "उत्तर लिखें..." : "Enter answer...",
    helpButton: language === "hi" ? "मदद चाहिए" : "Need help",
  };

  const handleOptionClick = (option: string) => {
    if (isSubmitting) return;
    onSubmit(option);
  };

  const handleSubmitText = () => {
    if (!inputValue.trim() || isSubmitting) return;
    onSubmit(inputValue.trim());
    setInputValue("");
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{question}</h2>
        <p className="text-sm text-neutral-500">
          {language === "hi" ? "ईमानदारी से जवाब दें — यह बेहतर सुझाव देगा।" : "Answer honestly — this gives better suggestions."}
        </p>
      </div>

      {/* Options grid (big buttons) */}
      {labels.options?.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {labels.options.map((opt) => (
            <button
              key={opt}
              onClick={() => handleOptionClick(opt)}
              disabled={isSubmitting}
              className="py-4 rounded-xl bg-emerald-700 text-white font-semibold text-lg hover:bg-emerald-600 transition-shadow shadow-md"
            >
              {opt}
            </button>
          ))}
        </div>
      )}

      {/* Type/Speak toggles */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setInputMode("text")}
          className={`px-4 py-2 rounded-full font-medium ${inputMode === "text" ? "bg-emerald-600 text-white" : "bg-white/80 text-emerald-700"}`}
        >
          ⌨️ {language === "hi" ? "टाइप" : "Type"}
        </button>

        <button
          onClick={() => setInputMode("voice")}
          className={`px-4 py-2 rounded-full font-medium ${inputMode === "voice" ? "bg-emerald-600 text-white" : "bg-white/80 text-emerald-700"}`}
        >
          🎙️ {language === "hi" ? "बोलें" : "Speak"}
        </button>
      </div>

      {/* Text input */}
      {inputMode === "text" && (
        <>
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={labels.placeholder}
            className="w-full p-4 rounded-xl border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-emerald-400 text-lg bg-white/95"
            rows={4}
          />
          <div className="flex gap-3">
            <button
              onClick={handleSubmitText}
              disabled={isSubmitting || !inputValue.trim()}
              className="flex-1 py-3 rounded-xl bg-emerald-700 text-white font-semibold hover:bg-emerald-600"
            >
              {language === "hi" ? "जमा करें" : "Submit"}
            </button>

            <button
              onClick={onHelpRequest}
              disabled={isSubmitting}
              className="px-5 py-3 rounded-xl bg-white/90 text-emerald-700 font-medium"
            >
              {language === "hi" ? "मदद चाहिए" : "I don't know / Need help"}
            </button>
          </div>
        </>
      )}

      {/* Voice input */}
      {inputMode === "voice" && (
        <>
          <VoiceInput
            onAudioRecorded={(blob) => onSubmit(undefined, blob)}
            disabled={isSubmitting}
            language={language}
          />
          <div className="mt-2">
            <button
              onClick={onHelpRequest}
              disabled={isSubmitting}
              className="w-full py-3 rounded-xl bg-white/90 text-emerald-700 font-medium"
            >
              {language === "hi" ? "मदद चाहिए" : "I don't know / Need help"}
            </button>
          </div>
        </>
      )}

      {/* Audio response playback */}
      {audioUrl && (
        <div className="mt-4">
          <AudioPlayer audioUrl={audioUrl} autoPlay onEnded={() => {}} />
        </div>
      )}

      {/* Helper panel */}
      {helperText && <HelpPanel helperText={helperText} />}
    </div>
  );
}
