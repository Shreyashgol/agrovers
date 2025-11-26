import { Check } from 'lucide-react';
import { cn } from '../../lib/utils';

interface Step {
  number: number;
  label: string;
  status: 'completed' | 'current' | 'pending';
}

interface ProgressStepperProps {
  steps: Step[];
  className?: string;
}

export function ProgressStepper({ steps, className }: ProgressStepperProps) {
  return (
    <div className={cn("space-y-1", className)}>
      {steps.map((step, index) => {
        const isLast = index === steps.length - 1;
        
        return (
          <div key={step.number} className="relative">
            {/* Step Item */}
            <div className="flex items-center gap-3 py-2">
              {/* Circle */}
              <div className={cn(
                "relative z-10 flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-200",
                step.status === 'completed' && "bg-agrovers-accent-primary text-white",
                step.status === 'current' && "bg-agrovers-accent-primary text-white ring-4 ring-agrovers-accent-primary/20",
                step.status === 'pending' && "bg-agrovers-bg-elevated text-agrovers-text-muted border border-agrovers-border-subtle"
              )}>
                {step.status === 'completed' ? (
                  <Check className="w-4 h-4" />
                ) : (
                  step.number
                )}
              </div>

              {/* Label */}
              <span className={cn(
                "text-sm transition-colors duration-200",
                step.status === 'current' && "text-agrovers-text-primary font-medium",
                step.status === 'completed' && "text-agrovers-text-secondary",
                step.status === 'pending' && "text-agrovers-text-muted"
              )}>
                {step.label}
              </span>
            </div>

            {/* Connecting Line */}
            {!isLast && (
              <div className="absolute left-4 top-10 w-0.5 h-6 -translate-x-1/2">
                <div className={cn(
                  "w-full h-full transition-colors duration-200",
                  step.status === 'completed' ? "bg-agrovers-accent-primary" : "bg-agrovers-border-subtle"
                )} />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
