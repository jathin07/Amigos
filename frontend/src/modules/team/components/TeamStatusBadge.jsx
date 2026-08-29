import React from "react";

export function TeamStatusBadge({ isActive, employmentStatus }) {
  if (isActive === false) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-100 select-none">
        Inactive
      </span>
    );
  }

  const status = employmentStatus || "FULL_TIME";
  let classes = "bg-emerald-50 text-emerald-700 border-emerald-100";

  if (status.toUpperCase().includes("PROBATION")) {
    classes = "bg-amber-50 text-amber-700 border-amber-100";
  } else if (status.toUpperCase().includes("CONTRACT")) {
    classes = "bg-sky-50 text-sky-700 border-sky-100";
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border select-none ${classes}`}>
      Active
    </span>
  );
}

export default TeamStatusBadge;
