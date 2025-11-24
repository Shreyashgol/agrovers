/**
 * API Client for backend communication.
 * 
 * Handles all HTTP requests to the FastAPI backend.
 * 
 * To change API base URL:
 *   Update API_BASE_URL constant below
 */

import axios from 'axios';

// API base URL - change this if backend runs on different port/host
const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types matching backend models
export type Language = 'hi' | 'en';

export interface StartSessionRequest {
  language: Language;
}

export interface StartSessionResponse {
  session_id: string;
  parameter: string;
  question: string;
  step_number: number;
  total_steps: number;
}

export interface NextMessageRequest {
  session_id: string;
  user_message: string;
}

export interface NextMessageResponse {
  session_id: string;
  parameter: string;
  question?: string;
  helper_text?: string;
  answers: SoilTestResult;
  is_complete: boolean;
  step_number: number;
  total_steps: number;
  helper_mode: boolean;
  audio_url?: string;
  audit?: {
    asr_conf: number;
    validator_conf: number;
    llm_conf: number;
    combined_conf: number;
    asr_text?: string;
  };
}

export interface SoilTestResult {
  color?: string;
  moisture?: string;
  smell?: string;
  ph_category?: string;
  ph_value?: number;
  soil_type?: string;
  earthworms?: string;
  location?: string;
  fertilizer_used?: string;
}

export interface SessionStateResponse {
  session_id: string;
  language: Language;
  current_parameter: string;
  answers: SoilTestResult;
  step_number: number;
  total_steps: number;
  is_complete: boolean;
}

/**
 * Start a new session with language selection.
 */
export async function startSession(
  language: Language
): Promise<StartSessionResponse> {
  const response = await apiClient.post<StartSessionResponse>(
    '/session/start',
    { language }
  );
  return response.data;
}

/**
 * Send user message (text or audio) and get next step.
 */
export async function sendNext(
  sessionId: string,
  userMessage?: string,
  audioBlob?: Blob
): Promise<NextMessageResponse> {
  const formData = new FormData();
  formData.append('session_id', sessionId);
  
  if (userMessage) {
    formData.append('user_text', userMessage);
  }
  
  if (audioBlob) {
    formData.append('audio_file', audioBlob, 'audio.wav');
  }
  
  const response = await apiClient.post<NextMessageResponse>(
    '/session/next',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
}

/**
 * Get current session state.
 */
export async function getState(
  sessionId: string
): Promise<SessionStateResponse> {
  const response = await apiClient.get<SessionStateResponse>(
    `/session/state/${sessionId}`
  );
  return response.data;
}

