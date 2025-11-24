/**
 * Parameter Step Component
 * 
 * Displays question, options, and input for current parameter.
 * Handles user input submission.
 */

import { useState } from 'react';
import { Language } from '../api/client';
import { LABELS } from '../config/labels';
import HelpPanel from './HelpPanel';
import { VoiceInput } from './VoiceInput';
import { AudioPlayer } from './AudioPlayer';

interface ParameterStepProps {
  parameter: string;
  question: string;
  language: Language;
  helperText?: string;
  audioUrl?: string;
  onSubmit: (message?: string, audioBlob?: Blob) => void;
  onHelpRequest: () => void;
}

export default function ParameterStep({
  parameter,
  question,
  language,
  helperText,
  audioUrl,
  onSubmit,
  onHelpRequest,
}: ParameterStepProps) {
  const [inputValue, setInputValue] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [inputMode, setInputMode] = useState<'text' | 'voice'>('text');
  
  const labels = LABELS[parameter]?.[language] || {
    question: question,
    options: [],
    placeholder: 'Enter your answer...',
    helpButton: 'Need help?',
  };
  
  const handleSubmit = async (value?: string, audioBlob?: Blob) => {
    if (!value?.trim() && !audioBlob && !isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      await onSubmit(value?.trim(), audioBlob);
    } finally {
      setIsSubmitting(false);
      setInputValue('');
    }
  };
  
  const handleVoiceSubmit = (audioBlob: Blob) => {
    handleSubmit(undefined, audioBlob);
  };
  
  const handleOptionClick = (option: string) => {
    handleSubmit(option);
  };
  
  return (
    <div className="space-y-6">
      {/* Question */}
      <div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          {question}
        </h2>
      </div>
      
      {/* Options */}
      {labels.options.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {labels.options.map((option) => (
            <button
              key={option}
              onClick={() => handleOptionClick(option)}
              disabled={isSubmitting}
              className="py-4 px-6 bg-white border-2 border-gray-300 rounded-lg text-lg font-medium text-gray-700 hover:border-blue-500 hover:bg-blue-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {option}
            </button>
          ))}
        </div>
      )}
      
      {/* Input Mode Toggle */}
      <div className="flex gap-2 justify-center">
        <button
          onClick={() => setInputMode('text')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            inputMode === 'text'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          ⌨️ {language === 'hi' ? 'टाइप करें' : 'Type'}
        </button>
        <button
          onClick={() => setInputMode('voice')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            inputMode === 'voice'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
        >
          🎤 {language === 'hi' ? 'बोलें' : 'Speak'}
        </button>
      </div>

      {/* Text Input Mode */}
      {inputMode === 'text' && (
        <div className="space-y-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !isSubmitting) {
                handleSubmit(inputValue);
              }
            }}
            placeholder={labels.placeholder}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-lg focus:outline-none focus:border-blue-500"
            disabled={isSubmitting}
          />
          
          <div className="flex gap-3">
            <button
              onClick={() => handleSubmit(inputValue)}
              disabled={isSubmitting || (!inputValue.trim() && labels.options.length === 0)}
              className="flex-1 py-3 px-6 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '...' : language === 'hi' ? 'जमा करें' : 'Submit'}
            </button>
            
            <button
              onClick={onHelpRequest}
              disabled={isSubmitting}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg text-lg font-medium hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {labels.helpButton}
            </button>
          </div>
        </div>
      )}

      {/* Voice Input Mode */}
      {inputMode === 'voice' && (
        <div className="space-y-3">
          <VoiceInput
            onAudioRecorded={handleVoiceSubmit}
            disabled={isSubmitting}
            language={language}
          />
          
          <button
            onClick={onHelpRequest}
            disabled={isSubmitting}
            className="w-full px-6 py-3 bg-gray-200 text-gray-700 rounded-lg text-lg font-medium hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {labels.helpButton}
          </button>
        </div>
      )}
      
      {/* Audio Response */}
      {audioUrl && (
        <div className="mt-4">
          <AudioPlayer audioUrl={audioUrl} autoPlay={true} />
        </div>
      )}

      {/* Help panel */}
      {helperText && (
        <HelpPanel helperText={helperText} />
      )}
    </div>
  );
}

