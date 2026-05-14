'use client';

import { useRouter } from 'next/navigation';
import { useTopics } from '@/lib/useTopics';
import TopicCard from '@/components/TopicCard';

export default function TopicsPage() {
  const router = useRouter();
  const { data: topics, isLoading } = useTopics();

  if (isLoading) return <div className="p-8">Đang tải...</div>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">Chủ đề</h1>
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {topics?.map((topic) => (
          <TopicCard
            key={topic.id}
            topicId={topic.topic_id}
            name={topic.topic_id.split('.').pop() || topic.topic_id}
            mastery={0.5}
            onClick={() => router.push(`/session/new?topic=${encodeURIComponent(topic.topic_id)}`)}
          />
        ))}
      </div>
    </div>
  );
}
