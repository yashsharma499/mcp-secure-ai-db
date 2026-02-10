import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldAlert,
  UserCheck,
  Database,
  Trash2,
  Save,
  ChevronRight,
  Lock,
  Unlock,
  Loader2,
  Table as TableIcon,
  Columns
} from "lucide-react";
import {
  fetchUsers,
  fetchUserPermissions,
  upsertUserPermission,
  deleteUserPermission
} from "../../api/admin.api";
import useAuth from "../../auth/useAuth";

const TABLE_SCHEMA = {
  candidates: ["id", "full_name", "email", "phone", "city"],
  interviewers: ["id", "full_name", "email", "department"],
  interviews: ["id", "candidate_id", "interviewer_id", "scheduled_at", "status"]
};

const emptyForm = {
  tableName: "",
  canRead: false,
  canWrite: false,
  allowedColumns: []
};

export default function UsersPermissions() {
  const { user } = useAuth();
  const storageKey = user?.id
    ? `mcp_admin_permissions_ui_${user.id}`
    : null;

  const [users, setUsers] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [permissions, setPermissions] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [loadingPermissions, setLoadingPermissions] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!storageKey) return;

    const saved = localStorage.getItem(storageKey);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.selectedUserId) setSelectedUserId(parsed.selectedUserId);
        if (parsed.form) setForm(parsed.form);
      } catch {}
    }
  }, [storageKey]);

  useEffect(() => {
    if (!storageKey) return;
    localStorage.setItem(
      storageKey,
      JSON.stringify({ selectedUserId, form })
    );
  }, [selectedUserId, form, storageKey]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchUsers();
        setUsers(data || []);
      } catch {
        setError("Failed to load users");
      } finally {
        setLoadingUsers(false);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (!selectedUserId) {
      setPermissions([]);
      return;
    }

    const loadPermissions = async () => {
      setLoadingPermissions(true);
      setError("");
      try {
        const data = await fetchUserPermissions(selectedUserId);
        setPermissions(data || []);
      } catch {
        setError("Failed to load permissions");
      } finally {
        setLoadingPermissions(false);
      }
    };

    loadPermissions();
  }, [selectedUserId]);

  const availableColumns = useMemo(
    () => TABLE_SCHEMA[form.tableName] || [],
    [form.tableName]
  );

  const validationError = useMemo(() => {
    if (!selectedUserId) return "Select user context";
    if (!form.tableName) return "Target table required";
    if (!form.canRead && !form.canWrite) return "Assign at least one privilege";
    if (form.canRead && !form.allowedColumns.length)
      return "Select readable columns";
    return "";
  }, [selectedUserId, form]);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (validationError) return;

    setSaving(true);

    try {
      await upsertUserPermission({
        userId: Number(selectedUserId),
        tableName: form.tableName,
        canRead: form.canRead,
        canWrite: form.canWrite,
        allowedColumns: form.canRead ? form.allowedColumns : []
      });

      const data = await fetchUserPermissions(selectedUserId);
      setPermissions(data || []);
      setForm(emptyForm);
    } catch (err) {
      setError(err?.response?.data?.message || "Permission upsert failed");
    } finally {
      setSaving(false);
    }
  };

  const onDelete = async (id) => {
    try {
      await deleteUserPermission(id);
      const data = await fetchUserPermissions(selectedUserId);
      setPermissions(data || []);
    } catch {
      setError("Delete protocol failed");
    }
  };

  const toggleColumn = (col) => {
    setForm((s) => ({
      ...s,
      allowedColumns: s.allowedColumns.includes(col)
        ? s.allowedColumns.filter((c) => c !== col)
        : [...s.allowedColumns, col]
    }));
  };

  return (
    <div className="min-h-screen bg-[#0a0c10] text-slate-200 p-4 md:p-8 space-y-8 font-sans">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Lock className="text-indigo-500 w-6 h-6" />
            Access Control Matrix
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Deploy fine-grained database permissions for AI agents & users.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-white/5 p-1 rounded-xl border border-white/10">
          <label className="text-xs font-bold text-slate-500 uppercase px-3">
            Active Context:
          </label>
          <select
            value={selectedUserId}
            onChange={(e) => setSelectedUserId(e.target.value)}
            className="bg-black/40 text-sm border-none rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 transition-all cursor-pointer min-w-[200px]"
            disabled={loadingUsers}
          >
            <option value="">Select an Operator</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.email}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-5 space-y-6"
        >
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-xl">
            <h2 className="text-sm font-bold uppercase tracking-widest text-indigo-400 mb-6 flex items-center gap-2">
              <Database size={16} /> New Rule Deployment
            </h2>

            <form onSubmit={onSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-400 ml-1">
                  Target Resource (Table)
                </label>
                <select
                  value={form.tableName}
                  onChange={(e) =>
                    setForm((s) => ({
                      ...s,
                      tableName: e.target.value,
                      allowedColumns: []
                    }))
                  }
                  className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Select table...</option>
                  {Object.keys(TABLE_SCHEMA).map((t) => (
                    <option key={t} value={t}>
                      {t.toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <PermissionToggle
                  label="Read Access"
                  active={form.canRead}
                  onClick={() =>
                    setForm((s) => ({ ...s, canRead: !s.canRead }))
                  }
                />
                <PermissionToggle
                  label="Write Access"
                  active={form.canWrite}
                  onClick={() =>
                    setForm((s) => ({ ...s, canWrite: !s.canWrite }))
                  }
                />
              </div>

              <div className="space-y-3">
                <label className="text-xs font-semibold text-slate-400 ml-1 flex items-center gap-2">
                  <Columns size={14} /> Column Visibility Control
                </label>
                <div className="flex flex-wrap gap-2 p-3 bg-black/20 rounded-xl border border-white/5 min-h-[100px]">
                  {form.tableName ? (
                    availableColumns.map((c) => (
                      <button
                        key={c}
                        type="button"
                        disabled={!form.canRead}
                        onClick={() => toggleColumn(c)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all border ${
                          form.allowedColumns.includes(c)
                            ? "bg-indigo-600/20 border-indigo-500 text-indigo-200"
                            : "bg-white/5 border-white/5 text-slate-500"
                        } disabled:opacity-30`}
                      >
                        {c}
                      </button>
                    ))
                  ) : (
                    <p className="text-[10px] text-slate-600 italic m-auto">
                      Select a resource to configure visibility
                    </p>
                  )}
                </div>
              </div>

              <button
                type="submit"
                disabled={!!validationError || saving}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:grayscale py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/20"
              >
                {saving ? (
                  <Loader2 className="animate-spin" size={18} />
                ) : (
                  <Save size={18} />
                )}
                Deploy Permission Rule
              </button>
            </form>

            {error && (
              <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-xs flex items-center gap-2">
                <ShieldAlert size={14} /> {error}
              </div>
            )}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-7"
        >
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl overflow-hidden shadow-xl">
            <div className="px-6 py-4 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
              <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400">
                Deployed Rulesets
              </h2>
              <span className="text-[10px] px-2 py-1 bg-indigo-500/10 text-indigo-400 rounded-md border border-indigo-500/20 font-mono">
                {permissions.length} Active Rules
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-black/20 text-[10px] uppercase tracking-widest text-slate-500 font-bold">
                    <th className="px-6 py-4">Resource</th>
                    <th className="px-6 py-4 text-center">Privileges</th>
                    <th className="px-6 py-4">Scope (Columns)</th>
                    <th className="px-6 py-4"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  <AnimatePresence mode="popLayout">
                    {loadingPermissions ? (
                      <tr>
                        <td
                          colSpan={4}
                          className="px-6 py-12 text-center text-slate-500"
                        >
                          <Loader2 className="animate-spin inline mr-2" /> Synching
                          Access Matrix...
                        </td>
                      </tr>
                    ) : permissions.length === 0 ? (
                      <tr>
                        <td
                          colSpan={4}
                          className="px-6 py-12 text-center text-slate-500 italic"
                        >
                          No active permissions for this operator.
                        </td>
                      </tr>
                    ) : (
                      permissions.map((p) => (
                        <motion.tr
                          layout
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0, scale: 0.95 }}
                          key={p.id}
                          className="hover:bg-white/[0.02] transition-colors group"
                        >
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <TableIcon
                                size={14}
                                className="text-indigo-400"
                              />
                              <span className="font-semibold text-white">
                                {p.table_name}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex justify-center gap-1.5">
                              {p.can_read && <Badge type="read" />}
                              {p.can_write && <Badge type="write" />}
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex flex-wrap gap-1 max-w-[200px]">
                              {(p.allowed_columns || []).map((col) => (
                                <span
                                  key={col}
                                  className="text-[10px] bg-white/5 px-1.5 rounded text-slate-400"
                                >
                                  {col}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="px-6 py-4 text-right">
                            <button
                              onClick={() => onDelete(p.id)}
                              className="p-2 text-slate-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                            >
                              <Trash2 size={16} />
                            </button>
                          </td>
                        </motion.tr>
                      ))
                    )}
                  </AnimatePresence>
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

function PermissionToggle({ label, active, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex items-center justify-between p-3 rounded-xl border transition-all ${
        active
          ? "bg-indigo-600/10 border-indigo-500/50 text-indigo-400"
          : "bg-black/40 border-white/10 text-slate-600"
      }`}
    >
      <span className="text-xs font-bold uppercase">{label}</span>
      {active ? <Unlock size={14} /> : <Lock size={14} />}
    </button>
  );
}

function Badge({ type }) {
  const styles = {
    read: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    write: "bg-blue-500/10 text-blue-500 border-blue-500/20"
  };

  return (
    <span
      className={`text-[9px] font-bold px-1.5 py-0.5 rounded border uppercase ${styles[type]}`}
    >
      {type}
    </span>
  );
}
