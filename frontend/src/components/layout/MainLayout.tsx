import { ReactNode } from 'react';
import { Sun, Moon, Globe } from 'lucide-react';
import { cn } from '../../lib/utils';

interface MainLayoutProps {
  sidebar: ReactNode;
  children: ReactNode;
  language: 'en' | 'hi';
  theme?: 'dark' | 'light';
  onThemeToggle?: () => void;
  onReset?: () => void;
  className?: string;
}

export function MainLayout({
  sidebar,
  children,
  language,
  theme = 'dark',
  onThemeToggle,
  onReset,
  className
}: MainLayoutProps) {
  return (
    <div className={cn(
      "min-h-screen bg-agrovers-bg-primary flex flex-col",
      className
    )}>
      {/* Header */}
      <header className="border-b border-agrovers-border-subtle bg-agrovers-bg-secondary">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-agrovers-accent-primary flex items-center justify-center">
              <span className="text-white font-bold text-lg">A</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-agrovers-text-primary">
                AGROVERS
              </h1>
              <p className="text-xs text-agrovers-text-secondary">
                {language === 'hi' ? 'मिट्टी सहायक' : 'Soil Assistant'}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            {/* Language Indicator */}
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-agrovers-bg-elevated">
              <Globe className="w-4 h-4 text-agrovers-text-secondary" />
              <span className="text-sm font-medium text-agrovers-text-primary uppercase">
                {language}
              </span>
            </div>

            {/* Theme Toggle */}
            {onThemeToggle && (
              <button
                onClick={onThemeToggle}
                className="w-10 h-10 rounded-lg bg-agrovers-bg-elevated hover:bg-agrovers-bg-tertiary flex items-center justify-center transition-colors"
                title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {theme === 'dark' ? (
                  <Sun className="w-5 h-5 text-agrovers-text-secondary" />
                ) : (
                  <Moon className="w-5 h-5 text-agrovers-text-secondary" />
                )}
              </button>
            )}

            {/* Reset Button */}
            {onReset && (
              <button
                onClick={onReset}
                className="px-4 py-2 rounded-lg bg-agrovers-bg-elevated hover:bg-agrovers-bg-tertiary text-sm font-medium text-agrovers-text-primary transition-colors"
              >
                {language === 'hi' ? 'रीसेट' : 'Reset'}
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Fixed/Sticky */}
        <aside className="w-64 border-r border-agrovers-border-subtle bg-agrovers-bg-secondary flex-shrink-0">
          <div className="h-full overflow-y-auto custom-scrollbar p-6">
            {sidebar}
          </div>
        </aside>

        {/* Main Area - Scrollable */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  );
}
