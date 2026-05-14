'use client';

import { useQuery } from '@tanstack/react-query';
import { getAdminStats } from '@/lib/api';

export default function AdminDashboardPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: getAdminStats,
  });

  if (isLoading) return <div className="p-8">Dang tai...</div>;
  if (error) return <div className="p-8 text-red-600">Khong the tai thong ke quan tri.</div>;
  if (!data) return <div className="p-8">Khong co du lieu.</div>;

  return (
    <div className="space-y-6 p-4 md:p-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Admin dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">Theo doi nguoi dung, phien hoc va cac chu de dang can can thiep.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="Tong nguoi dung" value={data.total_users} />
        <StatCard label="Hoc sinh hoat dong" value={data.active_students} />
        <StatCard label="Tong phien hoc" value={data.total_sessions} />
        <StatCard label="Phien hoan thanh" value={data.completed_sessions} />
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-sm text-slate-500">Phien hinh hoc</div>
          <div className="mt-3 text-4xl font-semibold text-slate-900">{data.geometry_sessions}</div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Chu de mastery thap</h2>
          <div className="mt-4 space-y-3">
            {data.lowest_mastery_topics.map((topic) => (
              <div key={topic.topic_id} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                <span className="text-sm font-medium text-slate-700">{topic.topic_id}</span>
                <span className="text-sm text-slate-500">{Math.round(topic.mastery_score * 100)}%</span>
              </div>
            ))}
            {data.lowest_mastery_topics.length === 0 && (
              <div className="text-sm text-slate-500">Chua co du lieu mastery.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="text-sm text-slate-500">{label}</div>
      <div className="mt-3 text-4xl font-semibold text-slate-900">{value}</div>
    </div>
  );
}
