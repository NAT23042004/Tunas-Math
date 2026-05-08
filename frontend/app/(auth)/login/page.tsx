'use client';

import { signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();

  const handleGoogleSignIn = async () => {
    await signIn('google', { callbackUrl: '/dashboard' });
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="w-full max-w-sm rounded-lg border p-6">
        <h1 className="text-xl font-semibold text-center">Đăng nhập</h1>
        <p className="mt-2 text-center text-sm text-gray-600">Chào mừng đến với Toán Socratic</p>
        <button
          onClick={handleGoogleSignIn}
          className="mt-4 w-full rounded bg-blue-600 py-2 text-white hover:bg-blue-700"
        >
          Đăng nhập với Google
        </button>
      </div>
    </div>
  );
}
