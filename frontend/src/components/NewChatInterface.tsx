import { useState, useEffect, useRef } from 'react';
import { Send, HelpCircle } from 'lucide-react';
import { Language } from '../api/client';
import { LABELS } from '../config/labels';
import { cn } from '../lib/utils';

// UI Components
import { AIAssistantCard } from './ui/AIAssistantCard';
import { UserMessageBubble } from './ui/UserMessageBubble';
import { StepCompletionCard } from './ui/StepCompletionCard';
import { QuickAnswerChip } from './ui/QuickAnswerChip';
import { VoiceInputButton } from './ui/VoiceInputButton';
import { AISpeakingIndicator } from './ui/AISpeakingIndicator';

interface Message {
  id: string;
  type: 'ai' | 'user' | 'completion';
  text?: string;
  isVoice?: boolean;
  duration?: string;
  timestamp: string;
  // For completion cards
  stepNumber?: number;
  parameter?: string;
  value?: string;
  displayValue?: string;
  colorSwatch?: string;
}

interface NewChatInterfaceProps {
  parameter: string;
  question: string;
  language: Language;
  helperText?: string;
  audioUrl?: string;
  onSubmit: (message?: string, audioBlob?: Blob) => void;
  onHelpRequest: () => void;
  isSubmitting?: boolean;
  stepNumber: number;
  lastAnswer?: { parameter: string; value: string; displayValue?: string };
}

