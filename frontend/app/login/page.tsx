export default function Login() {
  return (
    <main className="min-h-screen bg-bg flex items-center justify-center p-6">
      <div className="w-full max-w-[900px] bg-surface rounded-3xl overflow-hidden border border-line shadow-lg">
        {/* Left Side - Branding */}
        <div className="bg-ink p-16 flex flex-col justify-between relative overflow-hidden">
          {/* Background Circles */}
          <div className="absolute -top-15 -right-15 w-[260px] h-[260px] bg-brand rounded-full opacity-10"></div>
          <div className="absolute -bottom-10 -left-10 w-[180px] h-[180px] bg-brand rounded-full opacity-10"></div>

          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 bg-brand rounded-xl flex items-center justify-center">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M10 2L17 14H3L10 2Z" fill="white" fillOpacity="0.9"/>
                </svg>
              </div>
              <div className="font-display text-2xl font-bold text-white">
                Toán Socratic
                <div className="font-sans text-sm font-light opacity-50">Lớp 12</div>
              </div>
            </div>

            <div className="mb-8">
              <h2 className="font-display text-3xl font-bold text-white mb-4 leading-tight">
                Học Toán theo cách<br/><em className="not-italic text-brand-mid">bạn tự nghĩ ra</em>
              </h2>
              <p className="text-sm text-white/50 leading-relaxed">
                Không phải nhìn lời giải — mà là tự tìm ra đáp án với sự dẫn dắt thông minh.
                Phương pháp Socratic giúp bạn hiểu sâu, nhớ lâu hơn.
              </p>
            </div>

            <div className="space-y-3">
              {[
                "Đối thoại Socratic — AI hỏi, bạn khám phá",
                "Hình học 3D tương tác — xoay, cắt, khám phá",
                "Bám sát chương trình THPT Quốc gia 2025",
              ].map((feature, idx) => (
                <div key={idx} className="flex gap-3 items-start">
                  <div className="w-1.5 h-1.5 rounded-full bg-brand mt-1.5 flex-shrink-0"></div>
                  <div className="text-sm text-white/55">{feature}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="p-16">
          <h2 className="font-display text-2xl font-bold mb-2">Đăng nhập</h2>
          <p className="text-sm text-ink-3 mb-8">Chào mừng trở lại! Hãy tiếp tục học.</p>

          <button className="w-full flex items-center justify-center gap-3 p-3 border border-line-2 rounded-lg hover:shadow-sm transition-all">
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Tiếp tục với Google
          </button>

          <div className="flex items-center gap-3 my-5 text-ink-4 text-xs">
            <div className="flex-1 h-px bg-line"></div>
            <span>hoặc</span>
            <div className="flex-1 h-px bg-line"></div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-ink-2 mb-1">Email</label>
              <input
                type="email"
                placeholder="ten@email.com"
                defaultValue="khoa@example.com"
                className="w-full p-2.5 border border-line-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-light bg-surface"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-ink-2 mb-1">Mật khẩu</label>
              <input
                type="password"
                placeholder="••••••••"
                defaultValue="password"
                className="w-full p-2.5 border border-line-2 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-light bg-surface"
              />
            </div>
            <button
              className="w-full p-3 rounded-lg bg-brand text-white font-semibold text-sm hover:bg-brand-dark transition-colors"
              onClick={() => window.location.href = '/dashboard'}
            >
              Đăng nhập →
            </button>
          </div>

          <p className="text-center text-sm text-ink-3 mt-6">
            Chưa có tài khoản? <a href="#" className="text-brand font-medium">Đăng ký miễn phí</a>
          </p>
        </div>
      </div>
    </main>
  );
}
