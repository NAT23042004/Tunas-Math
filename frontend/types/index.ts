// frontend/types/index.ts

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
  role: 'student' | 'admin';
}

export interface Session {
  id: string;
  user_id: string;
  problem_id?: string;
  topic_id: string;
  status: 'active' | 'completed' | 'abandoned';
  dialogue_state: 'review' | 'heuristic' | 'rectify' | 'summarize';
  hint_level: number;
  hint_count: number;
  fail_count: number;
  messages: Message[];
  summary?: string;
  student_rating?: number;
  started_at: string;
  ended_at?: string;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  tool_call?: ToolCall;
}

export interface ToolCall {
  name: string;
  input: Record<string, unknown>;
}

export interface Problem {
  id: string;
  topic_id: string;
  statement_latex: string;
  difficulty: 'easy' | 'medium' | 'hard';
  is_geometry: boolean;
  geometry_params?: GeometryParams;
  source?: string;
}

export interface GeometryParams {
  solid_type: 'pyramid' | 'prism' | 'cone' | 'sphere' | 'cylinder' | 'composite';
  params: Record<string, unknown>;
  labels?: Record<string, string>;
}

export interface MasteryData {
  mastery_by_topic: Record<string, number>;
  sessions_this_week: number;
  suggested_topics: string[];
  streak_days: number;
}

export interface SolidSpec {
  solid_type: 'pyramid' | 'prism' | 'cone' | 'sphere' | 'cylinder' | 'composite';
  params: Record<string, unknown>;
  highlights?: string[];
  animated?: boolean;
}

export interface SessionCreateRequest {
  topic_id: string;
  problem_id?: string;
  initial_message?: string;
}

export interface SessionMessageRequest {
  content: string;
  hint_requested?: boolean;
}

export interface SessionCompleteRequest {
  student_rating?: number;
}