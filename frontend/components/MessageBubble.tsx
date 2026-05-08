'use client';

import React from 'react';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';
import type { Message } from '@/types';
import GeometryViewer from './GeometryViewer';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  const renderContent = (text: string) => {
    const parts = text.split(/(\$\$[\s\S]*?\$\$|\$[^$\n]+\$)/g);
    return parts.map((part, i) => {
      if (part.startsWith('$$') && part.endsWith('$$')) {
        return <BlockMath key={i} math={part.slice(2, -2)} />;
      } else if (part.startsWith('$') && part.endsWith('$')) {
        return <InlineMath key={i} math={part.slice(1, -1)} />;
      }
      return <span key={i}>{part}</span>;
    });
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3`}>
      <div className={`max-w-[80%] rounded-lg px-4 py-2 ${isUser ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
        {message.tool_call?.name === 'render_geometry' ? (
          <GeometryViewer solidSpec={message.tool_call.input as Record<string, unknown>} height={300} />
        ) : (
          <div className="text-sm">{renderContent(message.content)}</div>
        )}
      </div>
    </div>
  );
}
