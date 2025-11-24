/**
 * Summary Page Component
 * 
 * Displays all collected soil test parameters before final submission.
 * Shows confirmation message after data is sent to n8n.
 */

import { SoilTestResult, Language } from '../api/client';

interface SummaryPageProps {
  answers: SoilTestResult;
  language: Language;
  isComplete: boolean;
}

const FIELD_LABELS: Record<string, Record<Language, string>> = {
  color: { en: 'Color', hi: 'रंग' },
  moisture: { en: 'Moisture', hi: 'नमी' },
  smell: { en: 'Smell', hi: 'गंध' },
  ph_category: { en: 'pH Category', hi: 'pH श्रेणी' },
  ph_value: { en: 'pH Value', hi: 'pH मान' },
  soil_type: { en: 'Soil Type', hi: 'मिट्टी का प्रकार' },
  earthworms: { en: 'Earthworms', hi: 'केंचुए' },
  location: { en: 'Location', hi: 'स्थान' },
  fertilizer_used: { en: 'Fertilizer Used', hi: 'उपयोग की गई खाद' },
};

export default function SummaryPage({
  answers,
  language,
  isComplete,
}: SummaryPageProps) {
  const fields = [
    'color',
    'moisture',
    'smell',
    'ph_category',
    'ph_value',
    'soil_type',
    'earthworms',
    'location',
    'fertilizer_used',
  ] as const;
  
  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold text-center mb-6 text-gray-800">
          {language === 'hi' ? 'सारांश' : 'Summary'}
        </h2>
        
        {isComplete && (
          <div className="mb-6 p-4 bg-green-100 border-l-4 border-green-500 rounded-lg">
            <p className="text-green-800 font-semibold">
              {language === 'hi'
                ? '✅ डेटा सफलतापूर्वक भेजा गया। सिफारिशें संसाधित की जाएंगी।'
                : '✅ Data sent successfully. Recommendations will be processed.'}
            </p>
          </div>
        )}
        
        <div className="space-y-4">
          {fields.map((field) => {
            const value = answers[field as keyof SoilTestResult];
            if (value === null || value === undefined) return null;
            
            const label = FIELD_LABELS[field]?.[language] || field;
            
            return (
              <div
                key={field}
                className="flex justify-between items-center py-3 border-b border-gray-200"
              >
                <span className="font-semibold text-gray-700">{label}:</span>
                <span className="text-gray-900">{String(value)}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

