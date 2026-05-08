// frontend/lib/useTopics.ts
import { useQuery } from '@tanstack/react-query';
import { getProblems } from './api';
import type { Problem } from '@/types';

export function useTopics(topicId?: string, difficulty?: string, isGeometry?: boolean) {
  return useQuery<Problem[], Error>({
    queryKey: ['problems', topicId, difficulty, isGeometry],
    queryFn: () => getProblems(topicId, difficulty, isGeometry),
  });
}
