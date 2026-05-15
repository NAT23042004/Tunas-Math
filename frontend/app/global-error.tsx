'use client';

import ErrorState from '@/components/ErrorState';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="vi">
      <body>
        <ErrorState
          title="Ung dung dang tam thoi gian doan"
          message={error.message || "Da xay ra loi ngoai du kien trong luc tai ung dung."}
          actionLabel="Tai lai"
          onAction={reset}
          fullHeight
        />
      </body>
    </html>
  );
}
