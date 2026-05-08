'use client';

import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function HomePage() {
  const { status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'authenticated') router.push('/dashboard');
  }, [status, router]);

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold">Toán Socratic</h1>
        <p className="mt-4 text-lg text-gray-600">Gia sư Toán thông minh cho học sinh lớp 12</p>
        <button onClick={() => router.push('/login')} className="mt-6 rounded bg-blue-600 px-6 py-3 text-white hover:bg-blue-700">
          Bắt đầu học
        </button>
      </div>
    </div>
  );
}
