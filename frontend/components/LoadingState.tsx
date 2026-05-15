interface LoadingStateProps {
  title?: string;
  message?: string;
  fullHeight?: boolean;
}

export default function LoadingState({
  title = "Dang tai du lieu",
  message = "He thong dang chuan bi noi dung cho ban.",
  fullHeight = false,
}: LoadingStateProps) {
  return (
    <div className={`flex items-center justify-center p-6 ${fullHeight ? "min-h-[40vh]" : "min-h-[24rem]"}`}>
      <div className="w-full max-w-xl rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-slate-900" />
        <h2 className="mt-4 text-lg font-semibold text-slate-900">{title}</h2>
        <p className="mt-2 text-sm text-slate-500">{message}</p>
      </div>
    </div>
  );
}
