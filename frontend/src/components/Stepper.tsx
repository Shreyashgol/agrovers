/**
 * Stepper Component
 * 
 * Shows progress through the wizard steps.
 * Displays "Step X of Y" with parameter name.
 */

import { PARAMETER_ORDER } from '../config/labels';
import { Language } from '../api/client';

interface StepperProps {
  currentStep: number;
  totalSteps: number;
  currentParameter: string;
  language: Language;
}

const PARAMETER_NAMES: Record<string, Record<Language, string>> = {
  color: { en: 'Color', hi: 'रंग' },
  moisture: { en: 'Moisture', hi: 'नमी' },
  smell: { en: 'Smell', hi: 'गंध' },
  ph: { en: 'pH', hi: 'pH' },
  soil_type: { en: 'Soil Type', hi: 'मिट्टी का प्रकार' },
  earthworms: { en: 'Earthworms', hi: 'केंचुए' },
  location: { en: 'Location', hi: 'स्थान' },
  fertilizer_used: { en: 'Fertilizer', hi: 'खाद' },
};

export default function Stepper({
  currentStep,
  totalSteps,
  currentParameter,
  language,
}: StepperProps) {
  const parameterName = PARAMETER_NAMES[currentParameter]?.[language] || currentParameter;
  
  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-gray-600">
          {language === 'hi' ? 'चरण' : 'Step'} {currentStep} {language === 'hi' ? 'का' : 'of'} {totalSteps}
        </span>
        <span className="text-sm font-semibold text-gray-800">
          {parameterName}
        </span>
      </div>
      
      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
          style={{ width: `${(currentStep / totalSteps) * 100}%` }}
        />
      </div>
    </div>
  );
}

