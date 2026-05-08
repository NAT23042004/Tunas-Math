"use client";

import Link from "next/link";
import { useTopics } from "@/lib/useTopics";
import { LoadingDots } from "@/components/LoadingDots";

export default function Topics() {
  const { topics, isLoading, isError, error } = useTopics();

  if (isLoading) {
    return (
      <main className="min-h-screen">
        <div className="fixed left-0 top-0 h-screen w-[220px] bg-surface border-r border-line" />
        <div className="ml-[220px] p-8 flex items-center justify-center">
          <LoadingDots />
        </div>
      </main>
    );
  }

  if (isError) {
    return (
      <main className="min-h-screen">
        <div className="fixed left-0 top-0 h-screen w-[220px] bg-surface border-r border-line" />
        <div className="ml-[220px] p-8 flex items-center justify-center">
          <div className="text-red-600 text-sm">Lỗi tải dữ liệu: {error?.message}</div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-screen w-[220px] bg-surface border-r border-line flex flex-col">
        <div className="p-5 border-b border-line">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-brand rounded-lg flex items-center justify-center text-white text-sm font-bold">
              T
            </div>
            <div>
              <div className="font-display font-bold text-sm">Toán Socratic</div>
              <div className="text-[10px] text-ink-3">Lớp 12</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-3 flex flex-col gap-1">
          <div className="text-[10px] font-medium uppercase tracking-wider text-ink-4 mb-2 mt-2">
            Chính
          </div>
          <Link href="/dashboard" className="nav-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <rect x="1" y="1" width="6" height="6" rx="1.5"/>
              <rect x="9" y="1" width="6" height="6" rx="1.5"/>
              <rect x="1" y="9" width="6" height="6" rx="1.5"/>
              <rect x="9" y="9" width="6" height="6" rx="1.5"/>
            </svg>
            Tổng quan
          </Link>
          <Link href="/topics" className="nav-item active">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
              <rect x="2" y="2" width="12" height="12" rx="2"/>
              <path d="M2 6h12M6 2v12"/>
            </svg>
            Chủ đề
          </Link>
          <Link href="/session" className="nav-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
              <circle cx="8" cy="8" r="6"/>
              <path d="M8 5v3l2 2"/>
            </svg>
            Phiên học mới
          </Link>

          <div className="text-[10px] font-medium uppercase tracking-wider text-ink-4 mb-2 mt-8">
            Học tập
          </div>
          <a href="#" className="nav-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M8 1L2 5v8l6 2 6-2V5L8 1z"/>
            </svg>
            Lịch sử
          </a>
          <a href="#" className="nav-item">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5">
              <circle cx="8" cy="8" r="6"/>
              <path d="M8 5v3M8 11v.5"/>
            </svg>
            Tiến độ
          </a>
        </nav>

        <div className="p-4 border-t border-line flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-brand-light border-2 border-brand flex items-center justify-center text-xs font-bold text-brand">
            NK
          </div>
          <div>
            <div className="text-sm font-medium">Nguyễn Khoa</div>
            <div className="text-[11px] text-ink-3">Lớp 12A · THPT</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-[220px] p-8">
        <div className="max-w-5xl">
          <div className="mb-8">
            <h1 className="font-display text-3xl font-bold mb-2">Chủ đề</h1>
            <p className="text-ink-3">Chọn chủ đề để bắt đầu phiên Socratic. Ưu tiên chủ đề còn yếu.</p>
          </div>

          {/* Topics Grid */}
          <div className="grid grid-cols-3 gap-4">
            {topics.map((topic) => (
              <div
                key={topic.id}
                className={`topic-card ${topic.locked ? 'opacity-55' : 'cursor-pointer hover:border-brand transition-colors'}`}
                onClick={() => !topic.locked && (window.location.href = '/session')}
              >
                <div className="topic-card-accent" style={{ backgroundColor: `var(--${topic.color})` }}></div>
                <div className="topic-card-header">
                  <div className="topic-icon" style={{ backgroundColor: `var(--${topic.color}-light)` }}>
                    {topic.icon}
                  </div>
                  {topic.locked ? (
                    <span className="badge" style={{ background: 'var(--surface-2)', color: 'var(--ink-4)' }}>
                      Chưa bắt đầu
                    </span>
                  ) : topic.mastery >= 60 ? (
                    <span className="badge badge-green">Tốt</span>
                  ) : topic.mastery >= 40 ? (
                    <span className="badge badge-blue">Trung bình</span>
                  ) : (
                    <span className="badge badge-red">Cần luyện!</span>
                  )}
                </div>
                <div className="topic-name">{topic.name}</div>
                <div className="topic-chapters">{topic.chapters}</div>
                <div className="topic-mastery-row">
                  <div className="topic-mastery-track">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${topic.mastery}%`,
                        backgroundColor: `var(--${topic.color})`
                      }}
                    ></div>
                  </div>
                  <div className="topic-mastery-pct">{topic.mastery}%</div>
                </div>
                <div className="topic-footer">
                  <span className="text-[10px] flex items-center gap-1" style={{ color: topic.has3D ? 'var(--brand)' : 'var(--ink-3)' }}>
                    {topic.has3D ? (
                      <>
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                          <rect x="1" y="1" width="10" height="10" rx="1" stroke="currentColor" strokeWidth="1" fill="none"/>
                          <path d="M1 6h10" stroke="currentColor" strokeWidth="0.5"/>
                          <path d="M6 1v10" stroke="currentColor" strokeWidth="0.5"/>
                        </svg>
                        Có 3D
                      </>
                    ) : (
                      'Không có 3D'
                    )}
                  </span>
                  <button
                    className="topic-cta"
                    onClick={(e) => {
                      e.stopPropagation();
                      window.location.href = '/session';
                    }}
                  >
                    {topic.locked ? 'Bắt đầu →' : 'Học tiếp →'}
                  </button>
                </div>
              </div>
            ))}
            {topics.length === 0 && (
              <div className="col-span-3 text-center text-ink-3 text-sm py-8">
                Chưa có chủ đề nào. Hãy liên hệ quản trị viên.
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
