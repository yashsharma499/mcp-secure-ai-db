import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  ShieldCheck, 
  LogOut, 
  Zap, 
  Trash2
} from "lucide-react";
import useAuth from "../auth/useAuth";

export default function UserLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  const triggerClearChat = () => {
    window.dispatchEvent(new CustomEvent("mcp-clear-chat"));
  };

  const displayName =
    user?.name ||
    user?.full_name ||
    user?.email?.split("@")[0] ||
    "User";

  return (
    <div className="min-h-screen bg-[#0a0c10] flex flex-col font-sans selection:bg-indigo-500/30">
      <header className="h-16 bg-[#0a0c10]/80 backdrop-blur-xl border-b border-white/5 flex items-center justify-between px-6 md:px-10 z-50">
        <div className="flex items-center gap-6">
          <div
            className="flex items-center gap-2.5 cursor-pointer"
            onClick={() => navigate("/app")}
          >
            <div className="w-9 h-9 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Zap className="text-white w-5 h-5 fill-current" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-sm font-bold text-white tracking-tight leading-none">
                MCP GATEWAY
              </h1>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 md:gap-4">
          {location.pathname === "/app" && (
            <button
              onClick={triggerClearChat}
              className="flex items-center gap-2 px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 hover:text-red-400 transition-colors border border-white/5 hover:border-red-500/20 rounded-lg bg-white/5"
            >
              <Trash2 size={14} />
              <span className="hidden sm:inline">Clear Terminal</span>
            </button>
          )}

          <div className="h-8 w-px bg-white/10 hidden sm:block" />

          <div className="flex items-center gap-3">

            {/* USER NAME (instead of profile icon) */}
            <div className="flex flex-col items-end mr-1">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest leading-none mb-1">
                Operator
              </span>
              <span className="text-xs text-indigo-400 font-semibold leading-none">
                {displayName}
              </span>
            </div>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleLogout}
              className="p-2 rounded-xl bg-white/5 border border-white/10 text-slate-400 hover:text-red-400 hover:bg-red-400/10 transition-all"
            >
              <LogOut size={18} />
            </motion.button>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-hidden relative">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-indigo-600/5 blur-[120px] pointer-events-none rounded-full" />
        <Outlet />
      </main>

      <footer className="h-8 bg-[#0a0c10] border-t border-white/5 flex items-center justify-between px-6 text-[9px] font-mono text-slate-600 uppercase tracking-[0.2em]">
        <div className="flex gap-4">
          <span className="flex items-center gap-1">
            <ShieldCheck size={10} className="text-emerald-500" /> Identity Verified
          </span>
        </div>
        <div className="animate-pulse">● Secure Link Established</div>
      </footer>
    </div>
  );
}
