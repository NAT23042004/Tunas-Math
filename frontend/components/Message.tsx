interface MessageProps {
  message: {
    role: "user" | "assistant";
    content: string;
    timestamp: string;
  };
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold ${
          isUser
            ? "bg-blue-100 text-blue-600"
            : "bg-brand-light text-brand"
        }`}
      >
        {isUser ? "NK" : "AI"}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[78%] p-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-blue-600 text-white rounded-br-md"
            : "bg-surface-2 border border-line rounded-bl-md text-ink"
        }`}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        <div
          className={`text-[10px] mt-1 ${
            isUser ? "text-blue-200" : "text-ink-4"
          }`}
        >
          {new Date(message.timestamp).toLocaleTimeString("vi-VN", {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </div>
      </div>
    </div>
  );
}
