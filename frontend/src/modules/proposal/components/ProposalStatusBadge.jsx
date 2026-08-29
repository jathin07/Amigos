import React from "react";

export function ProposalStatusBadge({ status }) {
  const code = status?.code || status || "";
  const name = status?.name || status || "";

  let classes = "bg-slate-100 text-slate-700 border-slate-200";

  switch (code.toUpperCase()) {
    case "DRAFT":
      classes = "bg-slate-100 text-slate-700 border-slate-200";
      break;
    case "UNDER_DISCUSSION":
    case "SENT":
      classes = "bg-sky-50 text-sky-700 border-sky-100";
      break;
    case "REVISED":
      classes = "bg-purple-50 text-purple-700 border-purple-100";
      break;
    case "APPROVED":
    case "ACCEPTED":
      classes = "bg-emerald-50 text-emerald-700 border-emerald-100";
      break;
    case "WAITING_FOR_ADVANCE":
      classes = "bg-amber-50 text-amber-700 border-amber-100";
      break;
    case "CONVERTED":
      classes = "bg-teal-50 text-teal-700 border-teal-100";
      break;
    case "REJECTED":
    case "ARCHIVED":
    case "EXPIRED":
      classes = "bg-red-50 text-red-700 border-red-100";
      break;
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border ${classes}`}>
      {name}
    </span>
  );
}

export default ProposalStatusBadge;
