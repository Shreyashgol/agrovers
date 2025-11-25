// src/components/AudioPlayer.tsx
import React, { useEffect, useRef, useState } from "react";

interface AudioPlayerProps {
  audioUrl: string;
  autoPlay?: boolean;
  onEnded?: () => void;
}

export function AudioPlayer({ audioUrl, autoPlay = false, onEnded }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (audioRef.current && autoPlay) {
      audioRef.current.play().catch(() => {});
    }
  }, [audioUrl, autoPlay]);

  return (
    <div className="p-3 bg-white/90 rounded-lg shadow-sm">
      <audio
        controls
        ref={audioRef}
        src={audioUrl}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => {
          setIsPlaying(false);
          onEnded?.();
        }}
        className="w-full"
      />
      {isPlaying && <div className="text-xs text-neutral-600 mt-1">🔊 Playing</div>}
    </div>
  );
}
