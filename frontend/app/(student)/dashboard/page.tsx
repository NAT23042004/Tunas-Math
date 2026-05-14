'use client';

import Link from 'next/link';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import MasteryRadar from '@/components/MasteryRadar';
import { useDashboard } from '@/lib/useDashboard';

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) return <div className="p-8">Dang tai...</div>;
  if (error) return <div className="p-8 text-red-600">Loi: {error.message}</div>;
  if (!data) return <div className="p-8">Khong co du lieu</div>;

  return (
    <div className="space-y-6 p-4 md:p-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Bang tien do</h1>
          <p className="mt-1 text-sm text-slate-500">Theo doi muc thanh thao, tan suat hoc, va huong on tap tiep theo.</p>
        </div>
        <div className="flex gap-3">
          <Link
            href="/history"
            className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Lich su
          </Link>
          <Link
            href="/session/new"
            className="rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
          >
            Bat dau phien hoc
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-sm text-slate-500">Phien hoan thanh tuan nay</div>
          <div className="mt-3 text-4xl font-semibold text-slate-900">{data.sessions_this_week}</div>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-sm text-slate-500">Chuoi ngay hoc</div>
          <div className="mt-3 text-4xl font-semibold text-slate-900">{data.streak_days}</div>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-sm text-slate-500">Chu de nen uu tien</div>
          <div className="mt-3 text-sm text-slate-900">
            {data.suggested_topics.length > 0 ? data.suggested_topics.join(', ') : 'Chua co de xuat'}
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Thanh thao theo chu de</h2>
          <div className="mt-4 h-80">
            <MasteryRadar data={data} />
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Hoat dong 7 ngay</h2>
          <div className="mt-4 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.weekly_activity}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" tickFormatter={(value) => value.slice(5)} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="sessions" fill="#0f172a" radius={[10, 10, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
