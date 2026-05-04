import Link from "next/link";

export default function Dashboard() {
  return (
    <main className="min-h-screen bg-bg">
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
          <Link href="/" className="nav-item active">
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
            <h1 className="font-display text-3xl font-bold mb-2">Chào buổi tối, Khoa 👋</h1>
            <p className="text-ink-3">Hôm nay bạn đã học 0 phút. Hãy bắt đầu một phiên mới!</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-surface border border-line rounded-2xl p-5">
              <div className="text-[11px] text-ink-3 mb-1">Streak</div>
              <div className="text-3xl font-bold text-green-600">5 🔥</div>
              <div className="text-[11px] text-ink-4 mt-1">ngày liên tiếp</div>
            </div>
            <div className="bg-surface border border-line rounded-2xl p-5">
              <div className="text-[11px] text-ink-3 mb-1">Phiên học tuần này</div>
              <div className="text-3xl font-bold">7</div>
              <div className="text-[11px] text-green-600 mt-1">+2 so với tuần trước</div>
            </div>
            <div className="bg-surface border border-line rounded-2xl p-5">
              <div className="text-[11px] text-ink-3 mb-1">Chủ đề nắm chắc</div>
              <div className="text-3xl font-bold">3<span className="text-base text-ink-4">/8</span></div>
              <div className="text-[11px] text-ink-4 mt-1">cần luyện thêm 5</div>
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
                  {[
                    { name: "Giải tích", mastery: 72, color: "bg-green-500", textColor: "text-green-600" },
                    { name: "Hình học KG", mastery: 38, color: "bg-red-500", textColor: "text-red-600" },
                    { name: "Xác suất", mastery: 55, color: "bg-blue-500", textColor: "text-blue-600" },
                    { name: "Hàm số & Đại số", mastery: 81, color: "bg-green-500", textColor: "text-green-600" },
                    { name: "Lượng giác", mastery: 44, color: "bg-amber-500", textColor: "text-amber-600" },
                  ].map((topic, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-3 hover:bg-surface-2 rounded-lg cursor-pointer transition-colors">
                      <div className={`w-9 h-9 rounded-lg bg-${topic.color} bg-opacity-10 flex items-center justify-center text-sm ${topic.textColor}`}>
                        {topic.name[0]}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium">{topic.name}</div>
                      </div>
                      <div className="w-24">
                        <div className="h-1.5 bg-surface-3 rounded-full overflow-hidden">
                          <div className={`h-full ${topic.color} rounded-full`} style={{ width: `${topic.mastery}%` }}></div>
                        </div>
                      </div>
                      <div className={`text-sm min-w-[32px] text-right ${topic.textColor}`}>{topic.mastery}%</div>
                      <span className={`badge ${topic.mastery >= 60 ? 'badge-green' : topic.mastery >= 40 ? 'badge-amber' : 'badge-red'}`}>
                        {topic.mastery >= 60 ? 'Tốt' : topic.mastery >= 40 ? 'Trung bình' : 'Yếu!'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Sessions */}
              <div className="bg-surface border border-line rounded-2xl p-6">
                <h2 className="text-lg font-semibold mb-4">Phiên học gần đây</h2>
                <div className="space-y-4">
                  {[
                    { title: "Hình chóp - Thể tích & đường cao", time: "Hôm nay · 18 phút · 2 gợi ý", status: "success" },
                    { title: "Tích phân - Diện tích hình phẳng", time: "Hôm qua · 24 phút · 0 gợi ý", status: "success" },
                    { title: "Lượng giác - Phương trình lượng giác", time: "2 ngày trước · 11 phút · 3 gợi ý", status: "warning" },
                    { title: "Xác suất - Tổ hợp chỉnh hợp", time: "3 ngày trước · 20 phút · 1 gợi ý", status: "success" },
                  ].map((session, idx) => (
                    <div key={idx} className="flex items-center gap-3 pb-4 border-b border-line last:border-0">
                      <div className="w-9 h-9 rounded-lg bg-surface-2 flex items-center justify-center text-sm">
                        {session.title[0]}
                      </div>
                      <div className="flex-1">
                        <div className="text-sm font-medium">{session.title}</div>
                        <div className="text-[12px] text-ink-3">{session.time}</div>
                      </div>
                      <span className={`badge ${session.status === 'success' ? 'badge-green' : 'badge-amber'}`}>
                        {session.status === 'success' ? '✓ Hoàn thành' : '⚠ Bỏ dở'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column - Suggestions */}
            <div>
              <div className="bg-surface border border-line rounded-2xl p-6 mb-6">
                <h3 className="text-base font-semibold mb-2">Gợi ý tiếp theo</h3>
                <div className="text-[11px] text-ink-4 mb-4">Dựa trên điểm yếu của bạn</div>

                <div className="space-y-3">
                  {[
                    { priority: "brand", topic: "Hình học KG", title: "Đường thẳng vuông góc mặt phẳng", desc: "Bạn gặp lỗi ở bước này 3 lần tuần trước — hãy luyện thêm để nắm chắc." },
                    { priority: "amber", topic: "Lượng giác", title: "Phương trình lượng giác cơ bản", desc: "Chưa thực hành 5 ngày — nên ôn lại trước khi quên." },
                    { priority: "blue", topic: "Giải tích", title: "Bất phương trình hàm số", desc: "Bạn đã nắm 72% Giải tích — thử thách với bài khó hơn." },
                  ].map((item, idx) => (
                    <div key={idx} className="border border-line rounded-lg p-4 cursor-pointer hover:border-brand transition-colors">
                      <div className={`w-1 h-6 rounded`} style={{ backgroundColor: `var(--${item.priority})` }}></div>
                      <div className="text-[11px] font-medium mb-1" style={{ color: `var(--${item.priority})` }}>{item.topic}</div>
                      <div className="text-sm font-medium mb-1">{item.title}</div>
                      <div className="text-[12px] text-ink-3 leading-relaxed">{item.desc}</div>
                    </div>
                  ))}
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
