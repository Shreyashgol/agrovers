import { useState, useEffect } from 'react';
import { Language, NextMessageResponse, SoilTestResult } from '../api/client';
import { startSession, sendNext } from '../api/client';
import { generateReport, getReportStatus, ReportStatus } from '../api/reports';

// Layout & Components
import { MainLayout } from '../components/layout/MainLayout';
import { ProgressStepper } from '../components/ui/ProgressStepper';
import NewChatInterface from '../components/NewChatInterface';
import SummaryPage from '../components/SummaryPage';
import { SoilReportDisplay } from '../components/ui/SoilReportDisplay';
import { ComprehensiveSoilReport } from '../components/ui/ComprehensiveSoilReport';
import { ReportLoadingScreen } from '../components/ui/ReportLoadingScreen';

import { PARAMETER_ORDER } from '../config/labels';

interface NewSoilWizardProps {
  language: Language;
  onReset: () => void;
}

// Parameter labels for stepper
const PARAMETER_LABELS: Record<string, Record<Language, string>> = {
  name: { en: 'Your Name', hi: 'आपका नाम' },
  color: { en: 'Soil Color', hi: 'मिट्टी का रंग' },
  moisture: { en: 'Moisture', hi: 'नमी' },
  smell: { en: 'Smell Test', hi: 'गंध परीक्षण' },
  ph: { en: 'pH Level', hi: 'pH स्तर' },
  soil_type: { en: 'Soil Type', hi: 'मिट्टी का प्रकार' },
  earthworms: { en: 'Biological Activity', hi: 'जैविक गतिविधि' },
  location: { en: 'Location', hi: 'स्थान' },
  fertilizer_used: { en: 'Fertilizer History', hi: 'खाद इतिहास' },
};

