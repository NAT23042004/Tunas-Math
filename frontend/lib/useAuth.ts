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
      const accessToken = session.user.accessToken;
      const userId = session.user.userId;
      if (accessToken && userId) {
        const authUser: User = {
          id: userId,
          email: session.user.email as string,
          name: session.user.name as string,
          role: session.user.role ?? 'student',
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
