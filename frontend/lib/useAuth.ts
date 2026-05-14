// frontend/lib/useAuth.ts
'use client';

import { useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useAuthStore } from './authStore';
import type { User } from '@/types';

export function useAuth() {
  const { data: session, status } = useSession();
  const { setAuth, clearAuth } = useAuthStore();

  const isAuthenticated = status === 'authenticated' && !!session;

  // Sync auth state with localStorage when session changes
  useEffect(() => {
    if (isAuthenticated && session?.user) {
      const user = session.user as Record<string, unknown>;
      const accessToken = user.accessToken as string | undefined;
      const userId = user.userId as string | undefined;
      if (accessToken && userId) {
        const authUser: User = {
          id: userId,
          email: user.email as string,
          name: user.name as string,
          role: 'student',
          userId,
        };
        setAuth(authUser, accessToken);
      }
    } else if (status === 'unauthenticated') {
      clearAuth();
    }
  }, [isAuthenticated, session, status, setAuth, clearAuth]);

  return { session, status, isAuthenticated, setAuth, clearAuth };
}