export default function NewSoilWizard({ language, onReset }: NewSoilWizardProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentParameter, setCurrentParameter] = useState<string>('');
  const [currentQuestion, setCurrentQuestion] = useState<string>('');
  const [stepNumber, setStepNumber] = useState(1);
  const [helperText, setHelperText] = useState<string | undefined>();
  const [audioUrl, setAudioUrl] = useState<string | undefined>();
  const [answers, setAnswers] = useState<SoilTestResult>({});
  const [isComplete, setIsComplete] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [lastAnswer, setLastAnswer] = useState<{ parameter: string; value: string; displayValue?: string } | undefined>();
  
  // Report generation states
  const [reportStatus, setReportStatus] = useState<ReportStatus | null>(null);
  const [generatedReport, setGeneratedReport] = useState<any>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  // Initialize session
  useEffect(() => {
    const init = async () => {
      try {
        setIsLoading(true);
        const res = await startSession(language);

        setSessionId(res.session_id);
        setCurrentParameter(res.parameter);
        setCurrentQuestion(res.question);
        setStepNumber(res.step_number);
        
        if ('audio_url' in res) {
          setAudioUrl((res as any).audio_url);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to start session');
      } finally {
        setIsLoading(false);
      }
    };

    init();
  }, [language]);

  // Submit answer
  const handleSubmit = async (message?: string, audioBlob?: Blob) => {
    if (!sessionId) return;

    try {
      setIsLoading(true);
      setError(null);

      const res: NextMessageResponse = await sendNext(sessionId, message, audioBlob);

      // Track what answer was accepted (for completion card)
      if (!res.helper_mode && res.step_number > stepNumber) {
        // Step progressed - capture the accepted answer
        const prevParam = currentParameter;
        const acceptedValue = (res.answers as any)[prevParam];
        if (acceptedValue) {
          setLastAnswer({
            parameter: prevParam,
            value: acceptedValue,
            displayValue: message || acceptedValue,
          });
        }
      }

      setCurrentParameter(res.parameter);
      setAnswers(res.answers);
      setStepNumber(res.step_number);
      setAudioUrl(res.audio_url);

      if (res.is_complete) {
        setIsComplete(true);
        setHelperText(undefined);
        setAudioUrl(undefined);
        
        // Trigger report generation (don't await - let it run in background)
        triggerReportGeneration().catch(console.error);
        setHelperText(undefined);
        setAudioUrl(undefined);
        // Trigger report generation
        generateReport(sessionId);
      } else if (res.helper_mode && res.helper_text) {
        setHelperText(res.helper_text);
      } else if (res.question) {
        setCurrentQuestion(res.question);
        setHelperText(undefined);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit answer');
    } finally {
      setIsLoading(false);
    }
  };

  const handleHelpRequest = () => handleSubmit('help');

  const handleThemeToggle = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    // TODO: Implement light theme
  };

  // Trigger report generation
  const triggerReportGeneration = async () => {
    if (!sessionId) return;

    try {
      setIsGeneratingReport(true);
      
      // Start report generation
      await generateReport(sessionId);
      
      // Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const status = await getReportStatus(sessionId);
          setReportStatus(status);
          
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            setGeneratedReport(status.report);
            setIsGeneratingReport(false);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setIsGeneratingReport(false);
            setError(status.message || 'Failed to generate report');
          }
        } catch (err) {
          console.error('Error polling report status:', err);
        }
      }, 2000); // Poll every 2 seconds
      
      // Cleanup on unmount
      return () => clearInterval(pollInterval);
    } catch (err) {
      setIsGeneratingReport(false);
      setError(err instanceof Error ? err.message : 'Failed to generate report');
    }
  };

  // Build stepper steps
  const steps = PARAMETER_ORDER.map((param, index) => {
    const stepNum = index + 1;
    let status: 'completed' | 'current' | 'pending' = 'pending';
    
    if (stepNum < stepNumber) {
      status = 'completed';
    } else if (stepNum === stepNumber) {
      status = 'current';
    }

    return {
      number: stepNum,
      label: PARAMETER_LABELS[param]?.[language] || param,
      status,
    };
  });

  // Loading state
  if (isLoading && !sessionId) {
    return (
      <div className="min-h-screen bg-agrovers-bg-primary flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-agrovers-accent-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-agrovers-text-secondary">
            {language === 'hi' ? 'लोड हो रहा है...' : 'Loading...'}
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-agrovers-bg-primary flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-agrovers-bg-secondary border border-agrovers-accent-error/30 rounded-2xl p-6 text-center">
          <div className="w-16 h-16 bg-agrovers-accent-error/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-3xl">❌</span>
          </div>
          <h2 className="text-xl font-semibold text-agrovers-text-primary mb-2">
            {language === 'hi' ? 'त्रुटि' : 'Error'}
          </h2>
          <p className="text-agrovers-text-secondary mb-6">{error}</p>
          <button
            onClick={onReset}
            className="px-6 py-3 bg-agrovers-accent-primary hover:bg-agrovers-accent-primary/90 text-white rounded-xl font-medium transition-colors"
          >
            {language === 'hi' ? 'वापस जाएं' : 'Go Back'}
          </button>
        </div>
      </div>
    );
  }

  // Complete state - Show report
  if (isComplete) {
    // Show loading screen while generating report
    if (isGeneratingReport && reportStatus) {
      return (
        <ReportLoadingScreen
          progress={reportStatus.progress}
          message={reportStatus.message}
          status={reportStatus.status}
        />
      );
    }

    // Show generated report
    if (generatedReport) {
      // Check if it's the comprehensive format (with soilAnalysis)
      const isComprehensive = generatedReport.soilAnalysis && generatedReport.cropRecommendations;
      
      return (
        <div className="min-h-screen bg-agrovers-bg-primary py-12 px-4">
          <div className="max-w-6xl mx-auto">
            {isComprehensive ? (
              <ComprehensiveSoilReport report={generatedReport} />
            ) : (
              <SoilReportDisplay report={generatedReport} />
            )}
            
            <div className="text-center mt-8">
              <button
                onClick={onReset}
                className="px-8 py-4 bg-agrovers-accent-primary hover:bg-agrovers-accent-primary/90 text-white rounded-xl text-lg font-semibold transition-all hover:scale-105 active:scale-95"
              >
                {language === 'hi' ? 'नया टेस्ट शुरू करें' : 'Start New Test'}
              </button>
            </div>
          </div>
        </div>
      );
    }

    // Fallback to summary page if report generation failed
    return (
      <div className="min-h-screen bg-agrovers-bg-primary py-12">
        <SummaryPage answers={answers} language={language} isComplete={true} />

        <div className="text-center mt-6">
          <button
            onClick={onReset}
            className="px-8 py-4 bg-agrovers-accent-primary hover:bg-agrovers-accent-primary/90 text-white rounded-xl text-lg font-semibold transition-all hover:scale-105 active:scale-95"
          >
            {language === 'hi' ? 'नया टेस्ट शुरू करें' : 'Start New Test'}
          </button>
        </div>
      </div>
    );
  }

  // Main wizard UI
  return (
    <MainLayout
      language={language}
      theme={theme}
      onThemeToggle={handleThemeToggle}
      onReset={onReset}
      sidebar={
        <div>
          <h2 className="text-sm font-semibold text-agrovers-text-secondary uppercase tracking-wider mb-4">
            {language === 'hi' ? 'विश्लेषण प्रगति' : 'Analysis Progress'}
          </h2>
          <ProgressStepper steps={steps} />
        </div>
      }
    >
      <NewChatInterface
        parameter={currentParameter}
        question={currentQuestion}
        language={language}
        helperText={helperText}
        audioUrl={audioUrl}
        onSubmit={handleSubmit}
        onHelpRequest={handleHelpRequest}
        isSubmitting={isLoading}
        stepNumber={stepNumber}
        lastAnswer={lastAnswer}
      />
    </MainLayout>
  );
}
