import { X, Lightbulb } from 'lucide-react';
import { cn } from '../../lib/utils';

interface HelperPanelProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  content: string;
  language?: 'en' | 'hi';
  className?: string;
}

export function HelperPanel({
  isOpen,
  onClose,
  title,
  content,
  language = 'en',
  className
}: HelperPanelProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 z-40 animate-fade-in"
        onClick={onClose}
      />

      {/* Panel */}
      <div className={cn(
        "fixed bottom-0 left-0 right-0 z-50",
        "bg-agrovers-bg-secondary border-t-2 border-agrovers-accent-warning",
        "rounded-t-3xl shadow-2xl",
        "animate-slide-up",
        "max-h-[70vh] overflow-y-auto custom-scrollbar",
        className
      )}>
        {/* Header */}
        <div className="sticky top-0 bg-agrovers-bg-secondary border-b border-agrovers-accent-warning/30 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-agrovers-accent-warning/20 flex items-center justify-center">
              <Lightbulb className="w-5 h-5 text-agrovers-accent-warning" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-agrovers-text-primary">
                {title}
              </h3>
              <p className="text-xs text-agrovers-text-muted">
                {language === 'hi' ? 'मदद और मार्गदर्शन' : 'Help & Guidance'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-agrovers-bg-elevated hover:bg-agrovers-bg-tertiary flex items-center justify-center transition-colors"
          >
            <X className="w-5 h-5 text-agrovers-text-secondary" />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-6">
          <div className="bg-agrovers-accent-warning/10 border border-agrovers-accent-warning/30 rounded-xl p-4">
            <p className="text-agrovers-text-primary leading-relaxed whitespace-pre-wrap">
              {content}
            </p>
          </div>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="mt-6 w-full py-3 rounded-xl bg-agrovers-accent-primary hover:bg-agrovers-accent-primary/90 text-white font-medium transition-colors"
          >
            {language === 'hi' ? 'समझ गया' : 'Got it'}
          </button>
        </div>
      </div>
    </>
  );
}
