'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { createSession } from '@/lib/api';

export default function NewSessionPage() {
  const [topicId, setTopicId] = useState('hinh-hoc.hinh-chop');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleStart = async () => {
    setIsLoading(true);
    try {
      const res = await createSession({ topic_id: topicId });
      router.push(`/session/${res.session_id}`);
    } catch {
      alert('Không thể tạo phiên học');
    } finally {
      setIsLoading(false);
    }
  };

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
