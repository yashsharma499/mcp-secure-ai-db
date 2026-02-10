import { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, Database, FileJson } from "lucide-react";

export default function ResultTable({ data }) {
  const [expanded, setExpanded] = useState(false);

  const normalized = useMemo(() => {
    if (!data) return { type: "empty", rows: [], columns: [] };

    if (Array.isArray(data)) {
      if (data.length === 0) return { type: "table", rows: [], columns: [] };
      if (typeof data[0] === "object" && data[0] !== null) {
        const columns = Array.from(new Set(data.flatMap((r) => Object.keys(r || {}))));
        return { type: "table", rows: data, columns };
      }
      return { type: "list", rows: data.map((v) => ({ value: v })), columns: ["value"] };
    }

    if (typeof data === "object") {
      return {
        type: "object",
        rows: Object.entries(data).map(([k, v]) => ({ key: k, value: v })),
        columns: ["key", "value"]
      };
    }

    return { type: "value", value: data };
  }, [data]);

  if (normalized.type === "value") {
    return (
      <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-sm text-slate-300 font-mono shadow-inner">
        <span className="text-indigo-400 mr-2">❯</span> {String(normalized.value)}
      </div>
    );
  }

  const rowsToRender = expanded ? normalized.rows : normalized.rows.slice(0, 5);

  return (
    <div className="w-full bg-white/[0.02] border border-white/10 rounded-2xl overflow-hidden backdrop-blur-md shadow-2xl">
      {/* Table Header HUD */}
      <div className="px-4 py-2.5 bg-white/5 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database size={14} className="text-indigo-400" />
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
            Dataset Output
          </span>
        </div>
        <span className="text-[9px] font-mono text-slate-500">
          {normalized.rows.length} ROWS FOUND
        </span>
      </div>

      <div className="overflow-x-auto custom-scrollbar">
        <table className="min-w-full text-xs text-left">
          <thead>
            <tr className="bg-white/[0.03]">
              {normalized.columns.map((c) => (
                <th
                  key={c}
                  className="px-4 py-3 font-bold text-slate-300 uppercase tracking-tighter border-b border-white/5"
                >
                  {c.replace(/_/g, " ")}
                </th>
              ))}
            </tr>
          </thead>

          <tbody className="divide-y divide-white/[0.03]">
            <AnimatePresence>
              {rowsToRender.length === 0 ? (
                <tr>
                  <td
                    colSpan={normalized.columns.length || 1}
                    className="px-6 py-8 text-center text-slate-500 italic"
                  >
                    Zero records returned by agent.
                  </td>
                </tr>
              ) : (
                rowsToRender.map((row, idx) => (
                  <motion.tr
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    key={idx}
                    className="hover:bg-indigo-500/[0.04] transition-colors"
                  >
                    {normalized.columns.map((c) => (
                      <td
                        key={c}
                        className="px-4 py-3 text-slate-400 font-medium whitespace-pre-wrap break-words max-w-xs"
                      >
                        {renderCell(row?.[c])}
                      </td>
                    ))}
                  </motion.tr>
                ))
              )}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {/* Expand/Collapse Trigger */}
      {normalized.rows.length > 5 && (
        <div className="bg-white/[0.02] border-t border-white/5 p-1">
          <button
            onClick={() => setExpanded((s) => !s)}
            className="w-full py-2 flex items-center justify-center gap-2 text-[10px] font-bold uppercase tracking-widest text-indigo-400 hover:text-indigo-300 hover:bg-white/5 transition-all rounded-lg"
          >
            {expanded ? (
              <>
                <ChevronUp size={14} /> Show Less
              </>
            ) : (
              <>
                <ChevronDown size={14} /> Show All ({normalized.rows.length})
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
}

function renderCell(value) {
  if (value === null || value === undefined) return <span className="text-slate-700">NULL</span>;

  if (typeof value === "object") {
    return (
      <div className="flex flex-col gap-1 p-2 bg-black/30 rounded-lg border border-white/5 font-mono text-[10px]">
        <div className="flex items-center gap-1.5 text-indigo-400/70 border-b border-white/5 pb-1 mb-1">
          <FileJson size={10} /> 
          <span className="uppercase tracking-tighter">Object</span>
        </div>
        <pre className="overflow-x-auto text-slate-500">
          {JSON.stringify(value, null, 2)}
        </pre>
      </div>
    );
  }

  // Highlight ID values or special strings
  if (typeof value === "string" && value.match(/^[0-9a-fA-F-]{8,}$/)) {
    return <span className="font-mono text-indigo-300/80">{value.slice(0, 8)}...</span>;
  }

  return String(value);
}