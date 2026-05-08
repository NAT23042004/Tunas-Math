import { useQuery } from "@tanstack/react-query"
import { getProblems, getProgress, getMasteryMap } from "./api"
import type { Problem, Progress } from "./types"
import { useSession } from "next-auth/react"

export function useTopics() {
  const { data: session } = useSession()
  const token = session?.user?.id ? session.user.id : undefined
  const userId = session?.user?.id

  const problemsQuery = useQuery({
    queryKey: ["problems", "all"],
    queryFn: () => getProblems({ limit: 100 }, token),
  })

  const progressQuery = useQuery({
    queryKey: ["progress", userId],
    queryFn: () => getProgress(userId!, token),
    enabled: !!userId,
  })

  // Group problems by topic
  const topicsMap = new Map<string, Problem[]>()
  problemsQuery.data?.forEach((p) => {
    const list = topicsMap.get(p.topic_id) || []
    list.push(p)
    topicsMap.set(p.topic_id, list)
  })

  // Build topics with mastery
  const topics = Array.from(topicsMap.entries()).map(([topicId, problems]) => {
    const progress = progressQuery.data?.find((p: Progress) => p.topic_id === topicId)
    const mastery = progress ? Math.round(progress.mastery_score * 100) : 0
    const has3D = problems.some((p) => p.is_geometry)

    return {
      id: topicId,
      name: formatTopicName(topicId),
      icon: getTopicIcon(topicId),
      mastery,
      color: getTopicColor(topicId, mastery),
      chapters: `${problems.length} bài tập`,
      desc: problems[0]?.difficulty || "",
      has3D,
      locked: mastery === 0 && !progress,
    }
  })

  return {
    topics,
    isLoading: problemsQuery.isLoading || progressQuery.isLoading,
    isError: problemsQuery.isError || progressQuery.isError,
    error: problemsQuery.error || progressQuery.error,
  }
}

function formatTopicName(topicId: string): string {
  const names: Record<string, string> = {
    "giai-tich": "Giải tích",
    "hinh-hoc-khong-gian": "Hình học không gian",
    "xac-suat-thong-ke": "Xác suất & Thống kê",
    "ham-so-dai-so": "Hàm số & Đại số",
    "luong-giac": "Lượng giác",
    "so-phuc": "Số phức",
  }
  return names[topicId] || topicId
}

function getTopicIcon(topicId: string): string {
  const icons: Record<string, string> = {
    "giai-tich": "∫",
    "hinh-hoc-khong-gian": "△",
    "xac-suat-thong-ke": "P",
    "ham-so-dai-so": "f(x)",
    "luong-giac": "sin",
    "so-phuc": "ℂ",
  }
  return icons[topicId] || "?"
}

function getTopicColor(topicId: string, mastery: number): string {
  if (mastery >= 60) return "green"
  if (mastery >= 40) return "amber"
  if (mastery > 0) return "blue"
  return "ink-3"
}
