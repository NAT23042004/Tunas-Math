'use client';

import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import LoadingState from '@/components/LoadingState';

export default function StudentLayout({ children }: { children: React.ReactNode }) {
  const { status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') router.push('/login');
  }, [status, router]);

  if (status === 'loading') {
    return (
      <LoadingState
        title="Dang xac thuc"
        message="Phien dang nhap dang duoc kiem tra truoc khi vao khu hoc sinh."
        fullHeight
      />
    );
  }

  return (
    <div className="flex min-h-screen flex-col md:flex-row">
      <aside className="border-b p-4 md:w-64 md:border-b-0 md:border-r">
        <h2 className="text-lg font-semibold">Toán Socratic</h2>
        <nav className="mt-6 grid gap-2 sm:grid-cols-2 md:block">
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
