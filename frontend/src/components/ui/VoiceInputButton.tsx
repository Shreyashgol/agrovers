import { Mic } from 'lucide-react';
import { cn } from '../../lib/utils';

interface VoiceInputButtonProps {
  isRecording: boolean;
  isAISpeaking: boolean;
  onClick: () => void;
  disabled?: boolean;
  size?: 'default' | 'large';
  className?: string;
}

export function VoiceInputButton({
  isRecording,
  isAISpeaking,
  onClick,
  disabled = false,
  size = 'default',
  className
}: VoiceInputButtonProps) {
  const sizeClasses = {
    default: 'w-12 h-12',
    large: 'w-16 h-16'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "rounded-full flex items-center justify-center transition-all duration-200",
        "shadow-lg hover:shadow-xl",
        sizeClasses[size],
        isRecording 
          ? "bg-agrovers-accent-error animate-pulse ring-4 ring-agrovers-accent-error/30" 
          : isAISpeaking
          ? "bg-agrovers-accent-primary animate-pulse-slow ring-4 ring-agrovers-accent-primary/30"
          : "bg-agrovers-accent-primary hover:bg-agrovers-accent-primary/90 hover:scale-110 active:scale-95",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
        className
      )}
    >
      <Mic className={cn(
        "text-white",
        size === 'large' ? 'w-7 h-7' : 'w-5 h-5'
      )} />
    </button>
  );
}
