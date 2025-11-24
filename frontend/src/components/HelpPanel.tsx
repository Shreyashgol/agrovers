/**
 * Help Panel Component
 * 
 * Displays RAG+LLM generated helper text when user needs assistance.
 * Shows explanation on how to measure the current parameter.
 */

interface HelpPanelProps {
  helperText: string;
  onClose?: () => void;
}

export default function HelpPanel({ helperText, onClose }: HelpPanelProps) {
  return (
    <div className="mt-6 p-6 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
      <div className="flex items-start justify-between mb-2">
        <h3 className="text-lg font-semibold text-blue-900">
          💡 Help / मदद
        </h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-blue-600 hover:text-blue-800"
          >
            ✕
          </button>
        )}
      </div>
      <div className="text-gray-800 whitespace-pre-wrap leading-relaxed">
        {helperText}
      </div>
    </div>
  );
}

