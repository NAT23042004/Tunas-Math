'use client';

import { useState } from 'react';

interface SessionSummaryProps {
  summary: string;
  masteryDelta?: number;
  nextTopic?: string;
  mode?: 'rating' | 'summary';
  isSubmitting?: boolean;
  onCancel?: () => void;
  onFinish: (rating: number) => void | Promise<void>;
}

export default function SessionSummary({
  summary,
  masteryDelta,
  nextTopic,
  mode = 'summary',
  isSubmitting = false,
  onCancel,
  onFinish,
}: SessionSummaryProps) {
  const [rating, setRating] = useState(0);
  const isRatingMode = mode === 'rating';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="rounded-lg bg-white p-6 max-w-md w-full">
        <h2 className="text-lg font-semibold">Hoàn thành phiên học!</h2>
        <p className="mt-2 text-sm text-gray-600">{summary}</p>

        {!isRatingMode && masteryDelta !== undefined && (
          <div className="mt-3 text-sm">Tiến bộ: <span className="text-green-600">+{Math.round(masteryDelta * 100)}%</span></div>
        )}

        {isRatingMode && (
          <div className="mt-4">
            <p className="text-sm">Bạn thấy bài này thế nào?</p>
            <div className="mt-1 flex gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className={`text-2xl ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>
        )}

        {!isRatingMode && nextTopic && (
          <p className="mt-3 text-sm">Chủ đề tiếp theo: <span className="font-medium">{nextTopic}</span></p>
        )}

        <div className="mt-4 flex gap-2">
          {isRatingMode && onCancel && (
            <button
              type="button"
              onClick={onCancel}
              disabled={isSubmitting}
              className="rounded border px-4 py-2 text-sm text-gray-700 disabled:opacity-50"
            >
              Hủy
            </button>
          )}
          <button
            type="button"
            onClick={() => onFinish(rating)}
            disabled={isSubmitting || (isRatingMode && rating === 0)}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            {isSubmitting ? 'Đang lưu...' : isRatingMode ? 'Hoàn thành' : 'Tiếp tục'}
          </button>
        </div>
      </div>
    </div>
  );
}
