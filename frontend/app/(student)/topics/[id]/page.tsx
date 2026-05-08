'use client';

import { useParams } from 'next/navigation';

export default function TopicDetailPage() {
  const params = useParams();
  const topicId = params.id as string;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">{topicId.split('.').pop()}</h1>
      <p className="mt-4 text-gray-500">Danh sách bài tập đang được cập nhật...</p>
      <button
        onClick={() => window.location.href = '/session/new'}
        className="mt-4 rounded bg-blue-600 px-4 py-2 text-white"
      >
        Bắt đầu học chủ đề này
      </button>
    </div>
  );
}
