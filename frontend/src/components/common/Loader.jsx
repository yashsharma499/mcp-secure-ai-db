import { motion } from "framer-motion";
import { ShieldCheck } from "lucide-react";

export default function Loader({ label = "Initializing Secure Session..." }) {
  return (
    <div className="flex flex-col items-center justify-center gap-6 p-12">
      <div className="relative flex items-center justify-center">
        {/* outer pulsing ring */}
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.1, 0.3],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute w-16 h-16 bg-indigo-500 rounded-full blur-xl"
        />

        {/* spinning border */}
        <motion.div
          animate={{ rotate: 360 }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "linear",
          }}
          className="w-12 h-12 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full"
        />

        {/* center icon */}
        <div className="absolute">
          <motion.div
            animate={{
              opacity: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          >
            <ShieldCheck className="w-5 h-5 text-indigo-400" />
          </motion.div>
        </div>
      </div>

      {/* label with scanning effect */}
      <div className="flex flex-col items-center gap-2">
        <motion.span 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-[10px] font-bold uppercase tracking-[0.3em] text-indigo-400/80 ml-1"
        >
          System Loading
        </motion.span>
        
        <div className="relative">
          <span className="text-sm font-medium text-slate-400">
            {label}
          </span>
          
          <motion.div
            animate={{ x: ["-100%", "100%"] }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="absolute inset-0 bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent w-full h-full"
          />
        </div>
      </div>
    </div>
  );
}