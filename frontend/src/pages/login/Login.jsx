import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Eye, EyeOff, Lock, Mail, ShieldCheck, Loader2, ArrowRight, Database, Server } from "lucide-react";
import useAuth from "../../auth/useAuth";

const BackgroundParticle = ({ delay = 0, duration = 20 }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0 }}
    animate={{
      opacity: [0.1, 0.4, 0.1],
      scale: [1, 1.5, 1],
      x: [0, Math.random() * 80 - 40, 0],
      y: [0, Math.random() * 80 - 40, 0]
    }}
    transition={{ duration, repeat: Infinity, delay, ease: "linear" }}
    className="absolute w-1 h-1 bg-blue-400 rounded-full blur-[1px]"
    style={{
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`
    }}
  />
);

export default function Login() {
  const { login, user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [serverError, setServerError] = useState("");

  useEffect(() => {
    if (isAuthenticated && user?.role) {
      navigate(user.role === "admin" ? "/admin" : "/app", { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  const validate = () => {
    const e = {};
    if (!form.email.trim()) e.email = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) e.email = "Invalid format";
    if (!form.password) e.password = "Password is required";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleChange = (ev) => {
    setForm((s) => ({ ...s, [ev.target.name]: ev.target.value }));
    if (errors[ev.target.name]) setErrors((s) => ({ ...s, [ev.target.name]: undefined }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setServerError("");
    try {
      const res = await login(form);
      navigate(res.role === "admin" ? "/admin" : "/app", { replace: true });
    } catch (err) {
      setServerError(err?.response?.data?.message || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-[#0a0c10] font-sans">
      <div className="flex w-full lg:w-1/2 relative p-4 sm:p-6 h-[45vh] lg:h-auto">
        <div className="relative w-full h-full rounded-3xl overflow-hidden shadow-2xl bg-[#0f172a]">
          <img
            src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop"
            alt="Data Network"
            className="absolute inset-0 w-full h-full object-cover opacity-60"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0a0c10] via-transparent to-[#0a0c10]/40" />

          <div className="absolute bottom-6 sm:bottom-10 lg:bottom-20 left-0 right-0 px-6 sm:px-10 xl:px-16">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="flex items-center gap-3 mb-4 sm:mb-6">
                <div className="p-3 bg-indigo-600/20 border border-indigo-500/30 rounded-2xl backdrop-blur-md">
                  <Server className="text-indigo-400 w-7 h-7 sm:w-8 sm:h-8" />
                </div>
                <div className="h-[2px] w-10 sm:w-12 bg-indigo-500/50" />
                <Database className="text-indigo-400 w-7 h-7 sm:w-8 sm:h-8" />
              </div>

              <h2 className="text-2xl sm:text-3xl xl:text-5xl font-bold text-white mb-4 sm:mb-6 leading-tight">
                MCP-Based <br />
                <span className="text-indigo-500">Secure AI</span> Database Access Platform
              </h2>

              <div className="space-y-3 sm:space-y-4">
                <p className="text-slate-300 text-sm sm:text-base lg:text-lg max-w-md leading-relaxed">
                  The centralized secure gateway protocol for users and AI agents.
                </p>
                <div className="flex items-center gap-2 text-indigo-400/80 text-xs sm:text-sm font-mono">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  Gateway Status: Protected
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      <div className="w-full lg:w-1/2 relative flex items-center justify-center px-4 sm:px-6 py-10 lg:py-0 overflow-hidden">
        <div className="absolute inset-0 bg-[#0a0c10]">
          <motion.div
            animate={{ scale: [1, 1.15, 1], opacity: [0.2, 0.4, 0.2] }}
            transition={{ duration: 12, repeat: Infinity }}
            className="absolute -bottom-[10%] -right-[10%] w-[70%] h-[70%] bg-indigo-900/20 blur-[120px] rounded-full"
          />
          {[...Array(15)].map((_, i) => (
            <BackgroundParticle key={i} delay={i * 0.5} />
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10 w-full max-w-[440px]"
        >
          <div className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-2xl p-6 sm:p-8 shadow-[0_0_50px_-12px_rgba(0,0,0,0.5)]">
            <div className="flex flex-col items-center mb-8">
              <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center mb-4 shadow-lg shadow-indigo-500/20">
                <ShieldCheck className="text-white w-7 h-7" />
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight">MCP Secure Access</h1>
              <p className="text-slate-400 text-sm mt-2">Centralized AI Gateway Protocol</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider ml-1">
                  Identity (Email)
                </label>
                <div className="relative group">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
                  <input
                    type="email"
                    name="email"
                    value={form.email}
                    onChange={handleChange}
                    placeholder="operator@mcp-node.ai"
                    className={`w-full bg-black/40 border ${
                      errors.email ? "border-red-500/50" : "border-white/10"
                    } rounded-lg pl-10 pr-4 py-3 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 transition-all`}
                  />
                </div>
                {errors.email && <p className="text-[11px] text-red-400 ml-1">{errors.email}</p>}
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider ml-1">
                  Passkey
                </label>
                <div className="relative group">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={form.password}
                    onChange={handleChange}
                    placeholder="••••••••"
                    className={`w-full bg-black/40 border ${
                      errors.password ? "border-red-500/50" : "border-white/10"
                    } rounded-lg pl-10 pr-12 py-3 text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 transition-all`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-500 hover:text-white transition-colors"
                  >
                    {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
                  </button>
                </div>
                {errors.password && <p className="text-[11px] text-red-400 ml-1">{errors.password}</p>}
              </div>

              <AnimatePresence>
                {serverError && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-xs text-center"
                  >
                    {serverError}
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                disabled={loading}
                className="w-full relative overflow-hidden group bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-lg transition-all flex items-center justify-center gap-2 shadow-xl shadow-indigo-600/20 disabled:opacity-70"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <span>Initialize Session</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </motion.button>

              <div className="text-center pt-2">
                <p className="text-slate-500 text-sm">
                  New Operator?{" "}
                  <Link
                    to="/signup"
                    className="text-indigo-400 font-medium hover:underline decoration-indigo-400/30 underline-offset-4"
                  >
                    Request Access
                  </Link>
                </p>
              </div>
            </form>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
