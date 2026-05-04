import Link from "next/link";

const topics = [
  {
    id: 1,
    name: "Giải tích",
    icon: "∫",
    mastery: 72,
    color: "green",
    chapters: "5 chương · 42 bài tập",
    desc: "Đạo hàm, tích phân",
    has3D: false,
  },
  {
    id: 2,
    name: "Hình học không gian",
    icon: "△",
    mastery: 38,
    color: "brand",
    chapters: "4 chương · 38 bài tập",
    desc: "Hình chóp, lăng trụ, cầu",
    has3D: true,
    weak: true,
  },
  {
    id: 3,
    name: "Xác suất & Thống kê",
    icon: "P",
    mastery: 55,
    color: "blue",
    chapters: "3 chương · 28 bài tập",
    desc: "Tổ hợp, xác suất",
    has3D: false,
  },
  {
    id: 4,
    name: "Hàm số & Đại số",
    icon: "f(x)",
    mastery: 81,
    color: "green",
    chapters: "4 chương · 36 bài tập",
    desc: "Đồ thị, phương trình",
    has3D: false,
  },
  {
    id: 5,
    name: "Lượng giác",
    icon: "sin",
    mastery: 44,
    color: "amber",
    chapters: "3 chương · 24 bài tập",
    desc: "Hàm, phương trình",
    has3D: false,
  },
  {
    id: 6,
    name: "Số phức",
    icon: "ℂ",
    mastery: 0,
    color: "ink-3",
    chapters: "2 chương · 18 bài tập",
    desc: "Chưa bắt đầu",
    has3D: false,
    locked: true,
  },
];

export default function Topics() {
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

          {/* Search and Filters */}
          <div className="flex gap-3 items-center mb-8">
            <input
              type="text"
              placeholder="Tìm kiếm: hình chóp, tích phân, xác suất…"
              className="flex-1 px-4 py-3 border border-line-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-light bg-surface"
            />
            <button className="filter-chip active">Tất cả</button>
            <button className="filter-chip">Còn yếu</button>
            <button className="filter-chip">Có 3D</button>
            <button className="filter-chip">Khó</button>
          </div>

          {/* Topics Grid */}
          <div className="grid grid-cols-3 gap-4">
            {topics.map((topic) => (
              <div
                key={topic.id}
                className={`topic-card ${topic.weak ? 'weak' : ''} ${topic.locked ? 'opacity-55' : 'cursor-pointer hover:border-brand transition-colors'}`}
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
                  <span className="text-[10px]" style={{ color: topic.has3D ? 'var(--brand)' : 'var(--ink-3)' }}>
                    {topic.has3D ? '🔷 Có 3D' : 'Không có 3D'}
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
          </div>
        </div>
      </div>
    </main>
  );
}
