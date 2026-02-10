import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

export default function Button({
  type = "button",
  disabled,
  loading, 
  children,
  onClick,
  variant = "primary", 
  className = "",
  icon: Icon, 
}) {
  
  
  const variants = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-500 shadow-lg shadow-indigo-600/20 border-transparent",
    secondary: "bg-white/5 text-slate-200 border-white/10 hover:bg-white/10 backdrop-blur-md",
    ghost: "bg-transparent text-slate-400 hover:text-white hover:bg-white/5 border-transparent",
    danger: "bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20",
    outline: "bg-transparent border-slate-700 text-slate-300 hover:border-indigo-500 hover:text-indigo-400"
  };

  return (
    <motion.button
      whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || loading ? 1 : 0.97 }}
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`
        relative inline-flex items-center justify-center gap-2 
        rounded-xl px-5 py-2.5 text-sm font-bold 
        transition-all duration-200 border
        focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:ring-offset-2 focus:ring-offset-[#0a0c10]
        disabled:opacity-40 disabled:cursor-not-allowed
        ${variants[variant]} 
        ${className}
      `}
    >
      
      {loading && (
        <Loader2 className="w-4 h-4 animate-spin text-current" />
      )}

      
      {!loading && Icon && (
        <Icon className="w-4 h-4" />
      )}

      
      <span className={loading ? "opacity-0" : "opacity-100"}>
        {children}
      </span>

      
      {loading && (
        <span className="absolute inset-0 flex items-center justify-center text-[10px] uppercase tracking-widest">
          Processing
        </span>
      )}
    </motion.button>
  );
}