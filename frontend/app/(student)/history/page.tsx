'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { getSessions } from '@/lib/api';

export default function HistoryPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['sessions'],
    queryFn: getSessions,
  });

  if (isLoading) return <div className="p-8">Dang tai...</div>;
  if (error) return <div className="p-8 text-red-600">Loi khi tai lich su hoc tap.</div>;

  return (
    <div className="space-y-6 p-4 md:p-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Lich su hoc tap</h1>
        <p className="mt-1 text-sm text-slate-500">Xem lai cac phien hoc, trang thai va tien do theo tung chu de.</p>
      </div>

      <div className="space-y-3">
        {data?.map((session) => (
          <Link
            key={session.id}
            href={`/session/${session.id}`}
            className="block rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow"
          >
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-sm uppercase tracking-wide text-slate-400">{session.topic_id}</div>
                <div className="mt-2 text-lg font-semibold text-slate-900">{session.summary || 'Phien dang tien hanh'}</div>
                <div className="mt-2 text-sm text-slate-500">
                  Bat dau: {new Date(session.started_at).toLocaleString()}
                </div>
              </div>
              <div className="text-sm text-slate-600">
                <div>Trang thai: {session.status}</div>
                <div>Hoi thoai: {session.dialogue_state}</div>
                <div>Danh gia: {session.student_rating ?? '-'}</div>
              </div>
            </div>
          </Link>
        ))}

        {data?.length === 0 && (
          <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-slate-500">
            Chua co phien hoc nao. Hay bat dau mot phien moi.
          </div>
        )}
      </div>
    </div>
  );
}
