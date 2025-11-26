import { Play } from 'lucide-react';
import { cn } from '../../lib/utils';

interface UserMessageBubbleProps {
  message: string;
  timestamp?: string;
  isVoice?: boolean;
  duration?: string;
  className?: string;
}

export function UserMessageBubble({
  message,
  timestamp,
  isVoice = false,
  duration,
  className
}: UserMessageBubbleProps) {
  return (
    <div className={cn("flex items-end justify-end gap-2 animate-fade-in", className)}>
      <div className="flex flex-col items-end max-w-[85%]">
        {/* Timestamp */}
        {timestamp && (
          <span className="text-xs text-agrovers-text-muted mb-1">
            {timestamp}
          </span>
        )}

        {/* Message Bubble */}
        <div className={cn(
          "rounded-2xl px-4 py-3 shadow-lg",
          isVoice 
            ? "bg-agrovers-accent-primary" 
            : "bg-agrovers-accent-primary"
        )}>
          {isVoice ? (
            <div className="space-y-2">
              {/* Waveform with play button */}
              <div className="flex items-center gap-3">
                {/* Play Button */}
                <button className="flex-shrink-0 w-8 h-8 rounded-full bg-white/20 flex items-center justify-center hover:bg-white/30 transition-colors">
                  <Play className="w-4 h-4 text-white fill-white" />
                </button>

                {/* Waveform */}
                <div className="flex items-center gap-1 flex-1">
                  {[3, 5, 4, 6, 3, 5, 4, 3, 5, 4].map((height, i) => (
                    <div
                      key={i}
                      className="w-1 bg-white/60 rounded-full"
                      style={{ height: `${height * 3}px` }}
                    />
                  ))}
                </div>

                {/* Duration */}
                {duration && (
                  <span className="text-xs text-white/80 font-medium">
                    {duration}
                  </span>
                )}
              </div>
              
              {/* Transcribed text */}
              {message && !message.includes('Processing') && !message.includes('प्रोसेसिंग') && (
                <p className="text-white/90 text-sm leading-relaxed border-t border-white/10 pt-2">
                  "{message}"
                </p>
              )}
            </div>
          ) : (
            <p className="text-white leading-relaxed">
              {message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
