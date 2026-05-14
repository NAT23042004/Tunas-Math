'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { createSession } from '@/lib/api';

export default function NewSessionPage() {
  const searchParams = useSearchParams();
  const [topicId, setTopicId] = useState(searchParams.get('topic') || 'hinh-hoc.hinh-chop');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { data: session, status } = useSession();

  useEffect(() => {
    const requestedTopic = searchParams.get('topic');
    if (requestedTopic) {
      setTopicId(requestedTopic);
    }
  }, [searchParams]);

  useEffect(() => {
    // Store user_id in localStorage when session is available
    if (session?.user) {
      const userId = session.user.userId;
      if (userId) {
        localStorage.setItem('userId', userId);
      }
    }
  }, [session]);

  const handleStart = async () => {
    if (!session?.user) {
      alert('Vui lòng đăng nhập trước');
      router.push('/login');
      return;
    }

    setIsLoading(true);
    try {
      const res = await createSession({ topic_id: topicId });
      router.push(`/session/${res.id}`);
    } catch {
      alert('Không thể tạo phiên học');
    } finally {
      setIsLoading(false);
    }
  };

  if (status === 'loading') {
    return <div className="p-8">Đang tải...</div>;
  }

  if (status === 'unauthenticated') {
    return (
      <div className="p-8">
        <p className="mb-4">Vui lòng đăng nhập để bắt đầu phiên học</p>
        <button
          onClick={() => router.push('/login')}
          className="rounded bg-blue-600 px-4 py-2 text-white"
        >
          Đăng nhập
        </button>
      </div>
    );
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Bắt đầu phiên học mới</h1>
      <div className="mt-6 max-w-sm space-y-4">
        <div>
          <label className="block text-sm font-medium">Chủ đề</label>
          <select value={topicId} onChange={(e) => setTopicId(e.target.value)} className="mt-1 w-full rounded border p-2">
            <option value="hinh-hoc.hinh-chop">Hình học - Hình chóp</option>
            <option value="hinh-hoc.lang-tru">Hình học - Lăng trụ</option>
            <option value="giai-tich.dao-ham">Giải tích - Đạo hàm</option>
          </select>
        </div>
        <button onClick={handleStart} disabled={isLoading} className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50">
          {isLoading ? 'Đang tạo...' : 'Bắt đầu'}
        </button>
      </div>
    </div>
  );
}
