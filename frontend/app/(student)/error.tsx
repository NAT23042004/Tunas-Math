'use client';

import ErrorState from '@/components/ErrorState';

export default function StudentRouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <ErrorState
      title="Khong mo duoc khu hoc sinh"
      message={error.message || "Da xay ra loi khi tai giao dien hoc tap."}
      actionLabel="Thu lai"
      onAction={reset}
      fullHeight
    />
  );
}
