import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  getProblems,
  createSession,
  sendMessageStream,
  completeSession,
  getSession,
} from "./api"
import type { Problem, Session, MessageResponse } from "./types"

export function useProblems(topicId?: string, token?: string) {
  return useQuery({
    queryKey: ["problems", topicId],
    queryFn: () => getProblems({ topic_id: topicId, limit: 20 }, token),
    enabled: !!topicId,
  })
}

export function useCreateSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (params: {
      userId: string
      topicId: string
      problemId?: string
      token?: string
    }) =>
      createSession(
        {
          user_id: params.userId,
          topic_id: params.topicId,
          problem_id: params.problemId,
        },
        params.token
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["session"] })
    },
  })
}

export function useSendMessage() {
  return useMutation({
    mutationFn: (params: {
      sessionId: string
      content: string
      hintRequested?: boolean
      token?: string
      onChunk?: (content: string, done: boolean, sessionState?: any) => void
    }) =>
      sendMessageStream(
        params.sessionId,
        {
          content: params.content,
          hint_requested: params.hintRequested,
        },
        params.token,
        params.onChunk
      ),
  })
}

export function useCompleteSession() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (params: {
      sessionId: string
      rating?: number
      token?: string
    }) => completeSession(params.sessionId, { student_rating: params.rating }, params.token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["session"] })
    },
  })
}

export function useSession(sessionId: string | null, token?: string) {
  return useQuery({
    queryKey: ["session", sessionId],
    queryFn: () =>
      getSession(sessionId!, token),
    enabled: !!sessionId,
  })
}
