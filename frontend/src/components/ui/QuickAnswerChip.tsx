import { cn } from '../../lib/utils';

interface QuickAnswerChipProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  className?: string;
}

export function QuickAnswerChip({
  label,
  onClick,
  disabled = false,
  className
}: QuickAnswerChipProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
        "bg-agrovers-bg-elevated text-agrovers-text-primary",
        "hover:bg-agrovers-bg-tertiary hover:scale-105",
        "active:scale-95",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
        "border border-agrovers-border-subtle hover:border-agrovers-accent-primary/30",
        className
      )}
    >
      {label}
    </button>
  );
}
