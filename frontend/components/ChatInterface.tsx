"use client";

import { useState, useRef, useEffect } from "react";
import { useSession } from "next-auth/react";
import { useCreateSession, useProblems, useSendMessage } from "../lib/useChat";
import { Message } from "./Message";
import { LoadingDots } from "./LoadingDots";
import { GeometryViewer } from "./GeometryViewer";

interface MessageType {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export function ChatInterface() {
  const { data: session, status: authStatus } = useSession();
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionState, setSessionState] = useState<{
    dialogue_state: string;
    hint_level: number;
    fail_count: number;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const token = session?.user?.id ? session.user.id : undefined;

  // Queries and Mutations
  const createSessionMutation = useCreateSession();
  const problemsQuery = useProblems("hinh-hoc.hinh-chop", token);
  const sendMessageMutation = useSendMessage();

  const problem = problemsQuery.data?.[0] || null;

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Initialize session
  useEffect(() => {
    if (authStatus === "loading") return;
    if (authStatus === "unauthenticated") {
      window.location.href = "/login";
      return;
    }
    if (!session?.user?.id || sessionId) return;

    const userId = session.user.id;

    const initSession = async () => {
      try {
        const data = await createSessionMutation.mutateAsync({
          userId,
          topicId: "hinh-hoc.hinh-chop",
          token,
        });
        setSessionId(data.id);
        setSessionState({
          dialogue_state: data.dialogue_state,
          hint_level: data.hint_level,
          fail_count: data.fail_count,
        });
      } catch (err: any) {
        setError(err.message || "Failed to initialize session");
      }
    };
    initSession();
  }, [session?.user?.id, authStatus]);

  const sendMessage = async () => {
    if (!input.trim() || !sessionId || isLoading) return;

    const userMessage: MessageType = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setError(null);

    // Add placeholder for assistant message
    const assistantMessage: MessageType = {
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      await sendMessageMutation.mutateAsync({
        sessionId,
        content: input,
        hintRequested: false,
        token,
        onChunk: (content, done, sessionStateData) => {
          if (content) {
            setMessages((prev) => {
              const updated = [...prev];
              const lastMsg = updated[updated.length - 1];
              if (lastMsg && lastMsg.role === "assistant") {
                updated[updated.length - 1] = {
                  ...lastMsg,
                  content: lastMsg.content + content,
                };
              }
              return updated;
            });
          }
          if (done) {
            setIsLoading(false);
            if (sessionStateData) {
              setSessionState(sessionStateData);
            }
          }
        },
      });
    } catch (err: any) {
      setError(err.message || "Failed to send message");
      setIsLoading(false);
    }
  };

  const requestHint = async (level: number) => {
    if (!sessionId || isLoading) return;

    setIsLoading(true);
    setError(null);

    // Add placeholder for assistant message
    const assistantMessage: MessageType = {
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      await sendMessageMutation.mutateAsync({
        sessionId,
        content: `Em cần gợi ý cấp độ ${level}`,
        hintRequested: true,
        token,
        onChunk: (content, done, sessionStateData) => {
          if (content) {
            setMessages((prev) => {
              const updated = [...prev];
              const lastMsg = updated[updated.length - 1];
              if (lastMsg && lastMsg.role === "assistant") {
                updated[updated.length - 1] = {
                  ...lastMsg,
                  content: lastMsg.content + content,
                };
              }
              return updated;
            });
          }
          if (done) {
            setIsLoading(false);
            if (sessionStateData) {
              setSessionState(sessionStateData);
            }
          }
        },
      });
    } catch (err: any) {
      setError(err.message || "Failed to request hint");
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getPhaseColor = (state: string) => {
    switch (state) {
      case "review":
        return "bg-blue-50 text-blue-600";
      case "heuristic":
        return "bg-purple-50 text-purple-600";
      case "rectify":
        return "bg-amber-50 text-amber-600";
      case "summarize":
        return "bg-green-50 text-green-600";
      default:
        return "bg-gray-50 text-gray-600";
    }
  };

  return (
    <div className="flex h-screen" style={{ maxWidth: "1200px" }}>
      {/* Chat Section */}
      <div className="flex-1 flex flex-col border-r border-line bg-surface">
        {/* Top Bar */}
        <div className="p-4 border-b border-line bg-surface flex items-center gap-3">
          <button className="w-8 h-8 rounded-lg border border-line-2 flex items-center justify-center hover:bg-surface-2">
            ←
          </button>
          <span className="text-xs font-medium px-3 py-1 rounded-full bg-surface-2 text-ink-2">
            {problem ? "Hình chóp" : "Đang tải..."}
          </span>
          {sessionState && (
            <span
              className={`text-xs font-semibold px-3 py-1 rounded-full ${
                sessionState.dialogue_state === 'review' ? 'bg-blue-50 text-blue-600' :
                sessionState.dialogue_state === 'heuristic' ? 'bg-purple-50 text-purple-600' :
                sessionState.dialogue_state === 'rectify' ? 'bg-amber-50 text-amber-600' :
                sessionState.dialogue_state === 'summarize' ? 'bg-green-50 text-green-600' :
                'bg-gray-50 text-gray-600'
              }`}
            >
              {sessionState.dialogue_state.toUpperCase()}
            </span>
          )}
          <div className="ml-auto font-mono text-xs text-ink-4">00:12:34</div>
        </div>

        {/* Problem Statement */}
        {problem && (
          <div className="p-4 border-b border-line bg-surface">
            <div className="text-[10px] font-medium uppercase tracking-wider text-ink-4 mb-2">
              Đề bài
            </div>
            <div className="text-sm text-ink leading-relaxed">
              {problem.statement_latex}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <Message key={idx} message={msg} />
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <LoadingDots />
            </div>
          )}
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-line bg-surface">
          {/* Hint Level Selector */}
          <div className="flex gap-2 mb-3">
            <span className="text-[10px] font-mono text-ink-4">Gợi ý:</span>
            {[0, 1, 2, 3].map((level) => (
              <button
                key={level}
                onClick={() => requestHint(level)}
                className={`text-[10px] px-3 py-1 rounded-full border transition-all ${
                  sessionState?.hint_level === level
                    ? "bg-amber-50 text-amber-600 border-amber-300 font-medium"
                    : "border-gray-200 text-gray-500 hover:border-amber-300 hover:text-amber-600"
                }`}
              >
                L{level}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="flex gap-2 items-end">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Nhập câu trả lời hoặc thắc mắc..."
              className="flex-1 border border-line-2 rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-brand-light bg-surface"
              rows={1}
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="w-10 h-10 rounded-lg bg-brand hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center text-white transition-colors"
            >
              →
            </button>
          </div>
        </div>
      </div>

      {/* Viewer Section - 3D Geometry */}
      <div className="w-[380px] flex flex-col bg-surface">
        <div className="p-4 border-b border-line bg-surface flex items-center gap-2">
          <span className="text-sm font-medium flex-1">
            Hình 3D -{" "}
            {problem?.geometry_params?.solid_type === "pyramid"
              ? "Hình chóp"
              : "Hình học"}
          </span>
          <button className="text-[10px] px-3 py-1 rounded-full border border-line-2 hover:bg-surface-2">
            Xoay
          </button>
          <button className="text-[10px] px-3 py-1 rounded-full border border-line-2 hover:bg-surface-2">
            Cắt ngang
          </button>
        </div>

        {/* 3D Canvas with GeometryViewer */}
        <div className="flex-1 relative">
          {problem?.is_geometry ? (
            <GeometryViewer
              solid_type={problem.geometry_params?.solid_type}
              params={problem.geometry_params?.params}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center p-4">
              <div className="text-center">
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-ink-4 mb-2 mx-auto">
                  <path d="M8 40L24 8l16 32"/>
                  <path d="M14 32h20"/>
                  <path d="M18 24h12"/>
                </svg>
                <p className="text-xs text-ink-4">Bài toán không có hình học</p>
              </div>
            </div>
          )}
        </div>

        {/* Info Panel */}
        <div className="p-4 border-t border-line space-y-3">
          <div className="bg-surface border border-line rounded-xl p-4">
            <div className="text-xs font-semibold mb-3 text-ink">
              Thông tin bài toán
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-ink-3">Loại</span>
                <span className="font-mono text-ink">Hình chóp</span>
              </div>
              <div className="flex justify-between">
                <span className="text-ink-3">Độ khó</span>
                <span className="font-mono text-ink">Dễ</span>
              </div>
            </div>
          </div>

          {/* Phase Progress */}
          <div className="bg-surface border border-line rounded-xl p-4">
            <div className="text-xs font-semibold mb-3 text-ink">
              Tiến trình Socratic
            </div>
            <div className="flex gap-0">
              {["REVIEW", "HEURISTIC", "RECTIFY", "SUMMARIZE"].map(
                (phase, idx) => (
                  <div
                    key={phase}
                    className="flex-1 text-center relative pb-2"
                  >
                    <div
                      className={`w-5 h-5 rounded-full mx-auto mb-1 flex items-center justify-center text-[10px] ${
                        sessionState?.dialogue_state.toUpperCase() === phase
                          ? "bg-blue-500 text-white"
                          : idx <
                            (sessionState
                              ? [
                                  "REVIEW",
                                  "HEURISTIC",
                                  "RECTIFY",
                                  "SUMMARIZE",
                                ].indexOf(
                                  sessionState.dialogue_state.toUpperCase()
                                )
                              : 0)
                          ? "bg-green-500 text-white"
                          : "bg-gray-200"
                      }`}
                    >
                      {idx <
                      (sessionState
                        ? [
                            "REVIEW",
                            "HEURISTIC",
                            "RECTIFY",
                            "SUMMARIZE",
                          ].indexOf(
                            sessionState.dialogue_state.toUpperCase()
                          )
                        : 0) ? (
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M2 6l3 3 5-5"/>
                        </svg>
                      ) : null}
                    </div>
                    <div className="text-[10px] text-ink-4">{phase}</div>
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
