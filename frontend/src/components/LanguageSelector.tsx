/**
 * Language Selection Component
 * 
 * Allows user to select Hindi or English before starting the wizard.
 */

import { Language } from '../api/client';

interface LanguageSelectorProps {
  onSelect: (language: Language) => void;
}

export default function LanguageSelector({ onSelect }: LanguageSelectorProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-2 text-gray-800">
          Argovers Soil Assistant
        </h1>
        <p className="text-center text-gray-600 mb-8">
          मिट्टी परीक्षण सहायक
        </p>
        
        <p className="text-center text-gray-700 mb-6">
          Please select your preferred language / कृपया अपनी भाषा चुनें
        </p>
        
        <div className="space-y-4">
          <button
            onClick={() => onSelect('en')}
            className="w-full py-4 px-6 bg-blue-600 text-white rounded-lg text-lg font-semibold hover:bg-blue-700 transition-colors shadow-md"
          >
            English
          </button>
          
          <button
            onClick={() => onSelect('hi')}
            className="w-full py-4 px-6 bg-green-600 text-white rounded-lg text-lg font-semibold hover:bg-green-700 transition-colors shadow-md"
          >
            हिंदी (Hindi)
          </button>
        </div>
      </div>
    </div>
  );
}

