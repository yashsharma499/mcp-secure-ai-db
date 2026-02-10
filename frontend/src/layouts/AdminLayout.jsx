import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  ShieldCheck, 
  Key, 
  Activity, 
  LogOut, 
  User as UserIcon,
  Menu,
  ChevronRight
} from "lucide-react";
import useAuth from "../auth/useAuth";

export default function AdminLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  const navItems = [
    { to: "/admin/permissions", label: "Access Matrix", icon: Key },
    { to: "/admin/audit", label: "Security Logs", icon: Activity },
  ];

  const linkClass = ({ isActive }) =>
    `group flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all duration-200 ${
      isActive
        ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/20"
        : "text-slate-400 hover:text-white hover:bg-white/5"
    }`;

  return (
    <div className="min-h-screen flex bg-[#0a0c10] text-slate-200 font-sans">
      
      <aside className="w-72 bg-[#0d0f14] border-r border-white/5 hidden md:flex flex-col sticky top-0 h-screen">
        
        <div className="h-20 flex items-center px-8 gap-3 border-b border-white/5">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-indigo-600/20">
            <ShieldCheck className="text-white w-5 h-5" />
          </div>
          <span className="text-white font-bold tracking-tight text-lg">MCP Admin</span>
        </div>

        
        <nav className="flex-1 p-6 space-y-2">
          <div className="text-[10px] font-bold text-slate-600 uppercase tracking-[0.2em] mb-4 ml-2">
            Management Protocol
          </div>
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={linkClass}>
              <item.icon size={18} className="transition-transform group-hover:scale-110" />
              <span className="flex-1">{item.label}</span>
              <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
            </NavLink>
          ))}
        </nav>

        
        <div className="p-6 border-t border-white/5 bg-black/20">
          <div className="flex items-center gap-3 px-2 mb-4">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-slate-800 to-slate-700 border border-white/10 flex items-center justify-center">
              <UserIcon size={20} className="text-slate-400" />
            </div>
            <div className="flex flex-col overflow-hidden">
              <span className="text-xs font-bold text-white truncate">
                {user?.email?.split('@')[0].toUpperCase()}
              </span>
              
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500 hover:text-white transition-all group"
          >
            <LogOut size={14} className="group-hover:-translate-x-1 transition-transform" />
            TERMINATE SESSION
          </button>
        </div>
      </aside>

      
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
       
        <header className="h-20 bg-[#0a0c10]/80 backdrop-blur-md border-b border-white/5 flex items-center justify-between px-8 sticky top-0 z-50">
          <div className="flex items-center gap-4">
            <button className="md:hidden p-2 text-slate-400 hover:text-white">
              <Menu size={24} />
            </button>
            <div>
              <h2 className="text-sm font-bold text-white tracking-wide uppercase">
                System Interface
              </h2>
              
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex flex-col items-end mr-4">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Operator Email</span>
              <span className="text-xs text-indigo-400">{user?.email}</span>
            </div>
            
            
          </div>
        </header>

        
        <main className="flex-1 overflow-auto bg-[#0a0c10]">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="p-8"
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  );
}