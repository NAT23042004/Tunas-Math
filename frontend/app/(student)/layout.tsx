'use client';

import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  const { status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
  }, [status, router]);

  if (status === 'loading') return <div className="p-8 text-center">Đang tải...</div>;

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 border-r p-4">
        <h2 className="text-lg font-semibold">Toán Socratic</h2>
        <nav className="mt-6 space-y-2">
          <Link href="/dashboard" className="block rounded px-3 py-2 hover:bg-gray-100">Dashboard</Link>
          <Link href="/session/new" className="block rounded bg-blue-600 px-3 py-2 text-white hover:bg-blue-700">Bắt đầu học</Link>
          <Link href="/topics" className="block rounded px-3 py-2 hover:bg-gray-100">Chủ đề</Link>
          <Link href="/history" className="block rounded px-3 py-2 hover:bg-gray-100">Lịch sử</Link>
        </nav>
      </aside>
      <main className="flex-1">{children}</main>
    </div>
  );
}
