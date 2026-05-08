// frontend/lib/useDashboard.ts
import { useQuery } from '@tanstack/react-query';
import { getMyProgress } from './api';
import type { MasteryData } from '@/types';

export function useDashboard() {
  return useQuery<MasteryData, Error>({
    queryKey: ['progress', 'me'],
    queryFn: getMyProgress,
  });
}
