"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <div className="text-center space-y-4">
        <h2 className="text-2xl font-bold text-red-600">Something went wrong!</h2>
        <p className="text-ink-3">{error.message}</p>
        <button
          onClick={() => reset()}
          className="px-4 py-2 bg-brand text-white rounded-lg hover:bg-brand-dark"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
