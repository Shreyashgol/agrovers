/**
 * Root React component
 */

import { useState } from 'react';
import { Language } from './api/client';
import LanguageSelector from './components/LanguageSelector';
import NewSoilWizard from './pages/NewSoilWizard';

function App() {
  const [language, setLanguage] = useState<Language | null>(null);

  const handleLanguageSelect = (lang: Language) => {
    setLanguage(lang);
  };

  const handleReset = () => {
    setLanguage(null);
  };

  if (!language) {
    return <LanguageSelector onSelect={handleLanguageSelect} />;
  }

  return <NewSoilWizard language={language} onReset={handleReset} />;
}

export default App;
