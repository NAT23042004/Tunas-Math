'use client';

interface TopicCardProps {
  topicId: string;
  name: string;
  mastery?: number;
  isRecommended?: boolean;
  onClick: () => void;
}

export default function TopicCard({ name, mastery = 0, isRecommended, onClick }: TopicCardProps) {
  return (
    <button
      onClick={onClick}
      className="rounded-lg border p-4 text-left hover:bg-gray-50 transition-colors"
    >
      <div className="flex items-center justify-between">
        <h3 className="font-medium">{name}</h3>
        {isRecommended && <span className="rounded bg-green-100 px-2 py-0.5 text-xs text-green-700">Gợi ý</span>}
      </div>
      <div className="mt-2 h-2 rounded-full bg-gray-200">
        <div className="h-full rounded-full bg-blue-600" style={{ width: `${mastery * 100}%` }} />
      </div>
      <p className="mt-1 text-xs text-gray-500">Thành thạo: {Math.round(mastery * 100)}%</p>
    </button>
  );
}