export default function NewChatInterface({
  parameter,
  question,
  language,
  helperText,
  audioUrl,
  onSubmit,
  onHelpRequest,
  isSubmitting = false,
  stepNumber,
  lastAnswer
}: NewChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isAISpeaking, setIsAISpeaking] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  const [lastStepNumber, setLastStepNumber] = useState(-1); // Start at -1 to avoid double render on mount
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const labels = LABELS[parameter]?.[language] || {
    question,
    options: [],
    placeholder: language === 'hi' ? 'उत्तर लिखें...' : 'Type your answer...',
  };

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add AI question message ONLY when step changes
  useEffect(() => {
    if (question && stepNumber !== lastStepNumber && stepNumber > 0) {
      // If we have a last answer, show completion card first
      if (lastAnswer && lastStepNumber > 0) {
        const completionCard: Message = {
          id: `completion-${Date.now()}`,
          type: 'completion',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          stepNumber: lastStepNumber,
          parameter: lastAnswer.parameter,
          value: lastAnswer.value,
          displayValue: lastAnswer.displayValue,
        };
        setMessages((prev) => [...prev, completionCard]);
      }
      
      // Then add the new question
      const newMessage: Message = {
        id: `ai-${Date.now()}`,
        type: 'ai',
        text: question,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, newMessage]);
      setLastStepNumber(stepNumber);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [question, stepNumber]); // Removed lastAnswer from dependencies to prevent double rendering

  // Handle helper text - add as AI message in chat
  useEffect(() => {
    if (helperText) {
      const helperMessage: Message = {
        id: `helper-${Date.now()}`,
        type: 'ai',
        text: helperText,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, helperMessage]);
    }
  }, [helperText]);

  // Auto-play audio
  useEffect(() => {
    if (audioUrl && audioRef.current) {
      console.log('🔊 Playing audio:', audioUrl);
      setIsAISpeaking(true);
      audioRef.current.src = audioUrl;
      audioRef.current.play().catch((err) => {
        console.error('❌ Audio play failed:', err);
        setIsAISpeaking(false);
      });
    } else if (!audioUrl) {
      console.log('⚠️ No audio URL provided');
    }
  }, [audioUrl]);

  const handleAudioEnd = () => {
    setIsAISpeaking(false);
  };

  // Handle option click
  const handleOptionClick = (option: string) => {
    if (isSubmitting) return;
    
    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      text: option,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMessage]);
    
    // Submit immediately
    onSubmit(option);
  };

  // Handle text submit
  const handleSubmitText = () => {
    if (!inputValue.trim() || isSubmitting) return;
    
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      text: inputValue.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, userMessage]);
    
    onSubmit(inputValue.trim());
    setInputValue('');
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
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        
        // Add placeholder voice message (will be updated with transcription)
        const userMessage: Message = {
          id: `user-${Date.now()}`,
          type: 'user',
          text: language === 'hi' ? '🎤 प्रोसेसिंग...' : '🎤 Processing...',
          isVoice: true,
          duration: '0:12',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, userMessage]);
        
        onSubmit(undefined, audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert(language === 'hi' ? 'माइक्रोफ़ोन एक्सेस नहीं मिला' : 'Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const handleVoiceClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex flex-col h-full bg-agrovers-bg-primary">
      {/* Hidden audio player */}
      <audio
        ref={audioRef}
        onEnded={handleAudioEnd}
        className="hidden"
      />

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
        {messages.map((msg) => {
          if (msg.type === 'ai') {
            // Check if this is a helper message (contains steps or detailed guidance)
            const isHelper = msg.text?.includes('कदम') || msg.text?.includes('Step') || 
                           msg.text?.includes('1.') || msg.text?.includes('2.');
            
            return (
              <AIAssistantCard
                key={msg.id}
                message={msg.text || ''}
                timestamp={msg.timestamp}
                isHelper={isHelper}
              />
            );
          } else if (msg.type === 'user') {
            return (
              <UserMessageBubble
                key={msg.id}
                message={msg.text || ''}
                timestamp={msg.timestamp}
                isVoice={msg.isVoice}
                duration={msg.duration}
              />
            );
          } else if (msg.type === 'completion') {
            return (
              <StepCompletionCard
                key={msg.id}
                stepNumber={msg.stepNumber || 0}
                parameter={msg.parameter || ''}
                value={msg.value || ''}
                displayValue={msg.displayValue}
                colorSwatch={msg.colorSwatch}
              />
            );
          }
          return null;
        })}

        {/* AI Speaking Indicator */}
        {isAISpeaking && (
          <AISpeakingIndicator language={language} />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick options */}
      {labels.options?.length > 0 && !isSubmitting && (
        <div className="px-6 pb-4">
          <div className="flex flex-wrap gap-2">
            {labels.options.map((opt) => (
              <QuickAnswerChip
                key={opt}
                label={opt}
                onClick={() => handleOptionClick(opt)}
                disabled={isSubmitting}
              />
            ))}
          </div>
        </div>
      )}

      {/* Input area */}
      <div className="border-t border-agrovers-border-subtle bg-agrovers-bg-secondary p-4">
        <div className="flex items-center gap-3">
          {/* Voice Button (Large) */}
          <VoiceInputButton
            isRecording={isRecording}
            isAISpeaking={isAISpeaking}
            onClick={handleVoiceClick}
            disabled={isSubmitting}
            size="large"
          />

          {/* Text input */}
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSubmitText()}
            placeholder={labels.placeholder}
            disabled={isSubmitting || isRecording}
            className={cn(
              "flex-1 px-4 py-3 rounded-xl",
              "bg-agrovers-bg-elevated text-agrovers-text-primary placeholder-agrovers-text-muted",
              "focus:outline-none focus:ring-2 focus:ring-agrovers-accent-primary/50",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "transition-all duration-200"
            )}
          />

          {/* Send button */}
          {inputValue.trim() && (
            <button
              onClick={handleSubmitText}
              disabled={isSubmitting}
              className="w-12 h-12 rounded-xl bg-agrovers-accent-primary hover:bg-agrovers-accent-primary/90 flex items-center justify-center transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          )}

          {/* Help button */}
          <button
            onClick={onHelpRequest}
            disabled={isSubmitting}
            className="w-12 h-12 rounded-xl bg-agrovers-bg-elevated hover:bg-agrovers-bg-tertiary flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title={language === 'hi' ? 'मदद चाहिए' : 'Need help'}
          >
            <HelpCircle className="w-5 h-5 text-agrovers-text-secondary" />
          </button>
        </div>

        {/* Recording indicator */}
        {isRecording && (
          <div className="mt-3 flex items-center justify-center gap-2 text-agrovers-accent-error text-sm">
            <div className="w-2 h-2 bg-agrovers-accent-error rounded-full animate-pulse"></div>
            {language === 'hi' ? 'रिकॉर्डिंग...' : 'Recording...'}
          </div>
        )}
      </div>


    </div>
  );
}
