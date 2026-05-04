export type UserRole = "student" | "admin"

export type SessionStatus = "active" | "completed" | "abandoned"

export type DialogueState = "review" | "heuristic" | "rectify" | "summarize"

export type DifficultyLevel = "easy" | "medium" | "hard"

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  created_at: string
  last_active?: string
}

export interface Problem {
  id: string
  topic_id: string
  statement_latex: string
  difficulty: DifficultyLevel
  answer: string
  is_geometry: boolean
  geometry_params?: {
    solid_type: string
    params: Record<string, number>
    labels: Record<string, string>
  }
  source?: string
  misconceptions?: string[]
  created_at: string
}

export interface SessionMessage {
  role: "user" | "assistant"
  content: string
  timestamp: string
  tool_calls?: Array<Record<string, unknown>>
}

export interface Session {
  id: string
  user_id: string
  topic_id: string
  problem_id?: string
  status: SessionStatus
  dialogue_state: DialogueState
  hint_level: number
  hint_count: number
  fail_count: number
  messages: SessionMessage[]
  summary?: string
  student_rating?: number
  started_at: string
  ended_at?: string
}

export interface SessionCompleteResponse {
  summary: string
  mastery_delta: number
  next_suggested_topic: string
}

export interface MessageResponse {
  message: SessionMessage
  session_state: {
    dialogue_state: DialogueState
    hint_level: number
    fail_count: number
  }
}

export interface Progress {
  user_id: string
  topic_id: string
  mastery_score: number
  sessions_count: number
  last_practiced?: string
}

export interface MasteryMap {
  mastery_by_topic: Record<string, number>
  sessions_this_week: number
  suggested_topics: string[]
  streak_days: number
}

export interface GeometryParams {
  solid_type: string
  params: Record<string, number>
  labels: Record<string, string>
}

export interface HealthResponse {
  status: string
  service: string
  version: string
}
