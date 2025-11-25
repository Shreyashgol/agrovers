/**
 * Frontend labels and options for each parameter.
 * 
 * Make sure parameter keys match backend PARAMETER_ORDER.
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
      options: ['काली', 'लाल', 'भूरी', 'पीली', 'स्लेटी'],
      placeholder: 'मिट्टी का रंग लिखें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  moisture: {
    en: {
      question: 'How much moisture is in your soil?',
      options: ['Dry', 'Moist', 'Wet', 'Very Dry'],
      placeholder: 'Enter moisture level...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपकी मिट्टी में नमी कितनी है?',
      options: ['सूखी', 'थोड़ी नम', 'बहुत गीली', 'बहुत सूखी'],
      placeholder: 'नमी का स्तर लिखें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  smell: {
    en: {
      question: 'What does your soil smell like?',
      options: ['Earthy', 'Sweet', 'Sour', 'Rotten', 'No Smell'],
      placeholder: 'Describe the smell...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपकी मिट्टी से कैसी गंध आती है?',
      options: ['मिट्टी जैसी', 'थोड़ी मीठी', 'खट्टी', 'सड़ी हुई', 'कोई गंध नहीं'],
      placeholder: 'गंध का वर्णन करें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  ph: {
    en: {
      question: 'What is the pH of your soil?',
      options: ['Acidic', 'Neutral', 'Alkaline'],
      placeholder: 'Enter pH value (e.g., 6.5) or category...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपकी मिट्टी का pH क्या है?',
      options: ['अम्लीय', 'तटस्थ', 'क्षारीय'],
      placeholder: 'pH मान (जैसे 6.5) या श्रेणी लिखें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  soil_type: {
    en: {
      question: 'What type of soil do you have?',
      options: ['Clay', 'Sandy', 'Loamy', 'Silty'],
      placeholder: 'Enter soil type...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपकी मिट्टी किस प्रकार की है?',
      options: ['चिकनी (clay)', 'रेतिली (sandy)', 'दोमट (loamy)', 'गादयुक्त (silty)'],
      placeholder: 'मिट्टी का प्रकार लिखें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  earthworms: {
    en: {
      question: 'Do you see earthworms in your soil?',
      options: ['Many', 'Few', 'None'],
      placeholder: 'Write about earthworms...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'क्या मिट्टी में केंचुए दिखते हैं?',
      options: ['बहुत', 'थोड़े', 'नहीं'],
      placeholder: 'केंचुओं के बारे में लिखें...',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  location: {
    en: {
      question: 'Where is your farm? (village, district, state)',
      options: [],
      placeholder: 'Example: Village, District, State',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपका खेत कहाँ है? (गाँव, जिला, राज्य)',
      options: [],
      placeholder: 'जैसे: गाँव, जिला, राज्य',
      helpButton: 'मुझे नहीं पता / मदद चाहिए',
    },
  },
  fertilizer_used: {
    en: {
      question: 'Which fertilizers have you used recently?',
      options: ['Urea', 'DAP', 'NPK', 'Organic / Vermicompost', 'None'],
      placeholder: 'Write fertilizer names or say None...',
      helpButton: "I don't know / Need help",
    },
    hi: {
      question: 'आपने हाल में कौन सी खाद / उर्वरक डाली है?',
      options: ['यूरिया', 'डीएपी', 'एनपीके', 'जैविक / वर्मी कम्पोस्ट', 'कुछ नहीं'],
      placeholder: 'खाद का नाम लिखें या लिखें – कुछ नहीं',
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
