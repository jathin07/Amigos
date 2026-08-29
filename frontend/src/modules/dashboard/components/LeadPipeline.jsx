import React from "react";
import { useLeadPipeline } from "../hooks/useDashboard";
import WidgetCard from "../widgets/WidgetCard";
import { Link } from "react-router-dom";

export function LeadPipeline() {
  const { data, isLoading, error, refetch } = useLeadPipeline();

  const funnelItems = data?.data || [];

  return (
    <WidgetCard
      title="CRM Lead Funnel"
      description="Conversion rate across lead lifecycle stages"
      onRefresh={refetch}
      isRefreshing={isLoading}
      error={error}
    >
      <div className="flex-1 flex flex-col justify-between py-2 space-y-4">
        {funnelItems.length === 0 ? (
          <div className="text-center py-10 text-slate-400 text-xs">No active lead data available.</div>
        ) : (
          <div className="space-y-3.5">
            {funnelItems.map((item, idx) => {
              const percentage = item.percentage || 0;
              return (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between items-center text-xs font-semibold text-slate-700">
                    <Link
                      to={`/admin/dashboard`} // Keep redirect generic
                      className="hover:text-blue-600 uppercase transition-colors"
                    >
                      {item.status}
                    </Link>
                    <div className="flex items-center space-x-2 text-slate-500">
                      <span>{item.count} leads</span>
                      <span className="text-[10px] bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">
                        {percentage.toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  {/* Progress Bar */}
                  <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.min(100, Math.max(2, percentage))}%`,
                        backgroundColor: item.color || "#2563EB",
                      }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div className="border-t border-slate-50 pt-3 flex justify-between items-center text-xs text-slate-400">
          <span>Target Funnel Conversion</span>
          <span className="font-semibold text-slate-700">
            {funnelItems.length > 0
              ? `${(
                  (funnelItems.find((f) => f.status.toLowerCase() === "won")?.count || 0) /
                  (funnelItems.reduce((acc, curr) => acc + curr.count, 0) || 1) *
                  100
                ).toFixed(1)}%`
              : "0%"}
          </span>
        </div>
      </div>
    </WidgetCard>
  );
}
export default LeadPipeline;
