'use client';

import ErrorState from '@/components/ErrorState';

export default function AdminRouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <ErrorState
      title="Khong mo duoc khu quan tri"
      message={error.message || "Da xay ra loi khi tai giao dien quan tri."}
      actionLabel="Thu lai"
      onAction={reset}
      fullHeight
    />
  );
}
