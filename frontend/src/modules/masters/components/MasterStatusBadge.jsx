import React from "react";

export function MasterStatusBadge({ isActive }) {
  if (isActive === false) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-500 border border-slate-200 select-none">
        <span className="w-1.5 h-1.5 rounded-full bg-slate-400 mr-1.5" />
        Inactive
      </span>
    );
  }

  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-100 select-none">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5" />
      Active
    </span>
  );
}

export default MasterStatusBadge;
