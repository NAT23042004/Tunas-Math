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
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const res = await fetch(
    `${API_URL}/api/sessions/${sessionId}/message?stream=true`,
    {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    }
  )

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `HTTP ${res.status}`)
  }

  const reader = res.body?.getReader()
  const decoder = new TextDecoder()

  if (!reader) throw new Error("No readable stream available")

  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split("\n")

    // Keep the last potentially incomplete line
    buffer = lines.pop() || ""

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.error) throw new Error(data.error)
          if (onChunk) {
            onChunk(data.content || "", data.done || false, data.session_state)
          }
        } catch (e) {
          console.error("Error parsing SSE data:", e)
        }
      }
    }
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
