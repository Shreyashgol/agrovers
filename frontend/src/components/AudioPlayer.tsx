/**
 * Audio Player Component
 * 
 * Plays TTS audio responses from the backend
 */

import { useEffect, useRef, useState } from 'react';

interface AudioPlayerProps {
  audioUrl: string;
  autoPlay?: boolean;
  onEnded?: () => void;
}

export function AudioPlayer({ audioUrl, autoPlay = true, onEnded }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (audioRef.current && autoPlay) {
      audioRef.current.play().catch((err) => {
        console.error('Audio playback error:', err);
        setError(true);
      });
    }
  }, [audioUrl, autoPlay]);

  const handlePlay = () => {
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handleEnded = () => {
    setIsPlaying(false);
    onEnded?.();
  };

  const handleError = () => {
    setError(true);
    setIsPlaying(false);
  };

  if (error) {
    return (
      <div className="text-sm text-red-600">
        ⚠️ Could not play audio
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 p-2 bg-blue-50 rounded">
      <audio
        ref={audioRef}
        src={audioUrl}
        onPlay={handlePlay}
        onPause={handlePause}
        onEnded={handleEnded}
        onError={handleError}
        controls
        className="w-full"
      />
      {isPlaying && (
        <span className="text-sm text-blue-600">🔊 Playing...</span>
      )}
    </div>
  );
}
