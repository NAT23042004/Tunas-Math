"use client";

import Link from "next/link";
import { useDashboardData } from "@/lib/useDashboard";
import { useSession } from "next-auth/react";
import { LoadingDots } from "@/components/LoadingDots";

const TOPIC_META: Record<string, { name: string; icon: string; color: string }> = {
  "giai-tich": { name: "Giải tích", icon: "∫", color: "green" },
  "hinh-hoc-khong-gian": { name: "Hình học KG", icon: "△", color: "brand" },
  "xac-suat-thong-ke": { name: "Xác suất", icon: "P", color: "blue" },
  "ham-so-dai-so": { name: "Hàm số & Đại số", icon: "f(x)", color: "green" },
  "luong-giac": { name: "Lượng giác", icon: "sin", color: "amber" },
  "so-phuc": { name: "Số phức", icon: "ℂ", color: "ink-3" },
};

export default function Dashboard() {
  const { data: session } = useSession();
  const { masteryMap, progress, problems, isLoading, isError, error } = useDashboardData();

  if (isLoading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <LoadingDots />
      </main>
    );
  }

  if (isError) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="text-red-600 text-sm">Lỗi tải dữ liệu: {error?.message}</div>
      </main>
    );
  }

  const userName = session?.user?.name?.split(" ").pop() || "bạn";
  const streak = masteryMap?.streak_days || 0;
  const sessionsThisWeek = masteryMap?.sessions_this_week || 0;
  // Build topics from progress data
  const topics = progress?.map((p) => {
    const meta = TOPIC_META[p.topic_id] || { name: p.topic_id, icon: "?", color: "ink-3" };
    return {
      id: p.topic_id,
      name: meta.name,
      icon: meta.icon,
      mastery: Math.round(p.mastery_score * 100),
      color: meta.color,
      sessionsCount: p.sessions_count,
      lastPracticed: p.last_practiced,
    };
  }) || [];

  const recentSessions = problems?.slice(0, 4).map((p) => ({
    title: p.statement_latex?.substring(0, 50) + "..." || "Bài tập",
    time: "Gần đây",
    status: "success" as const,
  })) || [];

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
          <Link href="/dashboard" className="nav-item active">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <rect x="1" y="1" width="6" height="6" rx="1.5"/>
              <rect x="9" y="1" width="6" height="6" rx="1.5"/>
              <rect x="1" y="9" width="6" height="6" rx="1.5"/>
              <rect x="9" y="9" width="6" height="6" rx="1.5"/>
            </svg>
            Tổng quan
          </Link>
          <Link href="/topics" className="nav-item">
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

          <div className="text-[10px] font-medium uppercase tracking-wider text-ink-4 mb-2 mt-6">
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
            {session?.user?.name?.split(" ").map(w => w[0]).join("") || "NK"}
          </div>
          <div>
            <div className="text-sm font-medium">{session?.user?.name || "Người dùng"}</div>
            <div className="text-[11px] text-ink-3">Lớp 12A · THPT</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-[220px] p-8">
        <div className="max-w-5xl">
          <div className="mb-8">
            <h1 className="font-display text-3xl font-bold mb-2 flex items-center gap-2">
              Chào buổi tối, {userName}
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
            </h1>
            <p className="text-ink-3">
              Hôm nay bạn đã học {masteryMap?.sessions_this_week ? 0 : 0} phút. Hãy bắt đầu một phiên mới!
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-surface border border-line rounded-2xl p-5">
              <div className="text-[11px] text-ink-3 mb-1">Streak</div>
              <div className="text-3xl font-bold text-green-600 flex items-center gap-1">
                {streak}
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" className="text-orange-500">
                  <path d="M12 2c.5 0 1 .2 1.4 .6L17 6h4a2 2 0 0 1 2 2v1a2 2 0 0 1-1.1 1.8L18 13.5V19a2 2 0 0 1-2 2h-1.5l-1.2 1.5a1 1 0 0 1-1.6-.8L12 19h-1a2 2 0 0 1-2-2v-5.5L4.1 10.8A2 2 0 0 1 3 9V8a2 2 0 0 1 2-2h4l3.6-3.4c.4-.4 .9-.6 1.4-.6z"/>
                </svg>
              </div>
              <div className="text-[11px] text-ink-4 mt-1">ngày liên tiếp</div>
            </div>
            <div className="bg-surface border border-line rounded-2xl p-5">
              <div className="text-[11px] text-ink-3 mb-1">Phiên học tuần này</div>
              <div className="text-3xl font-bold">{sessionsThisWeek}</div>
              <div className="text-[11px] text-green-600 mt-1">tuần này</div>
            </div>
            <div className="bg-surface border border-line rounded-2xl p-5">
              <div className="text-[11px] text-ink-3 mb-1">Chủ đề nắm chắc</div>
              <div className="text-3xl font-bold">
                {topics.filter(t => t.mastery >= 60).length}<span className="text-base text-ink-4">/{topics.length}</span>
              </div>
              <div className="text-[11px] text-ink-4 mt-1">
                cần luyện thêm {topics.filter(t => t.mastery < 60).length}
              </div>
            </div>
            <div
              className="bg-brand text-white rounded-2xl p-5 cursor-pointer hover:bg-brand-dark transition-colors"
              onClick={() => window.location.href = '/session'}
            >
              <div className="text-[11px] opacity-80 mb-1">Bắt đầu học</div>
              <div className="text-base font-semibold">Phiên mới →</div>
            </div>
          </div>

          {/* Mastery Section */}
          <div className="grid grid-cols-3 gap-6">
            <div className="col-span-2">
              <div className="bg-surface border border-line rounded-2xl p-6 mb-6">
                <h2 className="text-lg font-semibold mb-4">Mức độ nắm chắc theo chủ đề</h2>
                <div className="space-y-3">
                  {topics.map((topic, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-3 hover:bg-surface-2 rounded-lg cursor-pointer transition-colors">
                      <div className={`w-9 h-9 rounded-lg bg-${topic.color}-light flex items-center justify-center text-sm text-${topic.color}-600`}>
                        {topic.icon}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium">{topic.name}</div>
                      </div>
                      <div className="w-24">
                        <div className="h-1.5 bg-surface-3 rounded-full overflow-hidden">
                          <div className={`h-full bg-${topic.color}-500 rounded-full`} style={{ width: `${topic.mastery}%` }}></div>
                        </div>
                      </div>
                      <div className={`text-sm min-w-[32px] text-right ${topic.mastery >= 60 ? 'text-green-600' : topic.mastery >= 40 ? 'text-amber-600' : 'text-red-600'}`}>{topic.mastery}%</div>
                      <span className={`badge ${topic.mastery >= 60 ? 'badge-green' : topic.mastery >= 40 ? 'badge-amber' : 'badge-red'}`}>
                        {topic.mastery >= 60 ? 'Tốt' : topic.mastery >= 40 ? 'Trung bình' : 'Yếu!'}
                      </span>
                    </div>
                  ))}
                  {topics.length === 0 && (
                    <div className="text-center text-ink-3 text-sm py-8">Chưa có dữ liệu tiến độ. Hãy bắt đầu học!</div>
                  )}
                </div>
              </div>

              {/* Recent Sessions */}
              <div className="bg-surface border border-line rounded-2xl p-6">
                <h2 className="text-lg font-semibold mb-4">Phiên học gần đây</h2>
                <div className="space-y-4">
                  {recentSessions.map((session, idx) => (
                    <div key={idx} className="flex items-center gap-3 pb-4 border-b border-line last:border-0">
                      <div className="w-9 h-9 rounded-lg bg-surface-2 flex items-center justify-center text-sm">
                        {session.title[0]}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium">{session.title}</div>
                        <div className="text-[12px] text-ink-3">{session.time}</div>
                      </div>
                      <span className={`badge ${session.status === 'success' ? 'badge-green' : 'badge-amber'}`}>
                        {session.status === 'success' ? (
                          <span className="flex items-center gap-1">
                            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                              <path d="M10 3L4.5 8.5 2 6" stroke="currentColor" strokeWidth="2" fill="none"/>
                            </svg>
                            Hoàn thành
                          </span>
                        ) : (
                          <span className="flex items-center gap-1">
                            <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
                              <path d="M6 2v4M6 8v.5" stroke="currentColor" strokeWidth="1.5" fill="none"/>
                            </svg>
                            Bỏ dở
                          </span>
                        )}
                      </span>
                    </div>
                  ))}
                  {recentSessions.length === 0 && (
                    <div className="text-center text-ink-3 text-sm py-8">Chưa có phiên học nào. Hãy bắt đầu!</div>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column - Suggestions */}
            <div>
              <div className="bg-surface border border-line rounded-2xl p-6 mb-6">
                <h3 className="text-base font-semibold mb-2">Gợi ý tiếp theo</h3>
                <div className="text-[11px] text-ink-4 mb-4">Dựa trên điểm yếu của bạn</div>

                <div className="space-y-3">
                  {topics.filter(t => t.mastery < 60).slice(0, 3).map((topic, idx) => {
                    const colors = ["brand", "amber", "blue"];
                    return (
                      <div key={idx} className="border border-line rounded-lg p-4 cursor-pointer hover:border-brand transition-colors">
                        <div className={`w-1 h-6 rounded`} style={{ backgroundColor: `var(--${colors[idx] || 'brand'})` }}></div>
                        <div className="text-[11px] font-medium mb-1" style={{ color: `var(--${colors[idx] || 'brand'})` }}>{topic.name}</div>
                        <div className="text-sm font-medium mb-1">{topic.name}</div>
                        <div className="text-[12px] text-ink-3 leading-relaxed">
                          Mức độ nắm chắc: {topic.mastery}% - Cần luyện thêm
                        </div>
                      </div>
                    );
                  })}
                  {topics.filter(t => t.mastery < 60).length === 0 && (
                    <div className="text-center text-ink-3 text-sm py-4">Tất cả chủ đề đều đạt mức tốt!</div>
                  )}
                </div>
              </div>

              <div className="bg-brand-light border border-brand-mid rounded-2xl p-6">
                <div className="text-sm font-semibold mb-2">Mẹo học hôm nay</div>
                <div className="text-sm text-ink leading-relaxed border-l-4 border-brand pl-3 italic">
                  "Khi gặp bài hình học không gian, hãy vẽ hình trước khi tính. Một hình vẽ tốt giải quyết 50% bài toán."
                </div>
                <div className="text-[11px] text-ink-4 mt-2">— Phương pháp Socratic</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
