import { Bot } from 'lucide-react';
import { cn } from '../../lib/utils';

interface AIAssistantCardProps {
  message: string;
  timestamp?: string;
  isHelper?: boolean;
  children?: React.ReactNode;
  className?: string;
}

// Helper function to parse and format text with steps
function formatMessage(text: string): React.ReactNode {
  // Split by newlines and format
  const lines = text.split('\n');
  
  return lines.map((line, index) => {
    // Check if line is a step (starts with number or "कदम")
    const isStep = /^(\d+\.|कदम \d+:|Step \d+:)/.test(line.trim());
    
    if (isStep) {
      return (
        <div key={index} className="flex gap-2 mb-2">
          <span className="text-agrovers-accent-primary font-semibold flex-shrink-0">
            {line.match(/^(\d+\.|कदम \d+:|Step \d+:)/)?.[0]}
          </span>
          <span className="flex-1">
            {line.replace(/^(\d+\.|कदम \d+:|Step \d+:)\s*/, '')}
          </span>
        </div>
      );
    }
    
    // Regular line
    return line.trim() ? (
      <p key={index} className="mb-2 last:mb-0">
        {line}
      </p>
    ) : (
      <br key={index} />
    );
  });
}

export function AIAssistantCard({
  message,
  timestamp,
  isHelper = false,
  children,
  className
}: AIAssistantCardProps) {
  return (
    <div className={cn("flex items-start gap-3 animate-fade-in", className)}>
      {/* AI Icon */}
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-agrovers-accent-teal/20 flex items-center justify-center ring-2 ring-agrovers-accent-teal/30">
        <Bot className="w-5 h-5 text-agrovers-accent-teal" />
      </div>

      {/* Card Content */}
      <div className="flex-1 max-w-[85%]">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium text-agrovers-accent-teal">
            AI Assistant
          </span>
          {timestamp && (
            <span className="text-xs text-agrovers-text-muted">
              {timestamp}
            </span>
          )}
          {isHelper && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-agrovers-accent-warning/20 text-agrovers-accent-warning border border-agrovers-accent-warning/30">
              Help Guide
            </span>
          )}
        </div>

        {/* Main Card */}
        <div className={cn(
          "rounded-2xl p-4 shadow-lg",
          isHelper 
            ? "bg-agrovers-bg-tertiary border-2 border-agrovers-accent-warning/30" 
            : "bg-agrovers-bg-secondary border border-agrovers-border-subtle"
        )}>
          <div className="text-agrovers-text-primary leading-relaxed">
            {formatMessage(message)}
          </div>

          {/* Additional Content (charts, buttons, etc.) */}
          {children && (
            <div className="mt-4">
              {children}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
