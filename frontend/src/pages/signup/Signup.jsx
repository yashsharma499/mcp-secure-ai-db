import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
  UserPlus,
  ShieldCheck,
  Loader2,
  CheckCircle2,
  Circle,
  Database,
  Server
} from "lucide-react";
import { signup } from "../../api/auth.api";

const passwordRules = {
  min: 8,
  upper: /[A-Z]/,
  lower: /[a-z]/,
  digit: /[0-9]/
};

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
    className="absolute w-1 h-1 bg-indigo-400 rounded-full blur-[1px]"
    style={{
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`
    }}
  />
);

export default function Signup() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
    confirmPassword: ""
  });

  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const e = {};
    const email = form.email.trim();
    const password = form.password;

    if (!email) e.email = "Email is required";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) e.email = "Invalid format";

    if (!password) e.password = "Password is required";
    else if (password.length < passwordRules.min) e.password = "Minimum 8 characters";
    else if (!passwordRules.upper.test(password)) e.password = "Include an uppercase letter";
    else if (!passwordRules.digit.test(password)) e.password = "Include at least one digit";

    if (form.confirmPassword !== password) e.confirmPassword = "Passwords do not match";

    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleChange = (ev) => {
    const { name, value } = ev.target;
    setForm((s) => ({ ...s, [name]: value }));
    setErrors((s) => ({ ...s, [name]: undefined }));
  };

  const handleSubmit = async (ev) => {
    ev.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setServerError("");

    try {
      await signup({ email: form.email.trim(), password: form.password });
      navigate("/login", { replace: true });
    } catch (err) {
      setServerError(err?.response?.data?.message || "Registration protocol failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex flex-col lg:flex-row bg-[#0a0c10] font-sans overflow-hidden">
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
          className="relative z-10 w-full max-w-[480px]"
        >
          <div className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-3xl p-6 sm:p-8 shadow-[0_0_50px_-12px_rgba(0,0,0,0.5)]">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-blue-500 mb-4 shadow-lg">
                <UserPlus className="text-white w-7 h-7" />
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight">
                Register Operator
              </h1>
              <p className="text-slate-400 text-sm mt-2">
                Initialize your MCP secure credentials
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5" noValidate>
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-[0.1em] ml-1">
                  Work Email
                </label>
                <div className="relative group">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-indigo-400" />
                  <input
                    name="email"
                    type="email"
                    value={form.email}
                    onChange={handleChange}
                    className={`w-full bg-black/40 border ${
                      errors.email ? "border-red-500/50" : "border-white/10"
                    } rounded-xl pl-10 pr-4 py-3 text-white transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500/50`}
                    placeholder="operator@secure-mcp.ai"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-[0.1em] ml-1">
                  Encryption Passkey
                </label>
                <div className="relative group">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 group-focus-within:text-indigo-400" />
                  <input
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={form.password}
                    onChange={handleChange}
                    className={`w-full bg-black/40 border ${
                      errors.password ? "border-red-500/50" : "border-white/10"
                    } rounded-xl pl-10 pr-12 py-3 text-white transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500/50`}
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-500 hover:text-white transition-colors"
                  >
                    {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-2 mt-3 px-1">
                  <Requirement met={form.password.length >= 8} text="8+ Characters" />
                  <Requirement
                    met={passwordRules.upper.test(form.password)}
                    text="Uppercase"
                  />
                  <Requirement
                    met={passwordRules.digit.test(form.password)}
                    text="One Digit"
                  />
                  <Requirement
                    met={
                      form.confirmPassword === form.password &&
                      form.confirmPassword !== ""
                    }
                    text="Matches"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-[0.1em] ml-1">
                  Confirm Identity
                </label>
                <div className="relative group">
                  <ShieldCheck className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    name="confirmPassword"
                    type="password"
                    value={form.confirmPassword}
                    onChange={handleChange}
                    className={`w-full bg-black/40 border ${
                      errors.confirmPassword
                        ? "border-red-500/50"
                        : "border-white/10"
                    } rounded-xl pl-10 pr-4 py-3 text-white transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500/50`}
                    placeholder="Repeat passkey"
                  />
                </div>
              </div>

              <AnimatePresence>
                {(serverError ||
                  errors.email ||
                  errors.password ||
                  errors.confirmPassword) && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-xs text-center"
                  >
                    {serverError ||
                      errors.email ||
                      errors.password ||
                      errors.confirmPassword}
                  </motion.div>
                )}
              </AnimatePresence>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                disabled={loading}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3.5 rounded-xl shadow-xl shadow-indigo-600/20 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <span>Create Account</span>
                )}
              </motion.button>

              <div className="text-center pt-4 border-t border-white/5">
                <p className="text-slate-500 text-sm">
                  Already registered?{" "}
                  <Link
                    to="/login"
                    className="text-indigo-400 font-semibold hover:text-indigo-300 transition-colors"
                  >
                    Authorize Here
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

function Requirement({ met, text }) {
  return (
    <div
      className={`flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider transition-colors ${
        met ? "text-emerald-400" : "text-slate-600"
      }`}
    >
      {met ? <CheckCircle2 size={12} /> : <Circle size={12} />}
      {text}
    </div>
  );
}
