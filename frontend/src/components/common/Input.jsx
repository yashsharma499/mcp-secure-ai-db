import { forwardRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle } from "lucide-react";

const Input = forwardRef(function Input(
  {
    label,
    type = "text",
    className = "",
    error,
    icon: Icon,
    ...props
  },
  ref
) {
  return (
    <div className="w-full space-y-1.5 group/container">
      {/* Label - Technical "Operator" styling */}
      {label && (
        <label className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] ml-1 group-focus-within/container:text-indigo-400 transition-colors duration-300">
          {label}
        </label>
      )}

      <div className="relative">
        {/* Leading Icon with interactive color state */}
        {Icon && (
          <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within/container:text-indigo-400 transition-colors duration-300 z-10">
            <Icon size={16} strokeWidth={2.5} />
          </div>
        )}

        {/* Input Field with Glassmorphism and Focus Aura */}
        <input
          ref={ref}
          type={type}
          {...props}
          className={`
            w-full bg-black/40 text-slate-200 text-sm rounded-xl py-3 px-4
            border transition-all duration-300 outline-none
            placeholder:text-slate-700
            ${Icon ? "pl-11" : "pl-4"}
            ${
              error 
                ? "border-red-500/50 bg-red-500/5 focus:ring-2 focus:ring-red-500/20" 
                : "border-white/10 focus:border-indigo-500/50 focus:ring-[4px] focus:ring-indigo-500/10 focus:bg-black/60 shadow-inner"
            } 
            ${className}
          `}
        />

        
        <div className="absolute inset-0 rounded-xl border border-white/5 pointer-events-none group-focus-within/container:border-indigo-500/20 transition-colors duration-300" />
      </div>

      
      <div className="h-5 overflow-hidden"> 
        <AnimatePresence mode="wait">
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="flex items-center gap-1.5 px-1.5 text-red-400"
            >
              <AlertCircle size={12} strokeWidth={2.5} />
              <p className="text-[11px] font-semibold tracking-wide">
                {error}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
});

export default Input;