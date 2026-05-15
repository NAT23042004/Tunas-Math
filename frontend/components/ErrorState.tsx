'use client';

interface ErrorStateProps {
  title?: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  fullHeight?: boolean;
}

export default function ErrorState({
  title = "Da xay ra su co",
  message,
  actionLabel,
  onAction,
  fullHeight = false,
}: ErrorStateProps) {
  return (
    <div className={`flex items-center justify-center p-6 ${fullHeight ? "min-h-[40vh]" : "min-h-[24rem]"}`}>
      <div className="w-full max-w-xl rounded-3xl border border-red-200 bg-red-50 p-8 text-center shadow-sm">
        <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-red-100 text-lg font-semibold text-red-700">
          !
        </div>
        <h2 className="mt-4 text-lg font-semibold text-red-900">{title}</h2>
        <p className="mt-2 text-sm text-red-700">{message}</p>
        {actionLabel && onAction ? (
          <button
            type="button"
            onClick={onAction}
            className="mt-5 rounded-full bg-red-700 px-4 py-2 text-sm font-medium text-white hover:bg-red-800"
          >
            {actionLabel}
          </button>
        ) : null}
      </div>
    </div>
  );
}
