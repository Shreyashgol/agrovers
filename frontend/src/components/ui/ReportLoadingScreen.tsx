import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle2, Sprout, FlaskConical, TrendingUp } from 'lucide-react';

interface ReportLoadingScreenProps {
  progress: number;
  message: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

const loadingSteps = [
  { threshold: 10, icon: Sprout, label: 'Preparing soil data', color: 'text-green-400' },
  { threshold: 30, icon: FlaskConical, label: 'Analyzing parameters', color: 'text-blue-400' },
  { threshold: 50, icon: TrendingUp, label: 'Generating recommendations', color: 'text-purple-400' },
  { threshold: 100, icon: CheckCircle2, label: 'Report ready', color: 'text-emerald-400' },
];

export const ReportLoadingScreen: React.FC<ReportLoadingScreenProps> = ({
  progress,
  message,
  status,
}) => {
  const [displayProgress, setDisplayProgress] = useState(0);

  useEffect(() => {
    // Smooth progress animation
    const interval = setInterval(() => {
      setDisplayProgress((prev) => {
        if (prev < progress) {
          return Math.min(prev + 2, progress);
        }
        return prev;
      });
    }, 50);

    return () => clearInterval(interval);
  }, [progress]);

  const currentStep = loadingSteps.findIndex((step) => displayProgress < step.threshold);
  const activeStepIndex = currentStep === -1 ? loadingSteps.length - 1 : Math.max(0, currentStep - 1);

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 rounded-2xl shadow-2xl border border-gray-700 p-8 max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full mb-4 animate-pulse">
            <Sprout className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Generating Your Soil Report
          </h2>
          <p className="text-gray-400 text-sm">
            Please wait while we analyze your soil data
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-400">{message}</span>
            <span className="text-sm font-semibold text-green-400">
              {displayProgress}%
            </span>
          </div>
          <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-green-500 via-emerald-500 to-green-600 transition-all duration-500 ease-out relative"
              style={{ width: `${displayProgress}%` }}
            >
              <div className="absolute inset-0 bg-white/20 animate-shimmer" />
            </div>
          </div>
        </div>

        {/* Loading Steps */}
        <div className="space-y-4">
          {loadingSteps.map((step, index) => {
            const StepIcon = step.icon;
            const isCompleted = displayProgress >= step.threshold;
            const isActive = index === activeStepIndex;

            return (
              <div
                key={index}
                className={`flex items-center gap-3 transition-all duration-300 ${
                  isActive ? 'scale-105' : 'scale-100'
                }`}
              >
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 ${
                    isCompleted
                      ? 'bg-green-500/20 border-2 border-green-500'
                      : isActive
                      ? 'bg-blue-500/20 border-2 border-blue-500 animate-pulse'
                      : 'bg-gray-700 border-2 border-gray-600'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                  ) : isActive ? (
                    <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                  ) : (
                    <StepIcon className="w-5 h-5 text-gray-500" />
                  )}
                </div>
                <span
                  className={`text-sm font-medium transition-colors duration-300 ${
                    isCompleted
                      ? 'text-green-400'
                      : isActive
                      ? 'text-white'
                      : 'text-gray-500'
                  }`}
                >
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>

        {/* Status Message */}
        {status === 'failed' && (
          <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p className="text-red-400 text-sm text-center">
              Failed to generate report. Please try again.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
