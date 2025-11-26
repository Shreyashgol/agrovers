import { Check } from 'lucide-react';
import { cn } from '../../lib/utils';

interface StepCompletionCardProps {
  stepNumber: number;
  parameter: string;
  value: string;
  displayValue?: string;
  colorSwatch?: string;
  className?: string;
}

export function StepCompletionCard({
  stepNumber,
  parameter,
  value,
  displayValue,
  colorSwatch,
  className
}: StepCompletionCardProps) {
  return (
    <div className={cn(
      "bg-agrovers-bg-tertiary border border-agrovers-border-subtle rounded-xl p-4 animate-slide-up",
      className
    )}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-agrovers-text-secondary uppercase tracking-wider">
          Step {stepNumber} Complete
        </span>
        <div className="flex items-center gap-1 text-agrovers-accent-primary">
          <Check className="w-4 h-4" />
          <span className="text-xs font-medium">Saved</span>
        </div>
      </div>

      {/* Content */}
      <div className="flex items-center gap-3">
        {/* Color Swatch (if applicable) */}
        {colorSwatch && (
          <div 
            className="w-12 h-12 rounded-lg border-2 border-agrovers-border-subtle flex-shrink-0"
            style={{ backgroundColor: colorSwatch }}
          />
        )}

        {/* Value */}
        <div className="flex-1">
          <p className="text-sm text-agrovers-text-secondary capitalize mb-1">
            {parameter}
          </p>
          <p className="text-base font-semibold text-agrovers-text-primary">
            {displayValue || value}
          </p>
        </div>
      </div>
    </div>
  );
}
