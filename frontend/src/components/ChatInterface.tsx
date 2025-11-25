// components/FarmerChatInterface.tsx
interface FarmerChatInterfaceProps {
  messages: Array<{
    text: string;
    isUser: boolean;
    timestamp: Date;
  }>;
  currentStep: number;
  totalSteps: number;
  onVoiceInput: (transcript: string) => void;
  isProcessing: boolean;
  options?: string[];
  onOptionSelect?: (option: string) => void;
}