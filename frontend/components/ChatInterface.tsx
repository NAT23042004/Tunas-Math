"use client";

import { useState, useRef, useEffect } from "react";
import { Message } from "./Message";
import { LoadingDots } from "./LoadingDots";

interface MessageType {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

interface SessionState {
  dialogue_state: string;
  hint_level: number;
  fail_count: number;
}

interface Problem {
  statement_latex: string;
  answer: string;
  is_geometry: boolean;
  geometry_params?: any;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionState, setSessionState] = useState<SessionState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [problem, setProblem] = useState<Problem | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await fetch("/api/sessions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: "00000000-0000-0000-0000-000000000001",
            topic_id: "hinh-hoc.hinh-chop",
            problem_id: null,
          }),
        });
        if (!response.ok) throw new Error("Failed to create session");
        const data = await response.json();
        setSessionId(data.id);
        setSessionState({
          dialogue_state: data.dialogue_state,
          hint_level: data.hint_level,
          fail_count: data.fail_count,
        });

        // Fetch a sample problem
        const problemResponse = await fetch("/api/problems?topic_id=hinh-hoc.hinh-chop&limit=1");
        if (problemResponse.ok) {
          const problems = await problemResponse.json();
          if (problems.length > 0) {
            setProblem(problems[0]);
          }
        }
      } catch (err) {
        setError("Failed to initialize session");
        console.error(err);
      }
    };
    initSession();
  }, []);

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

    try {
      const response = await fetch(`/api/sessions/${sessionId}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: input,
          hint_requested: false,
        }),
      });

      if (!response.ok) throw new Error("Failed to send message");

      const data = await response.json();

      const assistantMessage: MessageType = {
        role: "assistant",
        content: data.message.content,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setSessionState(data.session_state);
    } catch (err) {
      setError("Failed to send message");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const requestHint = async (level: number) => {
    if (!sessionId || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/sessions/${sessionId}/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: `Em cần gợi ý cấp độ ${level}`,
          hint_requested: true,
        }),
      });

      if (!response.ok) throw new Error("Failed to request hint");

      const data = await response.json();

      const assistantMessage: MessageType = {
        role: "assistant",
        content: data.message.content,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setSessionState(data.session_state);
    } catch (err) {
      setError("Failed to request hint");
      console.error(err);
    } finally {
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
      case "review": return "bg-brand-light text-brand";
      case "heuristic": return "bg-blue-light text-blue";
      case "rectify": return "bg-amber-light text-amber";
      case "summarize": return "bg-green-light text-green";
      default: return "bg-surface-2 text-ink-2";
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
            <span className={`text-xs font-semibold px-3 py-1 rounded-full ${getPhaseColor(sessionState.dialogue_state)}`}>
              {sessionState.dialogue_state.toUpperCase()}
            </span>
          )}
          <div className="ml-auto font-mono text-xs text-ink-4">
            00:12:34
          </div>
        </div>

        {/* Problem Statement */}
        {problem && (
          <div className="p-4 border-b border-line bg-bg">
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
                    ? "bg-amber-light text-amber border-amber font-medium"
                    : "border-line-2 text-ink-3 hover:border-amber hover:text-amber"
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
      <div className="w-[380px] flex flex-col bg-bg">
        <div className="p-4 border-b border-line bg-surface flex items-center gap-2">
          <span className="text-sm font-medium flex-1">Hình 3D - Hình chóp</span>
          <button className="text-[10px] px-3 py-1 rounded-full border border-line-2 hover:bg-surface-2">
            Xoay
          </button>
          <button className="text-[10px] px-3 py-1 rounded-full border border-line-2 hover:bg-surface-2">
            Cắt ngang
          </button>
        </div>

        {/* 3D Canvas Placeholder */}
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center">
            <div className="text-4xl mb-2">△</div>
            <p className="text-xs text-ink-4">
              {problem?.is_geometry ? "Hình 3D sẽ hiển thị ở đây" : "Bài toán không có hình học"}
            </p>
          </div>
        </div>

        {/* Info Panel */}
        <div className="p-4 border-t border-line space-y-3">
          <div className="bg-surface border border-line rounded-xl p-4">
            <div className="text-xs font-semibold mb-3 text-ink">Thông tin bài toán</div>
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
            <div className="text-xs font-semibold mb-3 text-ink">Tiến trình Socratic</div>
            <div className="flex gap-0">
              {["REVIEW", "HEURISTIC", "RECTIFY", "SUMMARIZE"].map((phase, idx) => (
                <div key={phase} className="flex-1 text-center relative pb-2">
                  <div className={`w-5 h-5 rounded-full mx-auto mb-1 flex items-center justify-center text-[10px] ${
                    sessionState?.dialogue_state.toUpperCase() === phase
                      ? "bg-blue text-white"
                      : idx < (sessionState ? ["REVIEW", "HEURISTIC", "RECTIFY", "SUMMARIZE"].indexOf(sessionState.dialogue_state.toUpperCase()) : 0)
                      ? "bg-green text-white"
                      : "bg-surface-3"
                  }`}>
                    {idx < (sessionState ? ["REVIEW", "HEURISTIC", "RECTIFY", "SUMMARIZE"].indexOf(sessionState.dialogue_state.toUpperCase()) : 0) ? "✓" : ""}
                  </div>
                  <div className="text-[10px] text-ink-4">{phase}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
