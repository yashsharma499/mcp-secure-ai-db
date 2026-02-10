import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  Search,
  User,
  Calendar,
  Database,
  AlertCircle,
  RefreshCw,
  Filter
} from "lucide-react";
import { fetchUsers, fetchAuditLogs } from "../../api/admin.api";

export default function AuditLogs() {
  const [users, setUsers] = useState([]);
  const [filters, setFilters] = useState({ userId: "", tableName: "" });

  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [limit] = useState(50);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const data = await fetchUsers();
        setUsers(Array.isArray(data) ? data : []);
      } catch {
        setUsers([]);
      }
    };
    loadUsers();
  }, []);

  const loadLogs = useCallback(
    async (nextOffset = 0, append = false) => {
      setLoading(true);
      setError("");

      try {
        const data = await fetchAuditLogs({
          userId: filters.userId ? Number(filters.userId) : undefined,
          tableName: filters.tableName?.trim() || undefined,
          limit,
          offset: nextOffset
        });

        const rows = Array.isArray(data) ? data : data?.items || [];

        setLogs((prev) => (append ? [...prev, ...rows] : rows));
        setHasMore(rows.length === limit);
        setOffset(nextOffset);
      } catch (err) {
        setError(
          err?.response?.data?.message ||
            "Protocol error: Failed to fetch event streams"
        );
      } finally {
        setLoading(false);
      }
    },
    [filters.userId, filters.tableName, limit]
  );

  // Reset paging and refetch when filters change
  useEffect(() => {
    setOffset(0);
    setHasMore(false);
    loadLogs(0, false);
  }, [filters.userId, filters.tableName, loadLogs]);

  const onLoadMore = () => {
    if (loading || !hasMore) return;
    loadLogs(offset + limit, true);
  };

  return (
    <div className="min-h-screen bg-[#0a0c10] text-slate-200 p-4 md:p-8 space-y-8 font-sans">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Activity className="text-indigo-500 w-6 h-6 animate-pulse" />
            System Audit Stream
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time telemetry of AI agent database transactions
          </p>
        </div>
      </div>

      <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-5 shadow-2xl">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px] space-y-2">
            <label className="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2">
              <User size={12} /> Filter Operator
            </label>
            <select
              value={filters.userId}
              onChange={(e) =>
                setFilters((s) => ({ ...s, userId: e.target.value }))
              }
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 transition-all outline-none"
            >
              <option value="">All Identities</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.email}
                </option>
              ))}
            </select>
          </div>

          <div className="flex-1 min-w-[200px] space-y-2">
            <label className="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2">
              <Database size={12} /> Target Resource
            </label>
            <div className="relative">
              <input
                value={filters.tableName}
                onChange={(e) =>
                  setFilters((s) => ({ ...s, tableName: e.target.value }))
                }
                placeholder="Search table e.g. 'interviews'"
                className="w-full bg-black/40 border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm focus:ring-2 focus:ring-indigo-500 outline-none transition-all"
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            </div>
          </div>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => loadLogs(0, false)}
            disabled={loading}
            className="h-[42px] px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-bold flex items-center gap-2 shadow-lg shadow-indigo-600/20 disabled:opacity-50"
          >
            {loading ? (
              <RefreshCw className="animate-spin w-4 h-4" />
            ) : (
              <Filter size={16} />
            )}
            Filter Stream
          </motion.button>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-xs flex items-center gap-2">
            <AlertCircle size={14} /> {error}
          </div>
        )}
      </div>

      <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-black/40 text-[10px] uppercase tracking-widest text-slate-500 font-bold">
                <th className="px-6 py-4 flex items-center gap-2">
                  <Calendar size={12} /> Timestamp
                </th>
                <th className="px-6 py-4">Operator Identity</th>
                <th className="px-6 py-4">Resource Scope</th>
                <th className="px-6 py-4 text-center">Status Protocol</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-white/5 text-sm">
              <AnimatePresence>
                {logs.map((l, idx) => (
                  <motion.tr
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    key={l.id ?? `${l.created_at}-${idx}`}
                    className="hover:bg-white/[0.02] transition-colors border-l-2 border-transparent hover:border-indigo-500"
                  >
                    <td className="px-6 py-4 font-mono text-xs text-slate-400 whitespace-nowrap">
                      {new Date(
                        l.created_at || l.timestamp
                      ).toLocaleString()}
                    </td>

                    <td className="px-6 py-4 font-medium text-slate-200">
                      {l.user_email || l.user_id}
                    </td>

                    <td className="px-6 py-4 text-slate-400 italic">
                      {l.table_name || "Global Scope"}
                    </td>

                    <td className="px-6 py-4 text-center">
                      <StatusBadge
                        failed={
                          l.success === false || l.status === "failed"
                        }
                      />
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>

              {loading && logs.length === 0 && (
                <tr>
                  <td
                    colSpan={4}
                    className="px-6 py-20 text-center text-slate-500 animate-pulse"
                  >
                    Intercepting System Telemetry...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {hasMore && (
          <div className="p-4 bg-black/20 flex justify-center border-t border-white/5">
            <button
              onClick={onLoadMore}
              disabled={loading}
              className="text-xs font-bold uppercase tracking-widest text-indigo-400 hover:text-indigo-300 flex items-center gap-2 py-2 transition-all"
            >
              {loading ? (
                <RefreshCw className="animate-spin w-4 h-4" />
              ) : (
                "Request More Data Packets"
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function StatusBadge({ failed }) {
  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase border tracking-tighter shadow-sm ${
        failed
          ? "bg-red-500/10 text-red-400 border-red-500/20"
          : "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          failed ? "bg-red-400 animate-pulse" : "bg-emerald-400"
        }`}
      />
      {failed ? "Rejected" : "Authorized"}
    </div>
  );
}
