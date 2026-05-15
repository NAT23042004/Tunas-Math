'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import LoadingState from '@/components/LoadingState';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
    else if (session && session.user.role !== 'admin') router.push('/dashboard');
  }, [session, status, router]);

  if (status === 'loading') {
    return (
      <LoadingState
        title="Dang xac thuc quan tri"
        message="Quyen truy cap dang duoc xac minh."
        fullHeight
      />
    );
  }

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="border-b p-4 md:w-64 md:border-b-0 md:border-r">
        <h2 className="text-lg font-semibold">Admin Panel</h2>
        <nav className="mt-6 space-y-2">
          <a href="/admin/dashboard" className="block rounded px-3 py-2 hover:bg-gray-100">Dashboard</a>
        </nav>
      </aside>
      <main className="flex-1">{children}</main>
    </div>
  );
}
