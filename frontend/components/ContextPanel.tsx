'use client';

import { InlineMath } from 'react-katex';
import 'katex/dist/katex.min.css';
import type { Message } from '@/types';

interface ContextPanelProps {
  problemStatement?: string;
  dialogueState: string;
  hintLevel: number;
  messages: Message[];
}

export default function ContextPanel({ problemStatement, dialogueState, hintLevel }: ContextPanelProps) {
  return (
    <div className="h-full overflow-y-auto border-l p-4">
      <h3 className="text-sm font-medium">Trạng thái hội thoại</h3>
      <div className="mt-2 rounded border p-2 text-sm">
        <span className="font-mono">{dialogueState}</span>
      </div>
      <div className="mt-2 text-sm">
        Mức gợi ý: <span className="font-mono">L{hintLevel}</span>
      </div>
      {problemStatement && (
        <div className="mt-4">
          <h4 className="text-sm font-medium">Đề bài</h4>
          <div className="mt-1 text-sm"><InlineMath math={problemStatement} /></div>
        </div>
      )}
    </div>
  );
}
