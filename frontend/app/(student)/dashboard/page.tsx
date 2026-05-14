'use client';

import Link from 'next/link';
import MasteryRadar from '@/components/MasteryRadar';
import { useDashboard } from '@/lib/useDashboard';

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard();

  if (isLoading) return <div className="p-8">Đang tải...</div>;
  if (error) return <div className="p-8 text-red-600">Lỗi: {error.message}</div>;
  if (!data) return <div className="p-8">Không có dữ liệu</div>;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <Link
          href="/session/new"
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Bắt đầu phiên học
        </Link>
      </div>
      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border p-4">
          <h2 className="text-lg font-medium">Thành thạo theo chủ đề</h2>
          <div className="mt-4 h-80">
            <MasteryRadar data={data} />
          </div>
        </div>
        <div className="rounded-lg border p-4">
          <h2 className="text-lg font-medium">Hoạt động tuần này</h2>
          <p className="mt-4 text-3xl font-bold">{data.sessions_this_week}</p>
          <p className="text-sm text-gray-500">phiên học</p>
        </div>
        <div className="rounded-lg border p-4">
          <h2 className="text-lg font-medium">Chuỗi ngày học</h2>
          <p className="mt-4 text-3xl font-bold">{data.streak_days}</p>
          <p className="text-sm text-gray-500">ngày liên tiếp</p>
        </div>
      </div>
    </div>
  );
}
