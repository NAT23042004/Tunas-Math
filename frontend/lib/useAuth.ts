// frontend/lib/useAuth.ts
import { useSession } from 'next-auth/react';
import { useAuthStore } from './authStore';

export function useAuth() {
  const { data: session, status } = useSession();
  const { setAuth, clearAuth } = useAuthStore();

  const isAuthenticated = status === 'authenticated' && !!session;

  return { session, status, isAuthenticated, setAuth, clearAuth };
}
