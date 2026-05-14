// frontend/lib/api.ts
import axios from 'axios';
import type {
  AdminStats,
  MasteryData,
  Problem,
  Session,
  SessionCompleteRequest,
  SessionCreateRequest,
  SessionMessageRequest,
  SessionSummaryResponse,
} from '@/types';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export async function createSession(data: SessionCreateRequest): Promise<Session> {
  const res = await api.post('/api/sessions', data);
  return res.data;
}

export async function sendMessage(sessionId: string, data: SessionMessageRequest): Promise<ReadableStream> {
  const res = await fetch(`${api.defaults.baseURL}/api/sessions/${sessionId}/message?stream=true`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
    body: JSON.stringify(data),
  });
  if (!res.ok || !res.body) {
    throw new Error(`Failed to stream message: ${res.status}`);
  }
  return res.body;
}

export async function completeSession(sessionId: string, data: SessionCompleteRequest): Promise<SessionSummaryResponse> {
  const res = await api.put(`/api/sessions/${sessionId}/complete`, data);
  return res.data;
}

export async function getProblems(topicId?: string, difficulty?: string, isGeometry?: boolean): Promise<Problem[]> {
  const params = new URLSearchParams();
  if (topicId) params.set('topic_id', topicId);
  if (difficulty) params.set('difficulty', difficulty);
  if (isGeometry !== undefined) params.set('is_geometry', String(isGeometry));
  const res = await api.get(`/api/problems?${params.toString()}`);
  return res.data;
}

export async function getMyProgress(): Promise<MasteryData> {
  const res = await api.get('/api/progress/me');
  return res.data;
}

export async function getSession(sessionId: string): Promise<Session> {
  const res = await api.get(`/api/sessions/${sessionId}`);
  return res.data;
}

export async function getSessions(): Promise<Session[]> {
  const res = await api.get('/api/sessions');
  return res.data;
}

export async function getAdminStats(): Promise<AdminStats> {
  const res = await api.get('/api/admin/stats');
  return res.data;
}

export default api;
