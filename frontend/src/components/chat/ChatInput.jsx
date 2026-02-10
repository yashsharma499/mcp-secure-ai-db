import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { Send, CornerDownLeft } from "lucide-react";

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  // Auto-resize logic remains but with smoother transition handling
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "0px";
    const scrollHeight = textarea.scrollHeight;
    textarea.style.height = `${scrollHeight}px`;
  }, [value]);

  const canSend = value.trim().length > 0 && !disabled;

  const submit = () => {
    if (!canSend) return;
    onSend(value.trim());
    setValue("");
  };

  const onKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  };

  return (
    <div className="relative flex items-end gap-3 p-2 bg-[#161922] transition-all">
      <div className="relative flex-1">
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          disabled={disabled}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask your data question..."
          className="w-full bg-transparent resize-none max-h-48 py-3 pl-4 pr-12 text-sm text-slate-200 placeholder:text-slate-600 outline-none custom-scrollbar"
        />
        
        {/* Subtle "Return" hint icon for desktop users */}
        <div className="absolute right-3 bottom-3 text-slate-700 pointer-events-none hidden md:block">
          <CornerDownLeft size={14} />
        </div>
      </div>

      <motion.button
        whileHover={{ scale: canSend ? 1.05 : 1 }}
        whileTap={{ scale: canSend ? 0.95 : 1 }}
        onClick={submit}
        disabled={!canSend}
        className={`
          flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-300
          ${canSend 
            ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/40" 
            : "bg-white/5 text-slate-600 border border-white/5"
          }
        `}
      >
        <Send size={18} className={canSend ? "animate-in fade-in zoom-in duration-300" : ""} />
      </motion.button>
    </div>
  );
}