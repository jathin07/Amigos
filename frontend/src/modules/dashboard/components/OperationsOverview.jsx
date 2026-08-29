import React from "react";
import { useOperationsOverview } from "../hooks/useDashboard";
import WidgetCard from "../widgets/WidgetCard";
import { UserCheck, CheckSquare, ShieldCheck, AlertCircle } from "lucide-react";

export function OperationsOverview() {
  const { data, isLoading, error, refetch } = useOperationsOverview();

  const coordinators = data?.data || [];

  return (
    <WidgetCard
      title="Trip Coordinator Workloads"
      description="Active tours, checklist items, and vendor statuses per staff member"
      onRefresh={refetch}
      isRefreshing={isLoading}
      error={error}
    >
      <div className="flex-1 flex flex-col justify-between py-1 space-y-4">
        {coordinators.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-xs">No active operation coordinator metrics.</div>
        ) : (
          <div className="space-y-4">
            {coordinators.map((coord, idx) => {
              return (
                <div key={idx} className="border border-slate-100 rounded-xl p-3.5 space-y-3">
                  {/* Coordinator Header */}
                  <div className="flex items-center justify-between border-b border-slate-50 pb-1.5">
                    <div className="flex items-center space-x-2 text-xs font-semibold text-slate-800">
                      <UserCheck size={14} className="text-blue-500" />
                      <span>{coord.coordinator}</span>
                    </div>
                    <span className="text-[10px] font-bold bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                      {coord.trips_assigned} trips active
                    </span>
                  </div>

                  {/* Workload breakdown grid */}
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div className="p-2 bg-slate-50 rounded-lg space-y-0.5">
                      <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wide block">Tasks</span>
                      <span className="text-sm font-bold text-slate-700">{coord.open_tasks}</span>
                    </div>

                    <div className="p-2 bg-slate-50 rounded-lg space-y-0.5">
                      <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wide block">Checklist</span>
                      <span className="text-sm font-bold text-slate-700">{coord.pending_checklist}</span>
                    </div>

                    <div className="p-2 bg-slate-50 rounded-lg space-y-0.5">
                      <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wide block">Vendors</span>
                      <span className="text-sm font-bold text-slate-700 flex justify-center items-center">
                        {coord.pending_vendors > 0 ? (
                          <>
                            <AlertCircle size={12} className="text-amber-500 mr-1 shrink-0" />
                            <span className="text-amber-600">{coord.pending_vendors}</span>
                          </>
                        ) : (
                          <>
                            <ShieldCheck size={12} className="text-emerald-500 mr-1 shrink-0" />
                            <span className="text-emerald-600">0</span>
                          </>
                        )}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </WidgetCard>
  );
}
export default OperationsOverview;
