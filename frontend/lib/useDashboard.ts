import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { getMasteryMap, getProgress, getProblems, createUser } from "./api"
import type { MasteryMap, Progress, Problem } from "./types"
import { useSession } from "next-auth/react"
import { useState, useEffect } from "react"

export function useDashboardData() {
  const { data: session } = useSession()
  const queryClient = useQueryClient()
  const token = session?.user?.id ? session.user.id : undefined
  const userId = session?.user?.id

  // Create/get user in backend when session loads
  const [backendUserId, setBackendUserId] = useState<string | null>(null)
  const [isCreatingUser, setIsCreatingUser] = useState(false)

  useEffect(() => {
    if (!session?.user?.email || backendUserId) return

    const createUserInBackend = async () => {
      setIsCreatingUser(true)
      try {
        const userData = await createUser({
          email: session.user.email!,
          name: session.user.name || '',
        })
        setBackendUserId(userData.id)
        // Invalidate queries to refetch with correct user ID
        queryClient.invalidateQueries({ queryKey: ["masteryMap"] })
        queryClient.invalidateQueries({ queryKey: ["progress"] })
      } catch (error) {
        console.error("Failed to create/get user:", error)
      } finally {
        setIsCreatingUser(false)
      }
    }

    createUserInBackend()
  }, [session?.user?.email])

  const effectiveUserId = backendUserId || userId

  const masteryQuery = useQuery({
    queryKey: ["masteryMap"],
    queryFn: () => getMasteryMap(effectiveUserId!, token),
    enabled: !!effectiveUserId,
  })

  const progressQuery = useQuery({
    queryKey: ["progress", effectiveUserId],
    queryFn: () => getProgress(effectiveUserId!, token),
    enabled: !!effectiveUserId,
  })

  const problemsQuery = useQuery({
    queryKey: ["problems", "all"],
    queryFn: () => getProblems({ limit: 100 }, token),
  })

  return {
    masteryMap: masteryQuery.data,
    progress: progressQuery.data,
    problems: problemsQuery.data,
    isLoading: masteryQuery.isLoading || progressQuery.isLoading || problemsQuery.isLoading || isCreatingUser,
    isError: masteryQuery.isError || progressQuery.isError,
    error: masteryQuery.error || progressQuery.error,
  }
}
