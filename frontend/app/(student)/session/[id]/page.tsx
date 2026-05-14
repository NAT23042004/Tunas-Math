'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ChatPanel from '@/components/ChatPanel';
import ContextPanel from '@/components/ContextPanel';
import SessionSummary from '@/components/SessionSummary';
import { completeSession, getSession, sendMessage } from '@/lib/api';
import { useSessionStore } from '@/lib/sessionStore';
import type { Message, SessionSummaryResponse } from '@/types';

export default function SessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.id as string;
  const { messages, addMessage, setSession, setStreaming, isStreaming } = useSessionStore();
  const [streamingText, setStreamingText] = useState('');
  const [dialogueState, setDialogueState] = useState('review');
  const [hintLevel, setHintLevel] = useState(0);
  const [summaryData, setSummaryData] = useState<SessionSummaryResponse | null>(null);
  const [isRatingDialogOpen, setIsRatingDialogOpen] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);

  useEffect(() => {
    setSession(sessionId);
    getSession(sessionId).then((data) => {
      if (data.messages && Array.isArray(data.messages)) {
        (data.messages as Message[]).forEach((msg) => addMessage(msg));
      }
      setDialogueState(data.dialogue_state || 'review');
      setHintLevel(data.hint_level ?? 0);
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

  const handleComplete = () => {
    setIsRatingDialogOpen(true);
  };

  const handleSubmitCompletion = async (rating: number) => {
    setIsCompleting(true);
    try {
      const result = await completeSession(sessionId, { student_rating: rating });
      setIsRatingDialogOpen(false);
      setSummaryData(result);
    } finally {
      setIsCompleting(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col xl:flex-row">
      <div className="flex min-h-[65vh] flex-1 flex-col">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div>
            <div className="text-sm font-medium text-slate-900">Phien hoc truc tiep</div>
            <div className="text-xs text-slate-500">Trang thai: {dialogueState} | Goi y: L{hintLevel}</div>
          </div>
          <button
            type="button"
            onClick={handleComplete}
            disabled={isCompleting}
            className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          >
            {isCompleting ? 'Dang ket thuc...' : 'Ket thuc phien'}
          </button>
        </div>
        <div className="flex-1">
          <ChatPanel messages={messages} isStreaming={isStreaming} streamingText={streamingText} onSend={handleSend} />
        </div>
      </div>
      <div className="border-t xl:w-96 xl:border-l xl:border-t-0">
        <ContextPanel dialogueState={dialogueState} hintLevel={hintLevel} messages={messages} />
      </div>

      {isRatingDialogOpen && (
        <SessionSummary
          mode="rating"
          summary="Danh gia phien hoc de cap nhat mastery chinh xac."
          isSubmitting={isCompleting}
          onCancel={() => setIsRatingDialogOpen(false)}
          onFinish={handleSubmitCompletion}
        />
      )}

      {summaryData && (
        <SessionSummary
          mode="summary"
          summary={summaryData.summary}
          masteryDelta={summaryData.mastery_delta}
          nextTopic={summaryData.next_suggested_topic}
          onFinish={() => {
            setSummaryData(null);
            router.push('/history');
          }}
        />
      )}
    </div>
  );
}
