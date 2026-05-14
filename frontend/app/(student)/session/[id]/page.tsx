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
  const [dialogueState, setDialogueState] = useState('review');
  const [hintLevel, setHintLevel] = useState(0);

  useEffect(() => {
    setSession(sessionId);
    getSessionHistory(sessionId).then((data) => {
      if (data.messages && Array.isArray(data.messages)) {
        (data.messages as Message[]).forEach((msg) => addMessage(msg));
      }
      if (data.dialogue_state) {
        setDialogueState(data.dialogue_state);
      }
      if (data.hint_level !== undefined) {
        setHintLevel(data.hint_level);
      }
    });
  }, [sessionId, setSession, addMessage]);

  const handleSend = async (content: string, hintRequested?: boolean) => {
    setStreaming(true);
    setStreamingText('');

    const userMsg: Message = { role: 'user', content, timestamp: new Date().toISOString() };
    addMessage(userMsg);

    try {
      const stream = await sendMessage(sessionId, { content, hint_requested: hintRequested });
      const reader = stream.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let assistantContent = '';
      let currentToolUse: Record<string, unknown> | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) {
            continue;
          }

          const rawEvent = line.slice(6);

          try {
            const parsed = JSON.parse(rawEvent) as {
              content?: string;
              done?: boolean;
              error?: string;
              session_state?: {
                dialogue_state?: string;
                hint_level?: number;
              };
              solid_type?: string;
            };

            if (parsed.error) {
              throw new Error(parsed.error);
            }

            if (parsed.solid_type) {
              currentToolUse = parsed as Record<string, unknown>;
            }

            if (parsed.content) {
              assistantContent += parsed.content;
              setStreamingText(assistantContent);
            }

            if (parsed.session_state?.dialogue_state) {
              setDialogueState(parsed.session_state.dialogue_state);
            }

            if (parsed.session_state?.hint_level !== undefined) {
              setHintLevel(parsed.session_state.hint_level);
            }
          } catch (error) {
            if (error instanceof Error) {
              throw error;
            }
            assistantContent += rawEvent;
            setStreamingText(assistantContent);
          }
        }
      }

      const assistantMsg: Message = {
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date().toISOString(),
      };
      if (currentToolUse) {
        (assistantMsg as unknown as Record<string, unknown>).tool_call = {
          name: 'render_geometry',
          input: currentToolUse,
        };
      }
      addMessage(assistantMsg);
    } finally {
      setStreamingText('');
      setStreaming(false);
    }
  };

  return (
    <div className="flex h-screen">
      <div className="flex-1">
        <ChatPanel messages={messages} isStreaming={isStreaming} streamingText={streamingText} onSend={handleSend} />
      </div>
      <div className="w-80">
        <ContextPanel dialogueState={dialogueState} hintLevel={hintLevel} messages={messages} />
      </div>
    </div>
  );
}
