/**
 * Help Panel Component
 * 
 * Shows explanation on how to measure the current parameter.
 */

interface HelpPanelProps {
  helperText: string;
  onClose?: () => void;
}

export default function HelpPanel({ helperText, onClose }: HelpPanelProps) {
  if (!helperText) return null;

  return (
    <div className="mt-6 p-4 sm:p-5 bg-sky-50 border border-sky-200 rounded-2xl">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">💡</span>
          <h3 className="text-sm sm:text-base font-semibold text-sky-900">
            Help / मदद
          </h3>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-sky-500 hover:text-sky-700 text-sm"
          >
            ✕
          </button>
        )}
      </div>
      <p className="text-xs sm:text-sm text-sky-900 whitespace-pre-wrap leading-relaxed">
        {helperText}
      </p>
    </div>
  );
}
