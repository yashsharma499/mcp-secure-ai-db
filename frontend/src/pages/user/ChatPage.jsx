import { useCallback, useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Database, User as UserIcon, Sparkles, ShieldCheck } from "lucide-react";
import { sendChatMessage, fetchMyPermissions } from "../../api/agent.api";
import ChatInput from "../../components/chat/ChatInput";
import ChatMessage from "../../components/chat/ChatMessage";
import ResultTable from "../../components/chat/ResultTable";
import useAuth from "../../auth/useAuth";

export default function ChatPage() {
  const { user } = useAuth();
  const userId = user?.id;

  const scrollRef = useRef(null);

  const STORAGE_KEY_MESSAGES = userId ? `mcp_chat_messages_${userId}` : null;

  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  
  const [showPermissions, setShowPermissions] = useState(true);
  const [permissions, setPermissions] = useState([]);
  const [loadingPermissions, setLoadingPermissions] = useState(false);
  

  const handleClearChat = useCallback(() => {
    if (!STORAGE_KEY_MESSAGES) return;
    localStorage.removeItem(STORAGE_KEY_MESSAGES);
    setMessages([]);
  }, [STORAGE_KEY_MESSAGES]);

  useEffect(() => {
    window.addEventListener("mcp-clear-chat", handleClearChat);
    return () =>
      window.removeEventListener("mcp-clear-chat", handleClearChat);
  }, [handleClearChat]);

  useEffect(() => {
    if (scrollRef.current)
      scrollRef.current.scrollTop =
        scrollRef.current.scrollHeight;
  }, [messages, loading]);

  useEffect(() => {
    if (!STORAGE_KEY_MESSAGES) return;
    const saved = localStorage.getItem(STORAGE_KEY_MESSAGES);
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch {
        setMessages([]);
      }
    }
    setHydrated(true);
  }, [STORAGE_KEY_MESSAGES]);

  useEffect(() => {
    if (!hydrated || !STORAGE_KEY_MESSAGES) return;
    localStorage.setItem(
      STORAGE_KEY_MESSAGES,
      JSON.stringify(messages)
    );
  }, [messages, hydrated, STORAGE_KEY_MESSAGES]);

  const loadMyPermissions = useCallback(async () => {
    if (!userId) return;

    setLoadingPermissions(true);

    try {
      const data = await fetchMyPermissions();
      setPermissions(Array.isArray(data) ? data : []);
    } catch {
      setPermissions([]);
    } finally {
      setLoadingPermissions(false);
    }
  }, [userId]);
  

  useEffect(() => {
    if (showPermissions) loadMyPermissions();
  }, [showPermissions, loadMyPermissions]);

  const handleSend = useCallback(
    async (text) => {
      if (!text?.trim() || !userId) return;

      const userMsg = {
        id: crypto.randomUUID(),
        role: "user",
        content: text.trim()
      };

      setMessages((m) => [...m, userMsg]);
      setLoading(true);

      try {
        const res = await sendChatMessage({
          message: text.trim(),
          user_id: userId
        });

        setMessages((m) => [
          ...m,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: res?.text || "Request processed.",
            data: res?.data || null
          }
        ]);
      } catch (err) {
        const msg =
          err?.response?.data?.detail ||
          err?.response?.data?.message ||
          err?.message ||
          "Request failed";

        setMessages((m) => [
          ...m,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: msg
          }
        ]);
      } finally {
        setLoading(false);
      }
    },
    [userId]
  );

  return (
    <div className="h-full w-full bg-[#0a0c10] overflow-hidden">
      <div className="flex h-full w-full">

        
        <AnimatePresence>
          {showPermissions && (
            <motion.aside
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -20, opacity: 0 }}
              className="w-[280px] min-w-[280px] border-r border-white/5 bg-[#0d111b] p-4"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                  <ShieldCheck size={14} />
                  My access
                </h3>
              </div>

              {loadingPermissions ? (
                <p className="text-xs text-slate-400">
                  Loading permissions…
                </p>
              ) : permissions.length === 0 ? (
                <p className="text-xs text-slate-400">
                  No permissions assigned.
                </p>
              ) : (
                <div className="space-y-3">
                  {permissions.map((p) => (
                    <div
                      key={p.id || p.table_name}
                      className="p-3 rounded-xl bg-white/5 border border-white/10"
                    >
                      <div className="text-sm font-medium text-white">
                        {p.table_name}
                      </div>

                      <div className="mt-1 text-[11px] text-slate-400 flex gap-3">
                        <span>
                          R: {p.can_read ? "Yes" : "No"}
                        </span>
                        <span>
                          W: {p.can_write ? "Yes" : "No"}
                        </span>
                      </div>

                      {Array.isArray(p.allowed_columns) &&
                        p.allowed_columns.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1">
                            {p.allowed_columns.map((c) => (
                              <span
                                key={c}
                                className="text-[10px] px-1.5 py-0.5 rounded bg-white/10 text-slate-300"
                              >
                                {c}
                              </span>
                            ))}
                          </div>
                        )}
                    </div>
                  ))}
                </div>
              )}
            </motion.aside>
          )}
        </AnimatePresence>
       

        
        <div className="flex-1 flex justify-center overflow-hidden">
          <div className="relative flex flex-col w-full max-w-5xl h-full bg-[#111623] border-l border-r border-white/5">

            
            <div className="flex justify-end px-6 pt-4">
              <button
                onClick={() => setShowPermissions((v) => !v)}
                className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-slate-300 hover:bg-white/10"
              >
                <ShieldCheck size={14} />
                {showPermissions ? "Hide permissions" : "Show permissions"}
              </button>
            </div>
           

            <div
              ref={scrollRef}
              className="flex-1 overflow-y-auto pt-4 pb-36 scroll-smooth custom-scrollbar"
            >
              <div className="px-6 space-y-8">
                <AnimatePresence initial={false}>
                  {messages.length === 0 && !loading && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex flex-col items-center justify-center py-20 text-center space-y-4"
                    >
                      <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center border border-white/10">
                        <Database className="text-slate-400" />
                      </div>
                      <h2 className="text-lg font-semibold text-white">
                        System Ready. Awaiting Query...
                      </h2>
                    </motion.div>
                  )}

                  {messages.map((m) => (
                    <motion.div
                      key={m.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`flex gap-4 ${
                        m.role === "user" ? "flex-row-reverse" : ""
                      }`}
                    >
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${
                          m.role === "user"
                            ? "bg-slate-800 border-white/10"
                            : "bg-indigo-500/20 border-indigo-400/30"
                        }`}
                      >
                        {m.role === "user" ? (
                          <UserIcon size={14} />
                        ) : (
                          <Sparkles
                            size={14}
                            className="text-indigo-400"
                          />
                        )}
                      </div>

                      <div
                        className={`flex flex-col max-w-[85%] space-y-3 ${
                          m.role === "user" ? "items-end" : ""
                        }`}
                      >
                        <ChatMessage
                          role={m.role}
                          content={m.content}
                        />

                        {m.role === "assistant" &&
                          Array.isArray(m.data) &&
                          m.data.length > 0 && (
                            <div className="w-full bg-[#0d111b] border border-white/10 rounded-2xl overflow-hidden mt-2 shadow-2xl">
                              <ResultTable data={m.data} />
                            </div>
                          )}
                      </div>
                    </motion.div>
                  ))}

                  {loading && (
                    <motion.div
                      key="agent-thinking"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex gap-4"
                    >
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border bg-indigo-500/20 border-indigo-400/30">
                        <Sparkles
                          size={14}
                          className="text-indigo-400"
                        />
                      </div>

                      <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-white/5 border border-white/10 text-sm text-slate-400">
                        <span>Agent is thinking</span>
                        <span className="flex gap-1">
                          <span className="w-1 h-1 bg-slate-400 rounded-full animate-bounce [animation-delay:0ms]" />
                          <span className="w-1 h-1 bg-slate-400 rounded-full animate-bounce [animation-delay:150ms]" />
                          <span className="w-1 h-1 bg-slate-400 rounded-full animate-bounce [animation-delay:300ms]" />
                        </span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>

            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#111623] via-[#111623] to-transparent pt-12 pb-8 px-6">
              <div className="relative">
                <div className="absolute -inset-1 bg-indigo-500 rounded-2xl blur opacity-10 transition" />
                <div className="relative bg-[#1a2030] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                  <ChatInput
                    onSend={handleSend}
                    disabled={loading}
                  />
                </div>
              </div>
            </div>

          </div>
        </div>
        
      </div>
    </div>
  );
}
