import { cn } from '../../lib/utils';

interface AISpeakingIndicatorProps {
  language?: 'en' | 'hi';
  className?: string;
}

export function AISpeakingIndicator({
  language = 'en',
  className
}: AISpeakingIndicatorProps) {
  const text = language === 'hi' ? 'AI बोल रहा है...' : 'AI Speaking';

  return (
    <div className={cn(
      "flex items-center gap-3 px-4 py-2 rounded-full",
      "bg-agrovers-accent-primary/10 border border-agrovers-accent-primary/30",
      className
    )}>
      {/* Waveform Animation */}
      <div className="flex items-center gap-1">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-1 bg-agrovers-accent-primary rounded-full animate-pulse"
            style={{
              height: '16px',
              animationDelay: `${i * 0.15}s`,
              animationDuration: '1s'
            }}
          />
        ))}
      </div>

      {/* Text */}
      <span className="text-sm font-medium text-agrovers-accent-primary">
        {text}
      </span>
    </div>
  );
}
