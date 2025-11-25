// src/pages/SoilWizard.tsx
import { useState, useEffect } from "react";
import { Language, NextMessageResponse, SoilTestResult } from "../api/client";
import { startSession, sendNext } from "../api/client";

import Stepper from "../components/Stepper";
import ParameterStep from "../components/ParameterStep";
import SummaryPage from "../components/SummaryPage";

import { PARAMETER_ORDER } from "../config/labels";   // IMPORTANT FIX

interface SoilWizardProps {
  language: Language;
  onReset: () => void;
}

export default function SoilWizard({ language, onReset }: SoilWizardProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Steps & parameters
  const [currentParameter, setCurrentParameter] = useState<string>("");
  const [currentQuestion, setCurrentQuestion] = useState<string>("");
  const [stepNumber, setStepNumber] = useState(1);
  const [totalSteps, setTotalSteps] = useState(8);
  const [completedSteps, setCompletedSteps] = useState(0);  // NEW FIX

  // Extra data
  const [helperText, setHelperText] = useState<string | undefined>();
  const [audioUrl, setAudioUrl] = useState<string | undefined>();
  const [answers, setAnswers] = useState<SoilTestResult>({});
  const [isComplete, setIsComplete] = useState(false);

  // Loading + error
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // ============================
  // START SESSION
  // ============================
  useEffect(() => {
    const init = async () => {
      try {
        setIsLoading(true);
        const res = await startSession(language);

        setSessionId(res.session_id);
        setCurrentParameter(res.parameter);
        setCurrentQuestion(res.question);
        setStepNumber(res.step_number);
        setTotalSteps(res.total_steps);

        setCompletedSteps(0); // Reset sidebar
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to start session");
      } finally {
        setIsLoading(false);
      }
    };

    init();
  }, [language]);

  // ============================
  // SUBMIT ANSWER
  // ============================
  const handleSubmit = async (message?: string, audioBlob?: Blob) => {
    if (!sessionId) return;

    try {
      setIsLoading(true);
      setError(null);

      const res: NextMessageResponse = await sendNext(sessionId, message, audioBlob);

      setCurrentParameter(res.parameter);
      setAnswers(res.answers);
      setStepNumber(res.step_number);
      setTotalSteps(res.total_steps);

      // update sidebar completed steps
      setCompletedSteps(res.step_number - 1);

      setAudioUrl(res.audio_url);

      if (res.is_complete) {
        setIsComplete(true);
        setHelperText(undefined);
        setAudioUrl(undefined);
      } else if (res.helper_mode && res.helper_text) {
        setHelperText(res.helper_text);
      } else if (res.question) {
        setCurrentQuestion(res.question);
        setHelperText(undefined);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to submit answer");
    } finally {
      setIsLoading(false);
    }
  };

  const handleHelpRequest = () => handleSubmit("help");

  // ============================
  // RENDER
  // ============================

  if (isLoading && !sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center text-xl text-gray-600">
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center text-center">
        <div>
          <p className="text-red-500 mb-4">{error}</p>
          <button onClick={onReset} className="px-6 py-2 bg-blue-600 text-white rounded-lg">
            {language === "hi" ? "वापस जाएं" : "Go Back"}
          </button>
        </div>
      </div>
    );
  }

  if (isComplete) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <SummaryPage answers={answers} language={language} isComplete={true} />

        <div className="text-center mt-6">
          <button
            onClick={onReset}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700"
          >
            {language === "hi" ? "नया टेस्ट शुरू करें" : "Start New Test"}
          </button>
        </div>
      </div>
    );
  }

 return (
  <div className="min-h-screen bg-gray-900 py-10 px-4 flex justify-center">
    <div className="w-full max-w-6xl bg-[#0f1818] rounded-2xl shadow-xl p-6 md:p-10 flex gap-8">

      {/* Sidebar */}
      <Stepper
        currentStep={stepNumber}
        totalSteps={totalSteps}
        currentParameter={currentParameter}
        language={language}
        allParameters={PARAMETER_ORDER}
        completedSteps={stepNumber - 1}
      />

      {/* Question + Options */}
      <div className="flex-1">
        <div className="mb-6">
          <div className="text-xl font-bold text-white">
            {currentQuestion}
          </div>
          <p className="text-sm text-gray-300 mt-1">
            ईमानदारी से जवाब दें — यह बेहतर सुझाव देगा।
          </p>
        </div>

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
          <div className="mt-4 text-center text-gray-400">Processing...</div>
        )}
      </div>
    </div>
  </div>
);

}
