/**
 * Report Generation API Client
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export interface ReportStatus {
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  report?: any;
}

export async function generateReport(sessionId: string): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/reports/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ session_id: sessionId }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate report');
  }

  return response.json();
}

export async function getReportStatus(sessionId: string): Promise<ReportStatus> {
  const response = await fetch(`${API_BASE_URL}/api/reports/status/${sessionId}`);

  if (!response.ok) {
    throw new Error('Failed to get report status');
  }

  return response.json();
}

export async function downloadReport(sessionId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/reports/download/${sessionId}`);

  if (!response.ok) {
    throw new Error('Report not ready');
  }

  const data = await response.json();
  return data.report;
}
