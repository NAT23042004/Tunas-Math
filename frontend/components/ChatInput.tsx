'use client';

import { useState } from 'react';

interface ChatInputProps {
  onSend: (content: string, hintRequested?: boolean) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [content, setContent] = useState('');

  const handleSubmit = (hintRequested?: boolean) => {
    if (!content.trim() && !hintRequested) return;
    onSend(content, hintRequested);
    setContent('');
  };

  return (
    <div className="flex gap-2 p-4 border-t">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(); }
        }}
        placeholder="Nhập câu trả lời của bạn..."
        className="flex-1 resize-none rounded border p-2 text-sm"
        rows={2}
        disabled={disabled}
      />
      <button
        onClick={() => handleSubmit()}
        disabled={disabled || !content.trim()}
        className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
      >
        Gửi
      </button>
      <button
        onClick={() => handleSubmit(true)}
        disabled={disabled}
        className="rounded border px-4 py-2 text-sm disabled:opacity-50"
      >
        Gợi ý
      </button>
    </div>
  );
}
