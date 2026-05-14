'use client';

import { SessionProvider } from 'next-auth/react';
import { useSession } from 'next-auth/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { useAuthStore } from '@/lib/authStore';
import type { User } from '@/types';

function AuthSyncGate({
  children,
  queryClient,
}: {
  children: React.ReactNode;
  queryClient: QueryClient;
}) {
  const { data: session, status } = useSession();
  const { setAuth, clearAuth } = useAuthStore();
  const [isAuthReady, setIsAuthReady] = useState(false);

  useEffect(() => {
    setIsAuthReady(false);

    if (status === 'loading') {
      return;
    }

    if (status === 'authenticated' && session?.user) {
      const accessToken = session.user.accessToken;
      const userId = session.user.userId;

      if (accessToken && userId) {
        const authUser: User = {
          id: userId,
          userId,
          email: session.user.email as string,
          name: session.user.name as string,
          role: session.user.role ?? 'student',
        };
        setAuth(authUser, accessToken);
        setIsAuthReady(true);
      }
      return;
    }

    clearAuth();
    setIsAuthReady(true);
  }, [clearAuth, session, setAuth, status]);

  if (status === 'loading' || !isAuthReady) {
    return <div className="p-8 text-center">Dang tai...</div>;
  }

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

export default function SessionProviderWrapper({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <SessionProvider>
      <AuthSyncGate queryClient={queryClient}>{children}</AuthSyncGate>
    </SessionProvider>
  );
}
