'use client';

import { useState } from 'react';

interface SessionSummaryProps {
  summary: string;
  masteryDelta: number;
  nextTopic: string;
  onRate: (rating: number) => void;
  onContinue: () => void;
}

export default function SessionSummary({ summary, masteryDelta, nextTopic, onRate, onContinue }: SessionSummaryProps) {
  const [rating, setRating] = useState(0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="rounded-lg bg-white p-6 max-w-md w-full">
        <h2 className="text-lg font-semibold">Hoàn thành phiên học!</h2>
        <p className="mt-2 text-sm text-gray-600">{summary}</p>
        <div className="mt-3 text-sm">Tiến bộ: <span className="text-green-600">+{Math.round(masteryDelta * 100)}%</span></div>
        <div className="mt-4">
          <p className="text-sm">Bạn thấy bài này thế nào?</p>
          <div className="mt-1 flex gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button key={star} onClick={() => setRating(star)} className={`text-2xl ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}>
                ★
              </button>
            ))}
          </div>
        </div>
        <p className="mt-3 text-sm">Chủ đề tiếp theo: <span className="font-medium">{nextTopic}</span></p>
        <div className="mt-4 flex gap-2">
          <button onClick={() => { onRate(rating); onContinue(); }} className="rounded bg-blue-600 px-4 py-2 text-sm text-white">Tiếp tục</button>
        </div>
      </div>
    </div>
  );
}
