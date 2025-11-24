/**
 * Frontend labels and options for each parameter.
 * 
 * To modify parameter list or labels:
 *   Update the LABELS object below
 *   Ensure parameter names match backend PARAMETER_ORDER
 */

import { Language } from '../api/client';

export interface ParameterLabels {
  question: string;
  options: string[];
  placeholder: string;
  helpButton: string;
}

export const LABELS: Record<string, Record<Language, ParameterLabels>> = {
  color: {
    en: {
      question: 'What is the color of your soil?',
      options: ['Black', 'Red', 'Brown', 'Yellow', 'Grey'],
      placeholder: 'Enter soil color...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपकी मिट्टी का रंग क्या है?',
      options: ['काली', 'लाल', 'भूरा', 'पीला', 'सुराही'],
      placeholder: 'मिट्टी का रंग दर्ज करें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  moisture: {
    en: {
      question: 'What is the moisture level of your soil?',
      options: ['Dry', 'Moist', 'Wet', 'Very Dry'],
      placeholder: 'Enter moisture level...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपकी मिट्टी में नमी का स्तर क्या है?',
      options: ['सूखी', 'नम', 'गीली', 'बहुत सूखी'],
      placeholder: 'नमी का स्तर दर्ज करें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  smell: {
    en: {
      question: 'What does your soil smell like?',
      options: ['Sweet', 'Earthy', 'Sour', 'Rotten', 'No Smell'],
      placeholder: 'Describe the smell...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपकी मिट्टी से कैसी गंध आती है?',
      options: ['मीठी', 'मिट्टी', 'खट्टी', 'सड़ी', 'कोई गंध नहीं'],
      placeholder: 'गंध का वर्णन करें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  ph: {
    en: {
      question: 'What is the pH level of your soil?',
      options: ['Acidic', 'Neutral', 'Alkaline'],
      placeholder: 'Enter pH value (e.g., 6.5) or category...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपकी मिट्टी का pH स्तर क्या है?',
      options: ['अम्लीय', 'तटस्थ', 'क्षारीय'],
      placeholder: 'pH मान दर्ज करें (जैसे, 6.5) या श्रेणी...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  soil_type: {
    en: {
      question: 'What type of soil do you have?',
      options: ['Clay', 'Sandy', 'Loamy', 'Silt'],
      placeholder: 'Enter soil type...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपकी मिट्टी किस प्रकार की है?',
      options: ['चिकनी', 'रेतिली', 'दोमट', 'मिट्टी'],
      placeholder: 'मिट्टी का प्रकार दर्ज करें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  earthworms: {
    en: {
      question: 'Are there earthworms in your soil?',
      options: ['Yes', 'No', 'Many', 'Few'],
      placeholder: 'Enter earthworm presence...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'क्या आपकी मिट्टी में केंचुए हैं?',
      options: ['हाँ', 'नहीं', 'बहुत', 'कम'],
      placeholder: 'केंचुए की उपस्थिति दर्ज करें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  location: {
    en: {
      question: 'Where is your farm located? (village, district, state)',
      options: [],
      placeholder: 'Enter location (e.g., Village, District, State)...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपका खेत कहाँ स्थित है? (गाँव, जिला, राज्य)',
      options: [],
      placeholder: 'स्थान दर्ज करें (जैसे, गाँव, जिला, राज्य)...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  fertilizer_used: {
    en: {
      question: 'What fertilizers have you used recently?',
      options: ['Yes', 'No'],
      placeholder: 'Enter fertilizer name or Yes/No...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपने हाल ही में कौन सी खाद का उपयोग किया है?',
      options: ['हाँ', 'नहीं'],
      placeholder: 'खाद का नाम दर्ज करें या हाँ/नहीं...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
};

export const PARAMETER_ORDER = [
  'color',
  'moisture',
  'smell',
  'ph',
  'soil_type',
  'earthworms',
  'location',
  'fertilizer_used',
];

