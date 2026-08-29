import React from "react";

export function LeadStatusBadge({ status }) {
  const code = status?.code || status || "";
  const name = status?.name || status || "";

  let classes = "bg-slate-100 text-slate-700 border-slate-200";

  switch (code.toUpperCase()) {
    case "NEW":
      classes = "bg-slate-100 text-slate-700 border-slate-200";
      break;
    case "ASSIGNED":
      classes = "bg-slate-100 text-slate-800 border-slate-200";
      break;
    case "CONTACTED":
      classes = "bg-sky-50 text-sky-700 border-sky-100";
      break;
    case "REQUIREMENT_GATHERING":
      classes = "bg-amber-50 text-amber-700 border-amber-100";
      break;
    case "PROPOSAL_SENT":
      classes = "bg-purple-50 text-purple-700 border-purple-100";
      break;
    case "NEGOTIATION":
      classes = "bg-blue-50 text-blue-700 border-blue-100";
      break;
    case "WON":
      classes = "bg-emerald-50 text-emerald-700 border-emerald-100";
      break;
    case "LOST":
      classes = "bg-red-50 text-red-700 border-red-100";
      break;
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${classes}`}>
      {name}
    </span>
  );
}

export function LeadPriorityBadge({ priority }) {
  const code = priority?.code || priority || "";
  const name = priority?.name || priority || "";

  let classes = "bg-slate-100 text-slate-700";

  switch (code.toUpperCase()) {
    case "HIGH":
      classes = "bg-rose-50 text-rose-700 border-rose-100";
      break;
    case "MEDIUM":
      classes = "bg-amber-50 text-amber-700 border-amber-100";
      break;
    case "LOW":
      classes = "bg-slate-100 text-slate-600 border-slate-200";
      break;
  }

  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold border ${classes}`}>
      {name}
    </span>
  );
}

export default LeadStatusBadge;
