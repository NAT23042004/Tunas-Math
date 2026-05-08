'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import ChatPanel from '@/components/ChatPanel';
import ContextPanel from '@/components/ContextPanel';
import { useSessionStore } from '@/lib/sessionStore';
import { sendMessage, getSessionHistory } from '@/lib/api';
import type { Message } from '@/types';

export default function SessionPage() {
  const params = useParams();
  const sessionId = params.id as string;
  const { messages, addMessage, setSession, setStreaming, isStreaming } = useSessionStore();
  const [streamingText, setStreamingText] = useState('');
  const [streamingToolUse, setStreamingToolUse] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    setSession(sessionId);
    getSessionHistory(sessionId).then((data) => {
      if (data.messages) {
        data.messages.forEach((msg: Message) => addMessage(msg));
      }
    });
  }, [sessionId, setSession, addMessage]);

  const handleSend = async (content: string, hintRequested?: boolean) => {
    setStreaming(true);
    setStreamingText('');
    setStreamingToolUse(null);

    const userMsg: Message = { role: 'user', content, timestamp: new Date().toISOString() };
    addMessage(userMsg);

    const stream = await sendMessage(sessionId, { content, hint_requested: hintRequested });

    const reader = stream.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          try {
            const parsed = JSON.parse(data);
            if (typeof parsed === 'string') setStreamingText((prev) => prev + parsed);
            else if (parsed.solid_type) setStreamingToolUse(parsed);
            else if (parsed.dialogue_state) setStreaming(false);
          } catch {
            setStreamingText((prev) => prev + data);
          }
        }
      }
    }

    const assistantMsg: Message = { role: 'assistant', content: streamingText, timestamp: new Date().toISOString() };
    if (streamingToolUse) (assistantMsg as Record<string, unknown>).tool_call = { name: 'render_geometry', input: streamingToolUse };
    addMessage(assistantMsg);
    setStreamingText('');
    setStreamingToolUse(null);
    setStreaming(false);
  };

  return (
    <div className="flex h-screen">
      <div className="flex-1">
        <ChatPanel messages={messages} isStreaming={isStreaming} streamingText={streamingText} onSend={handleSend} />
      </div>
      <div className="w-80">
        <ContextPanel dialogueState="review" hintLevel={0} messages={messages} />
      </div>
    </div>
  );
}
