import React from "react";

export function BookingStatusBadge({ status }) {
  const code = (status?.code || (typeof status === "string" ? status : "") || "").toUpperCase();
  const name = status?.name || (code ? code.replace(/_/g, " ").toLowerCase().replace(/\b\w/g, (l) => l.toUpperCase()) : "Waiting for Advance");

  let styles = "bg-amber-50 text-amber-700 border-amber-200";

  switch (code) {
    case "WAITING_FOR_ADVANCE":
      styles = "bg-amber-50 text-amber-700 border-amber-200";
      break;
    case "CONFIRMED":
      styles = "bg-emerald-50 text-emerald-700 border-emerald-200";
      break;
    case "PLANNING":
      styles = "bg-blue-50 text-blue-700 border-blue-200";
      break;
    case "READY":
      styles = "bg-indigo-50 text-indigo-700 border-indigo-200";
      break;
    case "ONGOING":
      styles = "bg-teal-50 text-teal-700 border-teal-200";
      break;
    case "COMPLETED":
      styles = "bg-purple-50 text-purple-700 border-purple-200";
      break;
    case "CLOSED":
      styles = "bg-slate-100 text-slate-700 border-slate-200";
      break;
    case "CANCELLED":
      styles = "bg-rose-50 text-rose-700 border-rose-200";
      break;
    default:
      if (code.includes("CONFIRM")) {
        styles = "bg-emerald-50 text-emerald-700 border-emerald-200";
      } else if (code.includes("CANCEL")) {
        styles = "bg-rose-50 text-rose-700 border-rose-200";
      }
      break;
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-bold border select-none ${styles}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current mr-1.5" />
      {name}
    </span>
  );
}

export default BookingStatusBadge;
