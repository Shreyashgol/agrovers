# Argovers Soil Assistant - Frontend

React + TypeScript + Vite frontend for the soil testing assistant wizard.

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure API Base URL

Edit `src/api/client.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000/api/v1';
```

Change this if your backend runs on a different host/port.

### 3. Run Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Root component
│   ├── api/
│   │   └── client.ts         # API client (axios)
│   ├── config/
│   │   └── labels.ts         # Parameter labels and options
│   ├── components/
│   │   ├── LanguageSelector.tsx
│   │   ├── Stepper.tsx
│   │   ├── ParameterStep.tsx
│   │   ├── HelpPanel.tsx
│   │   └── SummaryPage.tsx
│   └── pages/
│       └── SoilWizard.tsx    # Main wizard page
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## Component Overview

### `App.tsx`

Root component that manages:
- Language selection state
- Routing between `LanguageSelector` and `SoilWizard`

### `LanguageSelector`

Initial screen where user selects Hindi or English.

### `SoilWizard`

Main wizard page that:
- Manages session state
- Coordinates API calls
- Renders current step
- Handles completion

### `Stepper`

Progress indicator showing:
- Current step number (e.g., "Step 3 of 8")
- Parameter name
- Progress bar

### `ParameterStep`

Displays:
- Current question
- Option buttons (if available)
- Free-text input
- Submit and Help buttons
- Help panel (when helper mode active)

### `HelpPanel`

Shows RAG+LLM generated explanation when user needs help.

### `SummaryPage`

Displays all collected parameters and confirmation message.

## API Integration

### Flow

1. **Start Session**
   ```typescript
   const response = await startSession('hi');
   // Sets session_id, gets first question
   ```

2. **Submit Answer**
   ```typescript
   const response = await sendNext(sessionId, userMessage);
   // Returns next question OR helper text
   ```

3. **Get State** (optional)
   ```typescript
   const state = await getState(sessionId);
   // Returns current session state
   ```

### Error Handling

The `SoilWizard` component handles:
- Network errors
- Session not found
- API failures

Shows error message and allows reset.

## Customization

### Adding/Modifying Parameters

Edit `src/config/labels.ts`:

```typescript
export const LABELS = {
  color: {
    en: {
      question: 'What is the color?',
      options: ['Black', 'Red', 'Brown'],
      placeholder: 'Enter color...',
      helpButton: "I don't know",
    },
    hi: {
      // Hindi labels
    },
  },
  // Add new parameter
  new_param: {
    // ...
  },
};
```

Also update `PARAMETER_ORDER` array to include new parameter.

### Changing API Base URL

Edit `src/api/client.ts`:

```typescript
const API_BASE_URL = 'https://your-backend.com/api/v1';
```

### Styling

The app uses Tailwind CSS. Modify:
- `tailwind.config.js` for theme customization
- Component files for specific styling
- `src/index.css` for global styles

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### TypeScript

The project uses strict TypeScript. Types are defined in:
- `src/api/client.ts` - API types
- Component props interfaces

### State Management

Currently uses React `useState` hooks. For complex state, consider:
- Context API
- Zustand
- Redux

## Troubleshooting

### API Connection Errors

**Error:** "Failed to fetch"

**Solution:**
1. Ensure backend is running on `http://localhost:8000`
2. Check CORS settings in backend `config.py`
3. Verify API base URL in `src/api/client.ts`

### Build Errors

**Error:** TypeScript compilation errors

**Solution:**
1. Run `npm run lint` to see specific errors
2. Check type definitions match backend models
3. Ensure all imports are correct

## Deployment

### Build Output

After `npm run build`, serve the `dist/` directory with:
- Nginx
- Apache
- Vercel
- Netlify
- Any static file server

### Environment Variables

For production, you may want to set API URL via environment variable:

1. Create `.env.production`:
   ```
   VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
   ```

2. Update `src/api/client.ts`:
   ```typescript
   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
   ```

3. Rebuild:
   ```bash
   npm run build
   ```

## Future Enhancements

- [ ] Loading skeletons
- [ ] Offline support
- [ ] PWA capabilities
- [ ] Analytics integration
- [ ] Multi-language support expansion
- [ ] Accessibility improvements (ARIA labels, keyboard navigation)

