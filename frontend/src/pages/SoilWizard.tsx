/**
 * Soil Wizard Page
 * 
 * Main wizard component that orchestrates the multi-step flow.
 * Manages session state and coordinates between components.
 */

import { useState, useEffect } from 'react';
import { Language, NextMessageResponse, SoilTestResult } from '../api/client';
import { startSession, sendNext } from '../api/client';
import Stepper from '../components/Stepper';
import ParameterStep from '../components/ParameterStep';
import SummaryPage from '../components/SummaryPage';

interface SoilWizardProps {
  language: Language;
  onReset: () => void;
}

export default function SoilWizard({ language, onReset }: SoilWizardProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentParameter, setCurrentParameter] = useState<string>('');
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [stepNumber, setStepNumber] = useState(1);
  const [totalSteps, setTotalSteps] = useState(8);
  const [helperText, setHelperText] = useState<string | undefined>();
  const [audioUrl, setAudioUrl] = useState<string | undefined>();
  const [answers, setAnswers] = useState<SoilTestResult>({});
  const [isComplete, setIsComplete] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        setIsLoading(true);
        const response = await startSession(language);
        setSessionId(response.session_id);
        setCurrentParameter(response.parameter);
        setCurrentQuestion(response.question);
        setStepNumber(response.step_number);
        setTotalSteps(response.total_steps);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to start session');
      } finally {
        setIsLoading(false);
      }
    };
    
    initSession();
  }, [language]);
  
  const handleSubmit = async (message?: string, audioBlob?: Blob) => {
    if (!sessionId) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      const response: NextMessageResponse = await sendNext(sessionId, message, audioBlob);
      
      // Update state from response
      setCurrentParameter(response.parameter);
      setAnswers(response.answers);
      setStepNumber(response.step_number);
      setTotalSteps(response.total_steps);
      setAudioUrl(response.audio_url);
      
      // Log audit data for debugging
      if (response.audit) {
        console.log('Confidence scores:', response.audit);
      }
      
      if (response.is_complete) {
        setIsComplete(true);
        setHelperText(undefined);
        setAudioUrl(undefined);
      } else if (response.helper_mode && response.helper_text) {
        // Stay on same step, show helper
        setHelperText(response.helper_text);
      } else if (response.question) {
        // Move to next step
        setCurrentQuestion(response.question);
        setHelperText(undefined);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit answer');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleHelpRequest = () => {
    handleSubmit('help');
  };
  
  if (isLoading && !sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={onReset}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg"
          >
            {language === 'hi' ? 'वापस जाएं' : 'Go Back'}
          </button>
        </div>
      </div>
    );
  }
  
  if (isComplete) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <SummaryPage
          answers={answers}
          language={language}
          isComplete={isComplete}
        />
        <div className="text-center mt-6">
          <button
            onClick={onReset}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700"
          >
            {language === 'hi' ? 'नया परीक्षण शुरू करें' : 'Start New Test'}
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <Stepper
            currentStep={stepNumber}
            totalSteps={totalSteps}
            currentParameter={currentParameter}
            language={language}
          />
          
          <ParameterStep
            parameter={currentParameter}
            question={currentQuestion}
            language={language}
            helperText={helperText}
            audioUrl={audioUrl}
            onSubmit={handleSubmit}
            onHelpRequest={handleHelpRequest}
          />
          
          {isLoading && (
            <div className="mt-4 text-center text-gray-600">
              Processing...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

