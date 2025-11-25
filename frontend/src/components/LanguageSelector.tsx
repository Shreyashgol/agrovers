/**
 * Language Selection Component
 * 
 * First screen – choose Hindi or English.
 */

import { Language } from '../api/client';

interface LanguageSelectorProps {
  onSelect: (language: Language) => void;
}

export default function LanguageSelector({ onSelect }: LanguageSelectorProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-900 via-slate-900 to-slate-950 text-white px-4">
      <div className="w-full max-w-md bg-slate-900/80 border border-emerald-500/40 rounded-3xl shadow-2xl p-6 sm:p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="mx-auto w-12 h-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center text-2xl">
            🌾
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold">
            Agrovers Soil Assistant
          </h1>
          <p className="text-sm text-emerald-200">
            मिट्टी परीक्षण सहायक – simple guidance for your farm
          </p>
        </div>

        <p className="text-center text-sm text-slate-200">
          Please select your preferred language <br />
          <span className="text-emerald-300">
            / कृपया अपनी भाषा चुनें
          </span>
        </p>

        <div className="space-y-3">
          <button
            onClick={() => onSelect('en')}
            className="w-full py-3.5 px-6 rounded-2xl bg-emerald-500 hover:bg-emerald-400
                       text-base sm:text-lg font-semibold shadow-lg shadow-emerald-900/50
                       transition-transform active:scale-95"
          >
            English
          </button>

          <button
            onClick={() => onSelect('hi')}
            className="w-full py-3.5 px-6 rounded-2xl bg-amber-500 hover:bg-amber-400
                       text-base sm:text-lg font-semibold shadow-lg shadow-amber-900/50
                       transition-transform active:scale-95"
          >
            हिंदी (Hindi)
          </button>
        </div>

        <p className="text-[11px] text-center text-slate-400">
          Your answers will generate a{" "}
          <span className="text-emerald-300 font-medium">
            simple soil health report
          </span>{" "}
          for your farm.
        </p>
      </div>
    </div>
  );
}
