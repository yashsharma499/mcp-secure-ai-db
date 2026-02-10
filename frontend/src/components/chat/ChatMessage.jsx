export default function ChatMessage({ role, content }) {
  const isUser = role === "user";

  return (
    <div
      className={`
        px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap break-words
        ${isUser 
          ? "bg-indigo-600 text-white rounded-tr-none shadow-lg shadow-indigo-600/10" 
          : "bg-white/5 border border-white/10 text-slate-200 rounded-tl-none shadow-xl"
        }
      `}
    >
      {content}
    </div>
  );
}