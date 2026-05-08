import type {
  Problem,
  Session,
  SessionCompleteResponse,
  MessageResponse,
  Progress,
  MasteryMap,
  GeometryParams,
  HealthResponse,
} from "./types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `HTTP ${res.status}`)
  }

  return res.json()
}

// Health
export async function checkHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health")
}

// Users
export async function createUser(
  data: { email: string; name: string },
  token?: string
): Promise<{ id: string; email: string; name: string }> {
  return request<{ id: string; email: string; name: string }>("/api/users", {
    method: "POST",
    body: JSON.stringify(data),
  }, token)
}

// Problems
export async function getProblems(
  params?: {
    topic_id?: string
    difficulty?: string
    is_geometry?: boolean
    limit?: number
  },
  token?: string
): Promise<Problem[]> {
  const query = new URLSearchParams()
  if (params?.topic_id) query.set("topic_id", params.topic_id)
  if (params?.difficulty) query.set("difficulty", params.difficulty)
  if (params?.is_geometry !== undefined)
    query.set("is_geometry", String(params.is_geometry))
  if (params?.limit) query.set("limit", String(params.limit))

  const qs = query.toString()
  return request<Problem[]>(`/api/problems${qs ? `?${qs}` : ""}`, {}, token)
}

export async function getProblem(
  problemId: string,
  token?: string
): Promise<Problem> {
  return request<Problem>(`/api/problems/${problemId}`, {}, token)
}

export async function getProblemGeometry(
  problemId: string,
  token?: string
): Promise<GeometryParams> {
  return request<GeometryParams>(
    `/api/problems/${problemId}/geometry`,
    {},
    token
  )
}

// Sessions
export async function createSession(
  data: {
    user_id: string
    topic_id: string
    problem_id?: string
  },
  token?: string
): Promise<Session> {
  return request<Session>(
    "/api/sessions",
    {
      method: "POST",
      body: JSON.stringify(data),
    },
    token
  )
}

export async function getSession(
  sessionId: string,
  token?: string
): Promise<Session> {
  return request<Session>(`/api/sessions/${sessionId}`, {}, token)
}

export async function sendMessage(
  sessionId: string,
  data: { content: string; hint_requested?: boolean },
  token?: string
): Promise<MessageResponse> {
  return request<MessageResponse>(
    `/api/sessions/${sessionId}/message`,
    {
      method: "POST",
      body: JSON.stringify(data),
    },
    token
  )
}

export async function sendMessageStream(
  sessionId: string,
  data: { content: string; hint_requested?: boolean },
  token?: string,
  onChunk?: (content: string, done: boolean, sessionState?: any) => void
): Promise<void> {
  // Use non-streaming endpoint since backend returns JSON
  const response = await sendMessage(sessionId, data, token);

  if (onChunk) {
    // Send the content as one chunk
    onChunk(response.message.content, false, undefined);
    // Signal completion with session state
    onChunk("", true, response.session_state);
  }
}

export async function completeSession(
  sessionId: string,
  data: { student_rating?: number },
  token?: string
): Promise<SessionCompleteResponse> {
  return request<SessionCompleteResponse>(
    `/api/sessions/${sessionId}/complete`,
    {
      method: "PUT",
      body: JSON.stringify(data),
    },
    token
  )
}

// Progress
export async function getProgress(
  userId: string,
  token?: string
): Promise<Progress[]> {
  return request<Progress[]>(`/api/progress?user_id=${userId}`, {}, token)
}

export async function getMasteryMap(
  userId: string,
  token?: string
): Promise<MasteryMap> {
  return request<MasteryMap>(
    `/api/progress/mastery?user_id=${userId}`,
    {},
    token
  )
}
