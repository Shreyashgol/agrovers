/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ["class"],
  theme: {
    extend: {
      colors: {
        // Custom Agrovers color palette from mockup
        agrovers: {
          bg: {
            primary: '#0A1628',
            secondary: '#0F1F35',
            tertiary: '#1A2942',
            elevated: '#1E293B',
          },
          accent: {
            primary: '#10B981',
            teal: '#14B8A6',
            warning: '#F59E0B',
            error: '#EF4444',
          },
          text: {
            primary: '#F8FAFC',
            secondary: '#94A3B8',
            muted: '#64748B',
          },
          border: {
            subtle: '#1E293B',
            accent: '#10B981',
          }
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}

