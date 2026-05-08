'use client';

interface HintButtonProps {
  level: number;
  onRequest: () => void;
}

export default function HintButton({ level, onRequest }: HintButtonProps) {
  return (
    <button
      onClick={onRequest}
      className="flex items-center gap-1 rounded border px-3 py-1 text-sm hover:bg-gray-50"
    >
      <span>Gợi ý</span>
      <span className="rounded bg-gray-200 px-1.5 py-0.5 text-xs">L{level}</span>
    </button>
  );
}
