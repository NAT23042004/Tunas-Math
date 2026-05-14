'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
    else if (session && (session.user as Record<string, unknown>).role !== 'admin') router.push('/dashboard');
  }, [session, status, router]);

  if (status === 'loading') return <div className="p-8 text-center">Đang tải...</div>;

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r p-4">
        <h2 className="text-lg font-semibold">Admin Panel</h2>
        <nav className="mt-6 space-y-2">
          <a href="/admin/dashboard" className="block rounded px-3 py-2 hover:bg-gray-100">Dashboard</a>
        </nav>
      </aside>
      <main className="flex-1">{children}</main>
    </div>
  );
}
