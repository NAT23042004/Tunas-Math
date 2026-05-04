export function LoadingDots() {
  return (
    <div className="flex gap-1 p-3">
      <div className="w-2 h-2 bg-ink-4 rounded-full animate-bounce" style={{ animationDelay: "0s" }}></div>
      <div className="w-2 h-2 bg-ink-4 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
      <div className="w-2 h-2 bg-ink-4 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
    </div>
  );
}
